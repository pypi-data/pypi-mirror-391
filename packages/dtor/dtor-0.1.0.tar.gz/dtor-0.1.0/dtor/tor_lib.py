import os
import re
import sys
import time
import json
import socket
import psutil
import shutil
import hashlib
import zipfile
import tarfile
import requests
import platform
import subprocess
import binascii
from pathlib import Path
from typing import Optional, Dict, List, Union, Tuple

class TorHandler:
    """Comprehensive Tor process manager with full lifecycle control"""
    
    def __init__(self, recover=True):
        """Initialize TorHandler with directory paths
        Args:
            binary_dir: Directory for Tor binaries and data
            torrc_template_path: Directory for torrc configuration file
        """
        # Core state
        self.running = False
        self.tor_process_id = 0
        
        # Paths
        self.current_dir = Path(__file__).parent.resolve()
        self.base_dir = 'tor_handler_files'
        self.binary_dir = Path(self.base_dir, "tor_binaries")
        self.cache_directory = Path(self.base_dir, "cache")
        self.data_directory = Path(self.binary_dir, "data")
        self.torrc_template_path = Path(self.base_dir, "config")
        self.torrc_file = Path(self.torrc_template_path, "torrc")
        self.tor_process_file = Path(self.data_directory, "tor_process.pid")
        self.process_registry_file = Path(self.data_directory, "process.json")
        
        # Configuration
        self.socks_port: List[int] = [9050]
        self.control_port: List[int] = [9051]
        self.cookie_authentication = True
        self.hidden_services: List[Dict] = []
        self.tor_version_url = "https://github.com/QudsLab/tor-versions/raw/refs/heads/main/data/json/latest_export_versions.json"
        
        # Runtime temporary configuration
        self.temp_config = {
            'control_port': [],
            'socks_port': [],
            'cookie_authentication': self.cookie_authentication,
            'hidden_services': []
        }
        
        # Port collision settings
        self.socks_port_collision_resolve = False
        self.control_port_collision_resolve = False
        self.hidden_service_port_collision_resolve = False
        self.max_port_resolve_attempts = 100
        
        # Debug settings
        self.debug = False
        self.log_level = 0
        self.log_types = ['debug', 'info', 'notice', 'warning', 'error']
        
        # Detected conflicts
        self.conflicting_ports: Dict[str, List[int]] = {}
        
        # Max-Bounds to prevent overflow
        self.max_socks_ports = 3     # not nessassery this much
        self.max_control_ports = 3   # not nessassery this much
        self.max_hidden_services = 3 # actually 5 is possible but 3 is safer
        
        # Initialize
        self.cleanup_stale_processes()
        if recover:
            self.load_torrc_configuration()
        self.detect_port_conflicts()
    
    # ==================== LOGGING MANAGEMENT ====================
    def logger(self, message: str, level: int = 0, exception: Optional[Exception] = None, func_id: str = "", error_code: str = ""):
        """Structured logging function with consistent format
        
        Args:
            message: Log message
            level: 0=INFO, 1=WARNING, 2=ERROR
            exception: Optional exception object
            func_id: Function identifier (e.g., "F01" for function 1)
            error_code: Specific error code within function (e.g., "E01")
        """
        levels = {0: "INFO", 1: "WARN", 2: "ERROR"}
        level_str = levels.get(level, "INFO")
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Build structured log message
        log_parts = [f"[{timestamp}]", "[TorHandler]", f"[{level_str}]"]
        
        if func_id:
            log_parts.append(f"[{func_id}]")
        if error_code:
            log_parts.append(f"[{error_code}]")
        
        log_parts.append(message)
        
        if exception:
            log_parts.append(f"| Exception: {type(exception).__name__}: {str(exception)}")
        
        log_message = " ".join(log_parts)
        
        # Console output if debug enabled
        if self.debug:
            print(log_message)
        
        # File output
        if level >= self.log_level:
            try:
                with open("tor_handler.log", "a", encoding="utf-8") as log_file:
                    log_file.write(log_message + "\n")
            except Exception as log_err:
                if self.debug:
                    print(f"[CRITICAL] Failed to write log: {log_err}")
    
    # ==================== PROCESS REGISTRY MANAGEMENT ====================
    def load_process_registry(self) -> List[Dict]:
        """Load the process registry from JSON file"""
        try:
            if self.process_registry_file.exists():
                with open(self.process_registry_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('processes', [])
            return []
        except Exception as e:
            self.logger(f"Failed to load process registry | Error: {e}", 1, func_id="F03A")
            return []
    
    def save_process_registry(self, processes: List[Dict]) -> bool:
        """Save the process registry to JSON file (interrupt-proof)"""
        try:
            self.data_directory.mkdir(parents=True, exist_ok=True)
            
            # Create registry data
            registry_data = {
                'version': '1.0',
                'updated': time.strftime('%Y-%m-%d %H:%M:%S'),
                'processes': processes
            }
            
            # Write atomically using temp file
            temp_file = self.process_registry_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(registry_data, f, indent=2)
            
            # Atomic rename
            temp_file.replace(self.process_registry_file)
            return True
        except Exception as e:
            self.logger(f"Failed to save process registry | Error: {e}", 2, e, func_id="F03B", error_code="E01")
            return False
    
    def register_process(self, pid: int, metadata: Optional[Dict] = None) -> bool:
        """Register a new Tor process in the registry"""
        try:
            processes = self.load_process_registry()
            
            # Check if already registered
            if any(p['pid'] == pid for p in processes):
                return True
            
            # Add new process
            process_entry = {
                'pid': pid,
                'started': time.strftime('%Y-%m-%d %H:%M:%S'),
                'timestamp': int(time.time()),
                'metadata': metadata or {}
            }
            
            processes.append(process_entry)
            
            if self.save_process_registry(processes):
                self.logger(f"Process registered | PID: {pid}", 0, func_id="F03C")
                return True
            return False
        except Exception as e:
            self.logger(f"Failed to register process | PID: {pid}", 2, e, func_id="F03C", error_code="E01")
            return False
    
    def unregister_process(self, pid: int) -> bool:
        """Remove a process from the registry"""
        try:
            processes = self.load_process_registry()
            processes = [p for p in processes if p['pid'] != pid]
            
            if self.save_process_registry(processes):
                self.logger(f"Process unregistered | PID: {pid}", 0, func_id="F03D")
                return True
            return False
        except Exception as e:
            self.logger(f"Failed to unregister process | PID: {pid}", 2, e, func_id="F03D", error_code="E01")
            return False
    
    def kill_all_registered_processes(self, force: bool = True) -> bool:
        """Kill all registered processes (interrupt-proof)
        
        Args:
            force: If True, uses SIGKILL (force terminate), else uses SIGTERM
        
        Returns:
            True if all processes were killed successfully
        """
        try:
            # Disable keyboard interrupts during cleanup (only in main thread)
            import signal
            import threading
            
            original_sigint = None
            is_main_thread = threading.current_thread() is threading.main_thread()
            
            if is_main_thread:
                try:
                    original_sigint = signal.signal(signal.SIGINT, signal.SIG_IGN)
                except ValueError:
                    pass  # Not in main thread despite check
            
            try:
                processes = self.load_process_registry()
                
                if not processes:
                    self.logger("No registered processes to kill", 0, func_id="F03E")
                    return True
                
                self.logger(f"Killing {len(processes)} registered process(es) | Force: {force}", 0, func_id="F03E")
                
                killed_count = 0
                failed_pids = []
                
                for process_entry in processes:
                    pid = process_entry['pid']
                    
                    try:
                        proc = psutil.Process(pid)
                        
                        # Verify it's a Tor process AND it's using our config file
                        if 'tor' in proc.name().lower():
                            # Extra verification: check command line args for our config
                            try:
                                cmdline = proc.cmdline()
                                our_config = str(self.torrc_file)
                                
                                # Only kill if it's using our specific torrc file
                                if any(our_config in arg for arg in cmdline):
                                    if force:
                                        proc.kill()  # SIGKILL
                                    else:
                                        proc.terminate()  # SIGTERM
                                    
                                    # Wait for process to die
                                    try:
                                        proc.wait(timeout=5)
                                    except psutil.TimeoutExpired:
                                        if not force:
                                            # If terminate didn't work, force kill
                                            proc.kill()
                                            proc.wait(timeout=5)
                                    
                                    killed_count += 1
                                    self.logger(f"Process killed | PID: {pid}", 0, func_id="F03E")
                                else:
                                    self.logger(f"Tor process not using our config, skipping | PID: {pid}", 1, func_id="F03E")
                                    failed_pids.append(pid)
                            except (psutil.AccessDenied, psutil.ZombieProcess):
                                # Can't access cmdline, skip for safety
                                self.logger(f"Cannot verify process config, skipping | PID: {pid}", 1, func_id="F03E")
                                failed_pids.append(pid)
                        else:
                            self.logger(f"Process is not Tor, skipping | PID: {pid} | Name: {proc.name()}", 1, func_id="F03E")
                            failed_pids.append(pid)
                    
                    except psutil.NoSuchProcess:
                        self.logger(f"Process already dead | PID: {pid}", 0, func_id="F03E")
                        killed_count += 1
                    
                    except Exception as e:
                        self.logger(f"Failed to kill process | PID: {pid} | Error: {e}", 2, e, func_id="F03E")
                        failed_pids.append(pid)
                
                # Clear the registry
                self.save_process_registry([])
                
                self.logger(f"Process cleanup complete | Killed: {killed_count} | Failed: {len(failed_pids)}", 0, func_id="F03E")
                return len(failed_pids) == 0
            
            finally:
                # Restore keyboard interrupt handler (only if we changed it)
                if is_main_thread and original_sigint is not None:
                    try:
                        signal.signal(signal.SIGINT, original_sigint)
                    except ValueError:
                        pass
        
        except Exception as e:
            self.logger("Process cleanup failed", 2, e, func_id="F03E", error_code="E01")
            return False
    
    # ==================== REQUESTS MANAGEMENT ====================
    def download_from_url(self, url: str, path: str) -> None:
        self.logger(f"Downloading from URL: {url}", 0, func_id="F01")
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            self.logger(f"Download started | Target: {path}", 0, func_id="F01")
            
            with open(path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024*1024):
                    f.write(chunk)
            
            self.logger(f"Download completed | File: {path}", 0, func_id="F01")
        except requests.exceptions.RequestException as e:
            self.logger(f"Download failed | URL: {url}", 2, e, func_id="F01", error_code="E01")
    
    # ==================== FOLDERS MANAGEMENT ====================
    def create_required_directories(self) -> bool:
        """Create required directories for Tor operation"""
        try:
            self.binary_dir.mkdir(parents=True, exist_ok=True)
            self.cache_directory.mkdir(parents=True, exist_ok=True)
            self.data_directory.mkdir(parents=True, exist_ok=True)
            self.torrc_template_path.mkdir(parents=True, exist_ok=True)
            self.logger("Directories created successfully", 0, func_id="F02")
            return True
        except Exception as e:
            if self.debug:
                raise
            self.logger("Directory creation failed", 2, e, func_id="F02", error_code="E01")
            return False
    
    def clear_all_directories(self) -> bool:
        """Clear all Tor-related directories and files"""
        try:
            directories = [
                self.binary_dir,
                self.cache_directory,
                self.data_directory,
                self.torrc_template_path
            ]
            
            for directory in directories:
                if directory.exists() and directory.is_dir():
                    shutil.rmtree(directory)
            
            self.logger("All directories cleared", 0, func_id="F03")
            return True
        except Exception as e:
            if self.debug:
                raise
            self.logger("Directory cleanup failed", 2, e, func_id="F03", error_code="E01")
            return False
    
    # ==================== PROCESS MANAGEMENT ====================
    def cleanup_stale_processes(self) -> bool:
        """Clean up any stale Tor processes from previous runs and registry"""
        try:
            # First, kill all processes in the registry
            self.kill_all_registered_processes(force=True)
            
            # Also check the PID file (legacy support)
            if self.tor_process_file.exists():
                try:
                    with open(self.tor_process_file, "r", encoding="utf-8") as f:
                        pid = int(f.read().strip())
                    
                    try:
                        process = psutil.Process(pid)
                        if process.is_running() and process.name().lower() in ['tor', 'tor.exe']:
                            self.logger(f"Stale process found in PID file | PID: {pid} | Action: Terminating", 1, func_id="F04")
                            process.terminate()
                            try:
                                process.wait(timeout=5)
                            except psutil.TimeoutExpired:
                                process.kill()
                                process.wait(timeout=5)
                            self.logger(f"Stale process cleaned | PID: {pid}", 0, func_id="F04")
                    except psutil.NoSuchProcess:
                        pass
                    
                    # Remove PID file
                    self.tor_process_file.unlink()
                except Exception:
                    pass
            
            return True
        except (ValueError, FileNotFoundError):
            return True
        except Exception as e:
            if self.debug:
                raise
            self.logger("Stale process cleanup failed", 2, e, func_id="F04", error_code="E01")
            return False
    
    def get_tor_process(self) -> Optional[psutil.Process]:
        """Get the current Tor process if it exists"""
        # Try current PID first
        if self.tor_process_id != 0:
            try:
                process = psutil.Process(self.tor_process_id)
                if process.is_running() and process.name().lower() in ['tor', 'tor.exe']:
                    return process
            except psutil.NoSuchProcess:
                self.tor_process_id = 0
        
        # Try PID file
        if self.tor_process_file.exists():
            try:
                with open(self.tor_process_file, "r", encoding="utf-8") as f:
                    pid = int(f.read().strip())
                process = psutil.Process(pid)
                if process.is_running() and process.name().lower() in ['tor', 'tor.exe']:
                    self.tor_process_id = pid
                    return process
            except (ValueError, psutil.NoSuchProcess, FileNotFoundError):
                pass
        
        return None
    
    def find_tor_process_by_path(self, tor_path: Path) -> Optional[psutil.Process]:
        """Find a running Tor process by executable path and our config file"""
        tor_path_str = str(tor_path.resolve())
        our_config = str(self.torrc_file)
        
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
            try:
                if proc.info['name'] and proc.info['name'].lower() in ['tor', 'tor.exe']:
                    # Verify it's using our config file
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline and any(our_config in arg for arg in cmdline):
                        if proc.info['exe'] and os.path.samefile(proc.info['exe'], tor_path_str):
                            return proc
                        return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, FileNotFoundError):
                continue
        return None
    
    def terminate_all_tor_processes(self) -> bool:
        """Terminate all Tor processes managed by this handler"""
        try:
            process = self.get_tor_process()
            if process:
                self.logger(f"Terminating process | PID: {process.pid}", 0, func_id="F07")
                process.terminate()
                try:
                    process.wait(timeout=10)
                except psutil.TimeoutExpired:
                    self.logger(f"Force killing Tor process | PID: {process.pid}", 1, func_id="F34")
                    process.kill()
                    process.wait(timeout=5)
            
            self.tor_process_id = 0
            self.running = False
            
            # Clean up PID file
            if self.tor_process_file.exists():
                self.tor_process_file.unlink()
            
            self.logger("Tor service stopped successfully | Status: Stopped", 0, func_id="F34")
            return True
        except Exception as e:
            if self.debug:
                raise
            self.logger("Tor service stop failed", 2, e, func_id="F34", error_code="E01")
            return False
    
    def force_stop_tor(self) -> bool:
        """Force stop any running Tor process (interrupt-proof)"""
        try:
            # Use the interrupt-proof registry killer
            self.kill_all_registered_processes(force=True)
            
            # Also try to find and kill by path (backup method)
            tor_path = self.get_tor_executable_path()
            process = self.find_tor_process_by_path(tor_path)
            
            if process:
                self.logger(f"Force stopping Tor | PID: {process.pid}", 0, func_id="F35")
                try:
                    process.kill()
                    process.wait(timeout=5)
                except Exception:
                    pass
            
            self.running = False
            self.tor_process_id = 0
            
            if self.tor_process_file.exists():
                self.tor_process_file.unlink()
            
            self.logger("Tor force stopped successfully", 0, func_id="F35")
            return True
        except Exception as e:
            if self.debug:
                raise
            self.logger("Tor force stop failed", 2, e, func_id="F35", error_code="E01")
            return False
    
    def restart_tor_service(self) -> bool:
        """Restart the Tor service"""
        try:
            self.logger("Restarting Tor service", 0, func_id="F36")
            self.stop_tor_service()
            time.sleep(2)
            result = self.start_tor_service()
            
            if result:
                self.logger("Tor service restarted successfully", 0, func_id="F36")
            else:
                self.logger("Tor service restart failed", 2, func_id="F36", error_code="E01")
            
            return result
        except Exception as e:
            if self.debug:
                raise
            self.logger("Tor service restart failed", 2, e, func_id="F36", error_code="E02")
            return False
    
    # ==================== TOR BINARY MANAGEMENT ====================
    def calculate_hashes(self, binary_path: Path) -> Dict[str, str]:
        """Calculate MD5 and SHA256 hashes for a file"""
        try:
            self.logger(f"Calculating hashes | File: {binary_path}", 0, func_id="F37")
            
            md5_hash = hashlib.md5()
            sha256_hash = hashlib.sha256()
            
            with open(binary_path, 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    md5_hash.update(byte_block)
                    sha256_hash.update(byte_block)
            
            hashes = {
                'md5': md5_hash.hexdigest(),
                'sha256': sha256_hash.hexdigest()
            }
            
            self.logger(f"Hashes calculated | MD5: {hashes['md5']} | SHA256: {hashes['sha256']}", 0, func_id="F37")
            return hashes
        except Exception as e:
            if self.debug:
                raise
            self.logger(f"Hash calculation failed | File: {binary_path}", 2, e, func_id="F37", error_code="E01")
            return {}
    
    def fetch_latest_tor_download_url(self) -> Dict[str, str]:
        """Fetch the latest Tor binary download URL for the current platform"""
        return_list = {'version': '', 'url': '', 'latest_file': ''}
        
        try:
            response = requests.get(self.tor_version_url, timeout=10)
            response.raise_for_status()
            data = json.loads(response.text)
            
            latest_version_files = data['files']
            system = platform.system().lower()
            machine = platform.machine().lower()
            
            # Determine platform patterns
            if system == "windows":
                if "64" in machine or "amd64" in machine:
                    absolute_patterns = ["windows", "64"]
                else:
                    absolute_patterns = ["windows", "32"]
            elif system == "darwin":
                if "arm" in machine or "aarch64" in machine:
                    absolute_patterns = ["macos", "aarch64"]
                else:
                    absolute_patterns = ["macos", "x86_64"]
            elif system == "linux":
                if "aarch64" in machine or "arm64" in machine:
                    absolute_patterns = ["linux", "aarch64"]
                else:
                    absolute_patterns = ["linux", "x86_64"]
            elif system == "android":
                if "aarch64" in machine or "arm64" in machine:
                    absolute_patterns = ["android", "aarch64"]
                elif "armv7" in machine or "armeabi-v7a" in machine:
                    absolute_patterns = ["android", "armv7"]
                elif "x86_64" in machine:
                    absolute_patterns = ["android", "x86_64"]
                elif "x86" in machine or "i686" in machine:
                    absolute_patterns = ["android", "x86"]
                else:
                    return return_list
            else:
                return return_list
            
            # Find matching file
            for file in latest_version_files:
                file_name = file['file_name'].lower()
                if all(pattern in file_name for pattern in absolute_patterns):
                    return_list['version'] = data['version']
                    return_list['url'] = file['url']
                    return_list['latest_file'] = file['file_name']
                    return_list['binary_md5'] = file['binary_md5']
                    return_list['binary_sha256'] = file['binary_sha256']
                    
                    self.logger(f"Latest Tor version found | Version: {data['version']} | Platform: {system}-{machine}", 0, func_id="F38")
                    return return_list
            
            self.logger(f"No suitable binary found | Platform: {system}-{machine}", 2, func_id="F38", error_code="E01")
            return return_list
        except Exception as e:
            if self.debug:
                raise
            self.logger(f"Failed to fetch latest Tor URL | URL: {self.tor_version_url}", 2, e, func_id="F38", error_code="E02")
            return return_list
    
    def check_tor_binaries_exist(self) -> bool:
        """Check if Tor binary exists and is the latest version"""
        tor_path = self.get_tor_executable_path()
        self.logger(f"Checking Tor binary | Path: {tor_path}", 0, func_id="F39")
        
        if not tor_path.exists():
            self.logger("Tor binary not found", 2, func_id="F39", error_code="E01")
            return False
        
        # Get latest version info
        url_info = self.fetch_latest_tor_download_url()
        if not url_info or not url_info.get('version'):
            self.logger("Could not fetch latest version info", 2, func_id="F39", error_code="E02")
            return False
        
        # Calculate hashes
        calculated_hashes = self.calculate_hashes(tor_path)
        
        if not calculated_hashes:
            self.logger("Hash calculation failed", 2, func_id="F39", error_code="E03")
            return False
        
        self.logger(f"Hash comparison | Expected MD5: {url_info['binary_md5']} | Calculated MD5: {calculated_hashes.get('md5', 'N/A')}", 0, func_id="F39")
        self.logger(f"Hash comparison | Expected SHA256: {url_info['binary_sha256']} | Calculated SHA256: {calculated_hashes.get('sha256', 'N/A')}", 0, func_id="F39")
        
        if (calculated_hashes.get('md5') != url_info['binary_md5'] or
            calculated_hashes.get('sha256') != url_info['binary_sha256']):
            self.logger("Binary hash mismatch | Status: Outdated or corrupted", 2, func_id="F39", error_code="E04")
            return False
        
        self.logger("Tor binary verified | Status: Up-to-date", 0, func_id="F39")
        return True
    
    def check_latest_zip_in_cache(self) -> Tuple[bool, Optional[Dict], Optional[Path]]:
        """Check if the latest Tor binary zip exists in cache"""
        try:
            url_info = self.fetch_latest_tor_download_url()
            if not url_info or not url_info.get('latest_file'):
                self.logger("No suitable binary found for platform", 2, func_id="F40", error_code="E01")
                return (False, None, None)
            
            cache_path = Path(self.cache_directory)
            temp_file_path = cache_path / url_info['latest_file']
            
            if temp_file_path.exists():
                self.logger(f"Cached binary found | File: {temp_file_path}", 0, func_id="F40")
                return (True, url_info, temp_file_path)
            else:
                self.logger(f"Cached binary not found | Expected: {temp_file_path}", 1, func_id="F40")
                return (False, url_info, None)
        except Exception as e:
            if self.debug:
                raise
            self.logger("Cache check failed", 2, e, func_id="F40", error_code="E02")
            return (False, None, None)
    
    def download_and_install_tor_binaries(self, force: bool = False, cache_clear: bool = False) -> bool:
        """Download and install Tor binaries for the current platform"""
        
        # Check if binary exists and is up-to-date
        tor_exist = self.check_tor_binaries_exist()
        
        if tor_exist and not force:
            self.logger("Tor binary up-to-date | Action: Skipping download", 0, func_id="F41")
            return True
        
        if force and tor_exist:
            self.logger("Force download requested | Action: Re-downloading", 0, func_id="F41")
        else:
            self.logger("Tor binary missing or outdated | Action: Downloading", 0, func_id="F41")
        
        try:
            # Terminate any running Tor processes
            self.terminate_all_tor_processes()
            time.sleep(1)
            
            # Prepare directories
            self.binary_dir.mkdir(parents=True, exist_ok=True)
            cache_path = Path(self.cache_directory)
            cache_path.mkdir(parents=True, exist_ok=True)
            
            # Check cache
            check_cached_zip = self.check_latest_zip_in_cache()
            url_info = check_cached_zip[1]
            
            if not url_info:
                self.logger("No download URL available", 2, func_id="F41", error_code="E01")
                return False
            
            if check_cached_zip[0] and not cache_clear:
                temp_file_path = self.cache_directory / url_info['latest_file']
                self.logger(f"Using cached file | File: {temp_file_path}", 0, func_id="F41")
            elif not check_cached_zip[0] or cache_clear:
                if cache_clear:
                    self.logger("Cache clear requested | Action: Re-downloading", 0, func_id="F41")
                    cached_file = cache_path / url_info['latest_file']
                    if cached_file.exists():
                        cached_file.unlink()
                
                self.download_from_url(url_info['url'], cache_path / url_info['latest_file'])
                temp_file_path = self.cache_directory / url_info['latest_file']
            
            # Extract archive
            self.logger(f"Extracting archive | File: {temp_file_path}", 0, func_id="F41")
            
            if url_info['latest_file'].endswith('.zip'):
                with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
                    zip_ref.extractall(self.binary_dir)
                    self.logger(f"Extraction complete | Files extracted: {len(zip_ref.namelist())}", 0, func_id="F41")
            elif url_info['latest_file'].endswith(('.tar.gz', '.tgz')):
                with tarfile.open(temp_file_path, 'r:gz') as tar_ref:
                    if hasattr(tarfile, 'data_filter'):
                        tar_ref.extractall(self.binary_dir, filter='data')
                    else:
                        tar_ref.extractall(self.binary_dir)
                    self.logger("Extraction complete | Format: tar.gz", 0, func_id="F41")
            else:
                error = Exception("Unsupported file format for Tor binary")
                if self.debug:
                    raise error
                self.logger(f"Unsupported archive format | File: {url_info['latest_file']}", 2, error, func_id="F41", error_code="E02")
                return False
            
            # Verify extraction
            tor_exe_path = self.get_tor_executable_path()
            if not tor_exe_path.exists():
                error = Exception(f"Tor executable not found after extraction in {self.binary_dir}")
                if self.debug:
                    raise error
                self.logger(f"Tor executable not found after extraction | Expected: {tor_exe_path}", 2, error, func_id="F41", error_code="E03")
                return False
            
            # Set executable permissions on Unix-like systems
            if platform.system().lower() in ["darwin", "linux"]:
                os.chmod(tor_exe_path, 0o755)
                self.logger(f"Executable permissions set | File: {tor_exe_path}", 0, func_id="F41")
            
            self.logger(f"Tor binaries installation complete | Path: {tor_exe_path}", 0, func_id="F41")
            return True
        except Exception as e:
            if self.debug:
                raise
            self.logger("Tor binary installation failed", 2, e, func_id="F41", error_code="E04")
            return False
    # ==================== PORT MANAGEMENT ====================
    def check_port_availability(self, port: int) -> bool:
        """Check if a port is currently in use
        Returns:
            True if port is IN USE, False if AVAILABLE
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                result = s.connect_ex(("127.0.0.1", port))
                return result == 0
        except Exception:
            return False
    
    def find_available_port(self, start_port: int) -> Optional[int]:
        """Find the next available port starting from start_port"""
        port = start_port
        attempts = 0
        while self.check_port_availability(port):
            port += 1
            attempts += 1
            if attempts > self.max_port_resolve_attempts:
                error = RuntimeError(
                    f"Could not find available port after {self.max_port_resolve_attempts} "
                    f"attempts starting from {start_port}"
                )
                if self.debug:
                    raise error
                self.logger(f"Port search exhausted | Start: {start_port} | Attempts: {attempts}", 2, error, func_id="F09", error_code="E01")
                return None
        return port
    
    def detect_port_conflicts(self) -> Dict[str, List[int]]:
        """Detect and optionally resolve port conflicts"""
        conflicting_ports = {'socks_port': [], 'control_port': []}
        
        # Check SocksPort conflicts
        for i, port in enumerate(self.socks_port):
            if self.check_port_availability(port):
                conflicting_ports['socks_port'].append(port)
                if self.socks_port_collision_resolve:
                    new_port = self.find_available_port(port + 1)
                    if new_port and new_port not in self.socks_port:
                        self.logger(f"Port conflict resolved | Type: SocksPort | Old: {port} | New: {new_port}", 1, func_id="F10")
                        self.socks_port[i] = new_port
        
        # Check ControlPort conflicts
        for i, port in enumerate(self.control_port):
            if self.check_port_availability(port):
                conflicting_ports['control_port'].append(port)
                if self.control_port_collision_resolve:
                    new_port = self.find_available_port(port + 1)
                    if new_port and new_port not in self.control_port:
                        self.logger(f"Port conflict resolved | Type: ControlPort | Old: {port} | New: {new_port}", 1, func_id="F10")
                        self.control_port[i] = new_port
        
        self.conflicting_ports = conflicting_ports
        return conflicting_ports
    
    def add_socks_port(self, socks_port: Optional[int] = None) -> bool:
        """Add a new SOCKS port to the configuration"""
        if self.running:
            error = RuntimeError("Cannot add SocksPort while Tor is running. Use add_runtime_socks_port() instead.")
            if self.debug:
                raise error
            self.logger("SocksPort modification blocked | Reason: Tor is running", 2, error, func_id="F11", error_code="E01")
            return False
        
        if socks_port is None:
            socks_port = self.find_available_port(9050)
            if not socks_port:
                return False
        
        # Check if port is in use
        if self.check_port_availability(socks_port):
            if self.socks_port_collision_resolve:
                socks_port = self.find_available_port(socks_port + 1)
                if not socks_port:
                    return False
            else:
                error = ValueError(f"SocksPort {socks_port} is already in use")
                if self.debug:
                    raise error
                self.logger(f"Port unavailable | Port: {socks_port}", 2, error, func_id="F11", error_code="E02")
                return False
        
        # Check if already configured
        if socks_port in self.socks_port:
            self.logger(f"Port already configured | Port: {socks_port}", 1, func_id="F11")
            return True
        
        self.socks_port.append(socks_port)
        self.logger(f"SocksPort added | Port: {socks_port}", 0, func_id="F11")
        return True
    
    def add_control_port(self, control_port: Optional[int] = None) -> bool:
        """Add a new Control port to the configuration"""
        if self.running:
            error = RuntimeError("Cannot add ControlPort while Tor is running. Use add_runtime_control_port() instead.")
            if self.debug:
                raise error
            self.logger("ControlPort modification blocked | Reason: Tor is running", 2, error, func_id="F12", error_code="E01")
            return False
        
        if control_port is None:
            control_port = self.find_available_port(9051)
            if not control_port:
                return False
        
        # Check if port is in use
        if self.check_port_availability(control_port):
            if self.control_port_collision_resolve:
                control_port = self.find_available_port(control_port + 1)
                if not control_port:
                    return False
            else:
                error = ValueError(f"ControlPort {control_port} is already in use")
                if self.debug:
                    raise error
                self.logger(f"Port unavailable | Port: {control_port}", 2, error, func_id="F12", error_code="E02")
                return False
        
        # Check if already configured
        if control_port in self.control_port:
            self.logger(f"Port already configured | Port: {control_port}", 1, func_id="F12")
            return True
        
        self.control_port.append(control_port)
        self.logger(f"ControlPort added | Port: {control_port}", 0, func_id="F12")
        return True
    
    # ==================== RUNTIME PORT MANAGEMENT ====================
    def wait_for_control_port(self, timeout: int = 15, wait_after_ready: int = 1) -> bool:
        """Wait for control port to be ready and fully initialized"""
        start = time.time()
        
        # First wait for port to be listening
        while time.time() - start < timeout:
            if self.check_port_availability(self.control_port[0]):
                break
            time.sleep(0.3)
        else:
            self.logger(f"Control port timeout | Port: {self.control_port[0]} | Timeout: {timeout}s", 2, func_id="F13", error_code="E01")
            return False
        
        # Wait for initialization
        if wait_after_ready > 0:
            time.sleep(wait_after_ready)
        
        # Verify we can actually connect and authenticate
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                auth_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                auth_socket.settimeout(5)
                auth_socket.connect(("127.0.0.1", self.control_port[0]))
                
                cookie = self.read_authentication_cookie()
                if cookie:
                    cookie_hex = binascii.hexlify(cookie).decode()
                    auth_socket.send(f'AUTHENTICATE {cookie_hex}\r\n'.encode())
                    resp = auth_socket.recv(1024).decode()
                    auth_socket.close()
                    
                    if resp.startswith("250"):
                        return True
                else:
                    auth_socket.close()
                    return True
            except Exception as e:
                if attempt == max_attempts - 1:
                    self.logger(f"Control port verification failed | Attempts: {max_attempts}", 1, e, func_id="F13", error_code="E02")
                time.sleep(1)
        
        return False
    
    def add_runtime_socks_port(self, socks_port: Optional[int] = None, temporary: bool = False) -> Union[bool, Dict]:
        """Add a SOCKS port at runtime without restarting Tor"""
        if not self.running:
            error = RuntimeError("Tor is not running. Start Tor first.")
            if self.debug:
                raise error
            self.logger("Runtime operation blocked | Reason: Tor not running", 2, error, func_id="F14", error_code="E01")
            return False
        
        if socks_port is None:
            socks_port = self.find_available_port(19050)
            if not socks_port:
                return False
        
        # Check if port is in use
        if self.check_port_availability(socks_port):
            if self.socks_port_collision_resolve:
                socks_port = self.find_available_port(socks_port + 1)
                if not socks_port:
                    return False
            else:
                error = ValueError(f"SocksPort {socks_port} is already in use")
                if self.debug:
                    raise error
                self.logger(f"Runtime port unavailable | Port: {socks_port}", 2, error, func_id="F14", error_code="E02")
                return False
        
        try:
            current_response = self.send_control_commands("GETCONF SocksPort", skip_wait=True)
            if not current_response:
                return False
            
            # Parse current ports
            current_ports = []
            for resp in current_response.values():
                resp_text = resp['response']
                for line in resp_text.split('\n'):
                    if line.startswith('250') and 'SocksPort=' in line:
                        port_str = line.split('SocksPort=')[1].strip()
                        if port_str and port_str.isdigit():
                            current_ports.append(port_str)
            
            # Build new port list
            new_ports = current_ports + [str(socks_port)]
            ports_str = ' '.join(new_ports)
            command = f'SETCONF SocksPort="{ports_str}"'
            
            commands = [command]
            if not temporary:
                commands.append('SAVECONF')
            
            result = self.send_control_commands(commands, skip_wait=True)
            if result:
                self.temp_config['socks_port'].append(socks_port)
                self.logger(f"Runtime SocksPort added | Port: {socks_port} | Temporary: {temporary}", 0, func_id="F14")
            return result
        except Exception as e:
            if self.debug:
                raise
            self.logger("Runtime SocksPort addition failed", 2, e, func_id="F14", error_code="E03")
            return False
    
    def add_runtime_control_port(self, control_port: Optional[int] = None, temporary: bool = False) -> Union[bool, Dict]:
        """Add a Control port at runtime without restarting Tor"""
        if not self.running:
            error = RuntimeError("Tor is not running. Start Tor first.")
            if self.debug:
                raise error
            self.logger("Runtime operation blocked | Reason: Tor not running", 2, error, func_id="F15", error_code="E01")
            return False
        
        if control_port is None:
            control_port = self.find_available_port(19051)
            if not control_port:
                return False
        
        # Check if port is in use
        if self.check_port_availability(control_port):
            if self.control_port_collision_resolve:
                control_port = self.find_available_port(control_port + 1)
                if not control_port:
                    return False
            else:
                error = ValueError(f"ControlPort {control_port} is already in use")
                if self.debug:
                    raise error
                self.logger(f"Runtime port unavailable | Port: {control_port}", 2, error, func_id="F15", error_code="E02")
                return False
        
        try:
            current_response = self.send_control_commands("GETCONF ControlPort", skip_wait=True)
            if not current_response:
                return False
            
            # Parse current ports
            current_ports = []
            for resp in current_response.values():
                resp_text = resp['response']
                for line in resp_text.split('\n'):
                    if line.startswith('250') and 'ControlPort=' in line:
                        port_str = line.split('ControlPort=')[1].strip()
                        if port_str and port_str.isdigit():
                            current_ports.append(port_str)
            
            # Build new port list
            new_ports = current_ports + [str(control_port)]
            ports_str = ' '.join(new_ports)
            command = f'SETCONF ControlPort="{ports_str}"'
            
            commands = [command]
            if not temporary:
                commands.append('SAVECONF')
            
            result = self.send_control_commands(commands, skip_wait=True)
            if result:
                self.temp_config['control_port'].append(control_port)
                self.logger(f"Runtime ControlPort added | Port: {control_port} | Temporary: {temporary}", 0, func_id="F15")
            return result
        except Exception as e:
            if self.debug:
                raise
            self.logger("Runtime ControlPort addition failed", 2, e, func_id="F15", error_code="E03")
            return False
    
    # ==================== HIDDEN SERVICES ====================
    def register_hidden_service(
        self,
        port: int,
        target_port: int,
        pre_config: bool = False,
        host: Optional[str] = None,
        pk: Optional[bytes] = None,
        sk: Optional[bytes] = None
    ) -> bool:
        """Register a hidden service configuration"""
        if self.running:
            error = RuntimeError("Cannot add HiddenService while Tor is running. Use register_runtime_hidden_service() instead.")
            if self.debug:
                raise error
            self.logger("HiddenService modification blocked | Reason: Tor is running", 2, error, func_id="F16", error_code="E01")
            return False
        
        # Check for port conflicts
        if self.check_port_availability(port):
            if self.hidden_service_port_collision_resolve:
                new_port = self.find_available_port(port + 1)
                if not new_port:
                    return False
                self.logger(f"HiddenService port conflict resolved | Old: {port} | New: {new_port}", 1, func_id="F16")
                port = new_port
            else:
                error = ValueError(f"HiddenServicePort {port} is already in use")
                if self.debug:
                    raise error
                self.logger(f"HiddenService port unavailable | Port: {port}", 2, error, func_id="F16", error_code="E02")
                return False
        
        hidden_service_dir = self.data_directory / f"hidden_service_{len(self.hidden_services) + 1}"
        
        self.hidden_services.append({
            "dir": hidden_service_dir,
            "port": port,
            "target_port": target_port,
            "pre_config": pre_config,
            "host": host,
            "pk": pk,
            "sk": sk
        })
        
        self.logger(f"HiddenService registered | Port: {port} | Target: {target_port} | PreConfig: {pre_config}", 0, func_id="F16")
        return True
    
    def write_hidden_service_configs(self, index: int) -> bool:
        """Write pre-configured hidden service keys to disk"""
        try:
            service = self.hidden_services[index]
            hs_dir = service["dir"]
            hs_dir.mkdir(parents=True, exist_ok=True)
            
            if service.get("pre_config") and service.get("host") and service.get("pk") and service.get("sk"):
                hostname_path = hs_dir / "hostname"
                private_key_path = hs_dir / "hs_ed25519_secret_key"
                public_key_path = hs_dir / "hs_ed25519_public_key"
                
                with open(hostname_path, "w", encoding="utf-8") as f:
                    f.write(service["host"])
                
                with open(private_key_path, "wb") as f:
                    pk_data = service["pk"] if isinstance(service["pk"], bytes) else service["pk"].encode()
                    f.write(pk_data)
                
                with open(public_key_path, "wb") as f:
                    sk_data = service["sk"] if isinstance(service["sk"], bytes) else service["sk"].encode()
                    f.write(sk_data)
                
                self.logger(f"HiddenService config written | Index: {index} | Dir: {hs_dir}", 0, func_id="F17")
                return True
            return True
        except Exception as e:
            if self.debug:
                raise
            self.logger(f"HiddenService config write failed | Index: {index}", 2, e, func_id="F17", error_code="E01")
            return False
    
    def update_hidden_service_from_disk(self, index: int) -> bool:
        """Update hidden service details by reading from disk after Tor generates them
        
        Args:
            index: Index of the hidden service in self.hidden_services
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if index < 0 or index >= len(self.hidden_services):
                self.logger(f"Invalid index | Index: {index} | Total: {len(self.hidden_services)}", 2, func_id="F18", error_code="E01")
                return False
            
            service = self.hidden_services[index]
            hs_dir = service["dir"]
            
            if not hs_dir.exists():
                self.logger(f"HiddenService directory not found | Dir: {hs_dir}", 2, func_id="F18", error_code="E02")
                return False
            
            # Read hostname
            hostname_path = hs_dir / "hostname"
            if hostname_path.exists():
                with open(hostname_path, "r", encoding="utf-8") as f:
                    hostname = f.read().strip()
                    service["host"] = hostname
                    self.logger(f"Hostname loaded | Index: {index} | Host: {hostname}", 0, func_id="F18")
            
            # Read public key
            public_key_path = hs_dir / "hs_ed25519_public_key"
            if public_key_path.exists():
                with open(public_key_path, "rb") as f:
                    pk_data = f.read()
                    service["pk"] = pk_data
                    self.logger(f"Public key loaded | Index: {index} | Size: {len(pk_data)} bytes", 0, func_id="F18")
            
            # Read private key
            private_key_path = hs_dir / "hs_ed25519_secret_key"
            if private_key_path.exists():
                with open(private_key_path, "rb") as f:
                    sk_data = f.read()
                    service["sk"] = sk_data
                    self.logger(f"Secret key loaded | Index: {index} | Size: {len(sk_data)} bytes", 0, func_id="F18")
            
            # Mark as configured if we got the hostname
            if service["host"]:
                service["pre_config"] = True
            
            self.logger(f"HiddenService updated from disk | Index: {index} | Complete: {bool(service['host'] and service['pk'] and service['sk'])}", 0, func_id="F18")
            return True
            
        except Exception as e:
            if self.debug:
                raise
            self.logger(f"Failed to update HiddenService from disk | Index: {index}", 2, e, func_id="F18", error_code="E03")
            return False
    
    def refresh_all_hidden_services(self) -> bool:
        """Refresh all hidden service details from disk
        
        Should be called after Tor has started and generated the onion addresses
        """
        try:
            success_count = 0
            for i in range(len(self.hidden_services)):
                if self.update_hidden_service_from_disk(i):
                    success_count += 1
            
            self.logger(f"HiddenServices refreshed | Total: {len(self.hidden_services)} | Success: {success_count}", 0, func_id="F19")
            return success_count == len(self.hidden_services)
        except Exception as e:
            if self.debug:
                raise
            self.logger("Failed to refresh HiddenServices", 2, e, func_id="F19", error_code="E01")
            return False
    
    def get_hidden_service(
        self,
        index: Optional[int] = None,
        hostname: str = '',
        port: int = 0,
        get_all: bool = True
    ) -> Union[List[Dict], Dict, None]:
        """Retrieve hidden service by index, hostname, or port"""
        if get_all:
            return self.hidden_services
        
        if index is not None and 0 <= index < len(self.hidden_services):
            return self.hidden_services[index]
        
        for service in self.hidden_services:
            if hostname and service.get("host") == hostname:
                return service
            if port and service.get("port") == port:
                return service
        
        return None
    
    def unregister_hidden_service(self, hostname: str = '', index: Optional[int] = None) -> bool:
        """Remove a hidden service by hostname or index"""
        if self.running:
            error = RuntimeError("Cannot remove HiddenService while Tor is running")
            if self.debug:
                raise error
            self.logger("HiddenService removal blocked | Reason: Tor is running", 2, error, func_id="F21", error_code="E01")
            return False
        
        try:
            service = None
            removed_index = -1
            
            if index is not None and 0 <= index < len(self.hidden_services):
                service = self.hidden_services.pop(index)
                removed_index = index
            elif hostname:
                for i, s in enumerate(self.hidden_services):
                    if s.get("host") == hostname:
                        service = self.hidden_services.pop(i)
                        removed_index = i
                        break
            
            if not service:
                error = ValueError("Hidden service not found")
                if self.debug:
                    raise error
                self.logger(f"HiddenService not found | Hostname: {hostname} | Index: {index}", 2, error, func_id="F21", error_code="E02")
                return False
            
            # Clean up directory
            hs_dir = service["dir"]
            if hs_dir.exists() and hs_dir.is_dir():
                for item in hs_dir.iterdir():
                    if item.is_file():
                        item.unlink()
                hs_dir.rmdir()
            
            self.logger(f"HiddenService unregistered | Index: {removed_index} | Dir: {hs_dir}", 0, func_id="F21")
            return True
        except Exception as e:
            if self.debug:
                raise
            self.logger("HiddenService unregistration failed", 2, e, func_id="F21", error_code="E03")
            return False
    
    def register_runtime_hidden_service(
        self,
        port: int,
        target_port: int,
        pre_config: bool = False,
        host: Optional[str] = None,
        pk: Optional[bytes] = None,
        sk: Optional[bytes] = None,
        temporary: bool = False
    ) -> Union[bool, Dict]:
        """Add a hidden service at runtime without restarting Tor"""
        if not self.running:
            error = RuntimeError("Tor is not running. Start Tor first.")
            if self.debug:
                raise error
            self.logger("Runtime operation blocked | Reason: Tor not running", 2, error, func_id="F22", error_code="E01")
            return False
        
        # Check for port conflicts
        if self.check_port_availability(port):
            if self.hidden_service_port_collision_resolve:
                new_port = self.find_available_port(port + 1)
                if not new_port:
                    return False
                self.logger(f"Runtime HiddenService port conflict resolved | Old: {port} | New: {new_port}", 1, func_id="F22")
                port = new_port
            else:
                error = ValueError(f"HiddenServicePort {port} is already in use")
                if self.debug:
                    raise error
                self.logger(f"Runtime HiddenService port unavailable | Port: {port}", 2, error, func_id="F22", error_code="E02")
                return False
        
        try:
            # Use ADD_ONION command for runtime service
            if pre_config and sk:
                # Use pre-configured key
                if isinstance(sk, bytes):
                    sk_str = sk.decode('utf-8')
                else:
                    sk_str = sk
                
                if not sk_str.startswith('ED25519-V3:'):
                    sk_str = f'ED25519-V3:{sk_str}'
                
                command = f'ADD_ONION {sk_str} Port={port},127.0.0.1:{target_port}'
            else:
                # Generate new key
                command = f'ADD_ONION NEW:ED25519-V3 Port={port},127.0.0.1:{target_port}'
            
            # Add Detach flag to persist the service beyond the control connection
            # Without this, the service disappears when the control connection closes
            command += ' Flags=Detach'
            
            result = self.send_control_commands(command, skip_wait=True)
            
            if result and len(result) > 0:
                resp = result[1]['response']
                
                # Parse response to get onion address and key
                onion_address = None
                service_key = None
                
                for line in resp.split('\n'):
                    if 'ServiceID=' in line:
                        onion_address = line.split('ServiceID=')[1].strip() + '.onion'
                    elif 'PrivateKey=' in line:
                        service_key = line.split('PrivateKey=')[1].strip()
                
                if onion_address:
                    hidden_service_config = {
                        "port": port,
                        "target_port": target_port,
                        "onion_address": onion_address,
                        "service_key": service_key,
                        "temporary": temporary,
                        "runtime": True
                    }
                    
                    self.temp_config['hidden_services'].append(hidden_service_config)
                    self.logger(f"Runtime HiddenService registered | Address: {onion_address} | Port: {port} | Target: {target_port} | Temporary: {temporary}", 0, func_id="F22")
                    
                    return {
                        'success': True,
                        'onion_address': onion_address,
                        'service_key': service_key,
                        'port': port,
                        'target_port': target_port
                    }
                else:
                    self.logger("Failed to parse ADD_ONION response", 2, func_id="F22", error_code="E03")
                    return False
            
            return False
        except Exception as e:
            if self.debug:
                raise
            self.logger("Runtime HiddenService registration failed", 2, e, func_id="F22", error_code="E04")
            return False
    
    # def remove_runtime_hidden_service(self, onion_address: str) -> bool:
    #     """Remove a runtime hidden service"""
    #     if not self.running:
    #         error = RuntimeError("Tor is not running")
    #         if self.debug:
    #             raise error
    #         self.logger("Runtime operation blocked | Reason: Tor not running", 2, error, func_id="F23", error_code="E01")
    #         return False
    #     try:
    #         # Normalize address
    #         service_id = onion_address.replace('.onion', '')
    #         command = f'DEL_ONION {service_id}'
    #         result = self.send_control_commands(command, skip_wait=True)
    #         if result and len(result) > 0:
    #             resp = result[1]['response']
    #             if '250 OK' in resp:
    #                 # Remove from temp config
    #                 self.temp_config['hidden_services'] = [
    #                     s for s in self.temp_config['hidden_services']
    #                     if s.get('onion_address', '').replace('.onion', '') != service_id
    #                 ]
    #                 self.logger(f"Runtime HiddenService removed | Address: {onion_address}", 0, func_id="F23")
    #                 return True
    #         self.logger(f"Failed to remove runtime HiddenService | Address: {onion_address}", 2, func_id="F23", error_code="E02")
    #         return False
    #     except Exception as e:
    #         if self.debug:
    #             raise
    #         self.logger("Runtime HiddenService removal failed", 2, e, func_id="F23", error_code="E03")
    #         return False
    
    def remove_runtime_hidden_service(self, onion_address: str) -> bool:
        """Remove a runtime hidden service"""
        if not self.running:
            error = RuntimeError("Tor is not running")
            if self.debug:
                raise error
            self.logger("Runtime operation blocked | Reason: Tor not running", 2, error, func_id="F23", error_code="E01")
            return False
        try:
            # Normalize address
            service_id = onion_address.replace('.onion', '')
            
            # Add sufficient delay to ensure Tor has fully registered the service
            # Tor needs time to process ADD_ONION before DEL_ONION can work
            time.sleep(2)
            
            command = f'DEL_ONION {service_id}'
            result = self.send_control_commands(command, skip_wait=True)
            if result and len(result) > 0:
                # Get the first (and should be only) response
                resp = result[list(result.keys())[0]]['response']
                self.logger(f"DEL_ONION response | ServiceID: {service_id[:20]}... | Response: {resp}", 0, func_id="F23")
                # Check for success - Tor returns "250 OK" or just "250"
                if '250' in resp:
                    # Check if service was persisted
                    service_to_remove = None
                    for svc in self.temp_config['hidden_services']:
                        if svc.get('onion_address', '').replace('.onion', '') == service_id:
                            service_to_remove = svc
                            break
                    
                    is_persisted = service_to_remove and not service_to_remove.get('temporary', False) and service_to_remove.get('runtime', False)
                    
                    # If persisted, keep it in temp_config but mark as detached
                    # If not persisted, remove it completely
                    if is_persisted:
                        # Mark as detached from Tor but still in config
                        for svc in self.temp_config['hidden_services']:
                            if svc.get('onion_address', '').replace('.onion', '') == service_id:
                                svc['detached'] = True
                                svc['active'] = False
                        removed_count = 0
                        self.logger(f"Runtime HiddenService detached (persisted) | Address: {onion_address}", 0, func_id="F23")
                    else:
                        # Remove from temp config completely
                        original_count = len(self.temp_config['hidden_services'])
                        self.temp_config['hidden_services'] = [
                            s for s in self.temp_config['hidden_services']
                            if s.get('onion_address', '').replace('.onion', '') != service_id
                        ]
                        removed_count = original_count - len(self.temp_config['hidden_services'])
                        
                        # Also remove from hidden_services if it was persisted
                        self.hidden_services = [
                            s for s in self.hidden_services
                            if s.get('host', '').replace('.onion', '') != service_id
                        ]
                        self.logger(f"Runtime HiddenService removed | Address: {onion_address} | Removed: {removed_count}", 0, func_id="F23")
                    
                    return True
                else:
                    # Check if it's an error response
                    if '552' in resp or '551' in resp:
                        self.logger(f"DEL_ONION error | Address: {onion_address} | Response: {resp}", 2, func_id="F23", error_code="E02")
                    else:
                        self.logger(f"Unexpected DEL_ONION response | Address: {onion_address} | Response: {resp}", 2, func_id="F23", error_code="E03")
                    return False
            self.logger(f"No response from DEL_ONION | Address: {onion_address}", 2, func_id="F23", error_code="E04")
            return False
        except Exception as e:
            if self.debug:
                raise
            self.logger("Runtime HiddenService removal failed", 2, e, func_id="F23", error_code="E05")
            return False
    def list_runtime_hidden_services(self) -> List[Dict]:
        """List all runtime hidden services"""
        return self.temp_config['hidden_services']
    
    def persist_runtime_hidden_service(self, onion_address: str) -> bool:
        """Persist a runtime hidden service to torrc configuration"""
        try:
            # Find the runtime service
            service_id = onion_address.replace('.onion', '')
            runtime_service = None
            
            for svc in self.temp_config['hidden_services']:
                if svc.get('onion_address', '').replace('.onion', '') == service_id:
                    runtime_service = svc
                    break
            
            if not runtime_service:
                error = ValueError(f"Runtime hidden service {onion_address} not found")
                if self.debug:
                    raise error
                self.logger(f"Runtime HiddenService not found | Address: {onion_address}", 2, error, func_id="F25", error_code="E01")
                return False
            
            # Check if already persisted to avoid duplicates
            for existing_svc in self.hidden_services:
                if existing_svc.get('host', '').replace('.onion', '') == service_id:
                    self.logger(f"HiddenService already persisted | Address: {onion_address}", 1, func_id="F25")
                    return True
            
            # Add to permanent hidden services list
            hs_dir = self.data_directory / f"hidden_service_{len(self.hidden_services) + 1}"
            hs_dir.mkdir(parents=True, exist_ok=True)
            
            # Write the service key to disk in proper Tor format
            if runtime_service.get('service_key'):
                key_str = runtime_service['service_key']
                if key_str.startswith('ED25519-V3:'):
                    key_data = key_str.split('ED25519-V3:')[1]
                else:
                    key_data = key_str
                
                import base64
                private_key_path = hs_dir / "hs_ed25519_secret_key"
                public_key_path = hs_dir / "hs_ed25519_public_key"
                
                try:
                    # Decode the base64 key
                    key_bytes = base64.b64decode(key_data)
                    
                    # Write secret key in Tor's format
                    # The key_bytes should already be in the correct format from ADD_ONION
                    with open(private_key_path, "wb") as f:
                        f.write(key_bytes)
                    
                    # Try to derive public key from the onion address
                    # V3 onion addresses encode the public key
                    import base64
                    onion_addr = runtime_service['onion_address'].replace('.onion', '')
                    # Decode base32 (Tor uses base32 for v3 addresses)
                    try:
                        # V3 addresses are 56 chars base32, first 32 bytes is public key
                        pub_key_b32 = onion_addr.upper()
                        pub_key_bytes = base64.b32decode(pub_key_b32)
                        
                        # Write public key with Tor's header
                        pub_key_header = b'== ed25519v1-public: type0 =='
                        with open(public_key_path, "wb") as f:
                            f.write(pub_key_header)
                            f.write(pub_key_bytes[:32])  # First 32 bytes is the public key
                    except Exception as pub_err:
                        self.logger(f"Public key derivation warning | Address: {onion_address}", 1, pub_err, func_id="F25")
                        
                except Exception as key_err:
                    self.logger(f"Key write warning | Address: {onion_address}", 1, key_err, func_id="F25")
            
            # Write hostname
            hostname_path = hs_dir / "hostname"
            with open(hostname_path, "w", encoding="utf-8") as f:
                f.write(runtime_service['onion_address'])
            
            # Add to hidden services configuration
            self.hidden_services.append({
                "dir": hs_dir,
                "port": runtime_service['port'],
                "target_port": runtime_service['target_port'],
                "pre_config": True,
                "host": runtime_service['onion_address'],
                "pk": None,
                "sk": runtime_service.get('service_key', '').encode() if runtime_service.get('service_key') else None
            })
            
            # Save to torrc
            if not self.running:
                success = self.save_torrc_configuration()
            else:
                self.logger("Torrc update deferred | Reason: Tor is running | Action: Will apply on restart", 1, func_id="F25")
                success = True
            
            if success:
                runtime_service['temporary'] = False
                self.logger(f"Runtime HiddenService persisted | Address: {onion_address}", 0, func_id="F25")
            
            return success
        except Exception as e:
            if self.debug:
                raise
            self.logger("Runtime HiddenService persistence failed", 2, e, func_id="F25", error_code="E02")
            return False
    
    # ==================== CONFIGURATION MANAGEMENT ====================
    def load_torrc_configuration(self) -> bool:
        """Load existing torrc file to populate configuration"""
        if not self.torrc_file.exists():
            return True
        
        try:
            with open(self.torrc_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # Clear existing configuration to avoid duplicates
            socks_ports = []
            control_ports = []
            hidden_services = []
            current_hs = {}
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                if line.startswith("SocksPort"):
                    port = int(line.split()[1])
                    if port not in socks_ports:
                        socks_ports.append(port)
                
                elif line.startswith("ControlPort"):
                    port = int(line.split()[1])
                    if port not in control_ports:
                        control_ports.append(port)
                
                elif line.startswith("HiddenServiceDir"):
                    # Save previous service
                    if current_hs:
                        hidden_services.append(current_hs)
                        current_hs = {}
                    
                    # Parse directory path
                    dir_path = line.split("\"")[1] if "\"" in line else line.split()[1]
                    current_hs["dir"] = Path(dir_path)
                
                elif line.startswith("HiddenServicePort"):
                    parts = line.split()
                    port = int(parts[1])
                    target = parts[2].split(":")[1] if ":" in parts[2] else parts[2]
                    current_hs["port"] = port
                    current_hs["target_port"] = int(target)
                    current_hs["pre_config"] = False
                    current_hs["host"] = None
                    current_hs["pk"] = None
                    current_hs["sk"] = None
            
            # Save last service
            if current_hs:
                hidden_services.append(current_hs)
            
            # Replace configuration (not append)
            self.hidden_services = hidden_services
            if socks_ports:
                self.socks_port = socks_ports
            if control_ports:
                self.control_port = control_ports
            
            # Load existing hidden service details from disk
            for i in range(len(self.hidden_services)):
                self.update_hidden_service_from_disk(i)
            
            self.logger(f"Torrc configuration loaded | File: {self.torrc_file} | SocksPorts: {len(socks_ports)} | ControlPorts: {len(control_ports)} | HiddenServices: {len(self.hidden_services)}", 0, func_id="F26")
            return True
        except Exception as e:
            if self.debug:
                raise
            self.logger(f"Torrc load failed | File: {self.torrc_file}", 2, e, func_id="F26", error_code="E01")
            return False
    
    def save_torrc_configuration(self) -> bool:
        """Save the current configuration to torrc file"""
        if self.running:
            error = RuntimeError("Cannot save torrc while Tor is running")
            if self.debug:
                raise error
            self.logger("Torrc save blocked | Reason: Tor is running", 2, error, func_id="F27", error_code="E01")
            return False
        
        try:
            self.torrc_template_path.mkdir(parents=True, exist_ok=True)
            self.data_directory.mkdir(parents=True, exist_ok=True)
            
            with open(self.torrc_file, "w", encoding="utf-8") as f:
                f.write("# This is a generated torrc file\n")
                # Use forward slashes even on Windows - Tor handles this correctly
                data_dir = str(self.data_directory).replace('\\', '/')
                f.write(f'DataDirectory "{data_dir}"\n')
                
                # Write SOCKS ports
                for port in self.socks_port:
                    f.write(f"SocksPort {port}\n")
                
                # Write Control ports
                for port in self.control_port:
                    f.write(f"ControlPort {port}\n")
                
                # Write authentication
                if self.cookie_authentication:
                    f.write("CookieAuthentication 1\n")
                
                # Write hidden services
                for i, service in enumerate(self.hidden_services):
                    if service.get("pre_config"):
                        self.write_hidden_service_configs(i)
                    
                    service_dir = str(service["dir"]).replace('\\', '/')
                    f.write(f'HiddenServiceDir "{service_dir}"\n')
                    f.write(f"HiddenServicePort {service['port']} 127.0.0.1:{service['target_port']}\n")
            
            self.logger(f"Torrc configuration saved | File: {self.torrc_file} | SocksPorts: {len(self.socks_port)} | ControlPorts: {len(self.control_port)} | HiddenServices: {len(self.hidden_services)}", 0, func_id="F27")
            return True
        except Exception as e:
            if self.debug:
                raise
            self.logger(f"Torrc save failed | File: {self.torrc_file}", 2, e, func_id="F27", error_code="E02")
            return False
    
    # ==================== CONTROL PORT COMMUNICATION ====================
    def read_authentication_cookie(self) -> Optional[bytes]:
        """Read the Tor control authentication cookie"""
        cookie_path = self.data_directory / "control_auth_cookie"
        try:
            if cookie_path.exists():
                with open(cookie_path, "rb") as f:
                    return f.read()
            return None
        except Exception as e:
            if self.debug:
                raise
            self.logger(f"Cookie read failed | Path: {cookie_path}", 2, e, func_id="F28", error_code="E01")
            return None
    
    def authenticate_control_connection(self) -> Optional[socket.socket]:
        """Authenticate with Tor control port using cookie"""
        auth_socket = None
        try:
            auth_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            auth_socket.settimeout(10)
            auth_socket.connect(("127.0.0.1", self.control_port[0]))
            
            cookie = self.read_authentication_cookie()
            if not cookie:
                error = RuntimeError("Cookie authentication file not found")
                if self.debug:
                    raise error
                self.logger("Authentication cookie not found", 2, error, func_id="F29", error_code="E01")
                auth_socket.close()
                return None
            
            cookie_hex = binascii.hexlify(cookie).decode()
            cmd = f'AUTHENTICATE {cookie_hex}\r\n'
            auth_socket.send(cmd.encode())
            
            resp = auth_socket.recv(1024).decode()
            if not resp.startswith("250"):
                auth_socket.close()
                error = RuntimeError(f"Authentication failed: {resp.strip()}")
                if self.debug:
                    raise error
                self.logger(f"Control authentication failed | Response: {resp.strip()}", 2, error, func_id="F29", error_code="E02")
                return None
            
            return auth_socket
        except Exception as e:
            if auth_socket:
                try:
                    auth_socket.close()
                except Exception:
                    pass
            if self.debug:
                raise
            self.logger("Control connection authentication failed", 2, e, func_id="F29", error_code="E03")
            return None
    
    def send_control_commands(self, commands: Union[str, List[str]], skip_wait: bool = False) -> Dict:
        """Send commands to Tor control port"""
        response = {}
        
        # Wait for control port to be ready
        if not skip_wait:
            max_retries = 3
            port_ready = False
            for retry in range(max_retries):
                if self.check_port_availability(self.control_port[0]):
                    port_ready = True
                    break
                if retry < max_retries - 1:
                    time.sleep(1)
            
            if not port_ready:
                self.logger(f"Control port not ready | Port: {self.control_port[0]} | Retries: {max_retries}", 2, func_id="F30", error_code="E01")
                return response
        
        auth_socket = self.authenticate_control_connection()
        if not auth_socket:
            return response
        
        try:
            if isinstance(commands, str):
                commands = [commands]
            
            auth_socket.settimeout(10)
            
            for cmd_index, command in enumerate(commands):
                cmd = command.strip()
                auth_socket.send((cmd + "\r\n").encode())
                
                # Read response
                full_response = ""
                start_time = time.time()
                timeout_limit = 10
                
                while time.time() - start_time < timeout_limit:
                    try:
                        chunk = auth_socket.recv(4096).decode()
                        if not chunk:
                            break
                        full_response += chunk
                        
                        # Check if response is complete
                        lines = full_response.strip().split('\n')
                        last_line = lines[-1] if lines else ""
                        
                        if last_line.startswith('250 ') or last_line == '250 OK' or last_line.startswith('551') or last_line.startswith('552'):
                            break
                    except socket.timeout:
                        break
                
                response[len(response) + 1] = {
                    'command': cmd,
                    'response': full_response.strip()
                }
                
                self.logger(f"Control command sent | Command: {cmd[:50]}... | Response length: {len(full_response)} bytes", 0, func_id="F30")
            
            auth_socket.close()
            return response
        except Exception as e:
            if auth_socket:
                try:
                    auth_socket.close()
                except Exception:
                    pass
            if self.debug:
                raise
            self.logger("Control command failed", 2, e, func_id="F30", error_code="E02")
            return response
    
    # ==================== TOR SERVICE LIFECYCLE ====================
    def get_tor_executable_path(self) -> Path:
        """Get the platform-specific Tor executable path"""
        system = platform.system().lower()
        
        if system == "windows":
            exe_name = "tor.exe"
        elif system in ["darwin", "linux"]:
            exe_name = "tor"
        elif system == "android":
            exe_name = "libtor.so"
        else:
            exe_name = "tor"
        
        possible_paths = [
            self.binary_dir / "tor" / exe_name,
            self.binary_dir / "Tor" / exe_name,
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        return self.binary_dir / "tor" / exe_name
    
    def wait_for_tor_ready(self, timeout: int = 30) -> bool:
        """Wait for Tor to be ready by checking if SOCKS port is listening"""
        start = time.time()
        while time.time() - start < timeout:
            if self.check_port_availability(self.socks_port[0]):
                return True
            time.sleep(0.5)
        return False
    
    def start_tor_service(self) -> bool:
        """Start the Tor service"""
        if self.running:
            self.logger("Tor already running", 1, func_id="F33")
            return True
        
        try:
            # Clean up any stale processes
            self.cleanup_stale_processes()
            
            # Auto-initialize if needed
            tor_path = self.get_tor_executable_path()
            if not tor_path.exists():
                self.logger("Tor executable not found, attempting auto-download", 1, func_id="F33")
                if not self.download_and_install_tor_binaries():
                    error = FileNotFoundError(f"Failed to download Tor binaries")
                    if self.debug:
                        raise error
                    self.logger("Failed to download Tor binaries", 2, error, func_id="F33", error_code="E01")
                    return False
                tor_path = self.get_tor_executable_path()
            
            self.logger(f"Tor executable path | Path: {tor_path}", 0, func_id="F33")
            
            if not tor_path.exists():
                error = FileNotFoundError(f"Tor executable not found at {tor_path}")
                if self.debug:
                    raise error
                self.logger(f"Tor executable not found | Path: {tor_path}", 2, error, func_id="F33", error_code="E01a")
                return False
            
            # Check for torrc file - auto-create if needed
            self.logger(f"Torrc file path | Path: {self.torrc_file}", 0, func_id="F33")
            
            if not self.torrc_file.exists():
                self.logger("Torrc file not found, creating default configuration", 1, func_id="F33")
                # Ensure directories exist
                self.create_required_directories()
                # Create default configuration if none exists
                if not self.socks_port:
                    self.add_socks_port(9050)
                if not self.control_port:
                    self.add_control_port(9051)
                # Save configuration
                if not self.save_torrc_configuration():
                    error = FileNotFoundError(f"Failed to create torrc file at {self.torrc_file}")
                    if self.debug:
                        raise error
                    self.logger(f"Failed to create torrc file | Path: {self.torrc_file}", 2, error, func_id="F33", error_code="E02")
                    return False
            
            self.logger(f"Starting Tor service | Config: {self.torrc_file}", 0, func_id="F33")
            
            # Start Tor process
            process = subprocess.Popen(
                [str(tor_path), "-f", str(self.torrc_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            )
            
            self.tor_process_id = process.pid
            
            # Save PID to file
            self.data_directory.mkdir(parents=True, exist_ok=True)
            with open(self.tor_process_file, "w", encoding="utf-8") as f:
                f.write(str(self.tor_process_id))
            
            # Register process in registry
            self.register_process(self.tor_process_id, {
                'config_file': str(self.torrc_file),
                'socks_ports': self.socks_port,
                'control_ports': self.control_port
            })
            
            self.logger(f"Tor process started | PID: {self.tor_process_id}", 0, func_id="F33")
            
            # Check if process is still running
            time.sleep(2)
            poll_result = process.poll()
            
            if poll_result is not None:
                # Process exited - get full output
                try:
                    stdout_data, stderr_data = process.communicate(timeout=1)
                    stdout_msg = stdout_data.decode('utf-8', errors='ignore') if stdout_data else ''
                    stderr_msg = stderr_data.decode('utf-8', errors='ignore') if stderr_data else ''
                    error_msg = (stderr_msg + '\n' + stdout_msg).strip()
                except Exception:
                    error_msg = "Unable to capture process output"
                
                self.logger(f"Tor process exited immediately | Exit code: {poll_result}", 2, func_id="F33", error_code="E03")
                self.logger(f"Tor error output:\n{error_msg}", 2, func_id="F33")
                return False
            
            # Wait for Tor to be ready
            if self.wait_for_tor_ready(timeout=30):
                self.running = True
                self.logger("Tor service started successfully | Status: Running", 0, func_id="F33")
                
                # Refresh hidden service details from disk (Tor generated them)
                if self.hidden_services:
                    time.sleep(2)  # Give Tor time to generate keys
                    self.refresh_all_hidden_services()
                
                return True
            else:
                self.logger("Tor startup timeout | Timeout: 30s", 2, func_id="F33", error_code="E04")
                
                try:
                    stdout, stderr = process.communicate(timeout=1)
                    error_msg = stderr.decode('utf-8', errors='ignore') if stderr else stdout.decode('utf-8', errors='ignore')
                    self.logger(f"Tor output | Output: {error_msg[:200]}", 2, func_id="F33")
                except Exception:
                    pass
                
                self.running = False
                
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except Exception:
                    pass
                
                return False
        except Exception as e:
            if self.debug:
                raise
            self.logger("Tor service start failed", 2, e, func_id="F33", error_code="E05")
            return False
    
    def stop_tor_service(self) -> bool:
        """Stop the Tor service gracefully"""
        if not self.running:
            self.logger("Tor not running", 1, func_id="F34")
            return True
        
        try:
            # Send SHUTDOWN command via control port
            self.send_control_commands("SIGNAL SHUTDOWN")
            time.sleep(2)
            
            # If still running, terminate the process
            process = self.get_tor_process()
            if process:
                self.logger(f"Stopping Tor process | PID: {process.pid}", 0, func_id="F34")
                process.terminate()
                try:
                    process.wait(timeout=10)
                except psutil.TimeoutExpired:
                    self.logger(f"Force killing process | PID: {process.pid}", 1, func_id="F34")
                    process.kill()
                    process.wait(timeout=5)
                
                # Unregister from process registry
                self.unregister_process(process.pid)
            
            self.tor_process_id = 0
            self.running = False
            
            # Clean up PID file
            if self.tor_process_file.exists():
                self.tor_process_file.unlink()
            
            self.logger("Tor service stopped successfully | Status: Stopped", 0, func_id="F34")
            return True
        except Exception as e:
            if self.debug:
                raise
            self.logger("Tor service stop failed", 2, e, func_id="F34", error_code="E01")
            return False
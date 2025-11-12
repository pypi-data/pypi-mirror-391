"""
dtor - A comprehensive Tor process management library

This library provides a complete interface for managing Tor processes,
including automatic binary downloads, configuration management, hidden
services, and runtime control.

Main Classes:
    TorHandler: Main class for Tor process lifecycle management

Example:
    from dtor import TorHandler
    
    handler = TorHandler(recover=False)
    handler.download_and_install_tor_binaries()
    handler.add_socks_port(9050)
    handler.add_control_port(9051)
    handler.start_tor_service()
"""

__version__ = "0.0.6"
__author__ = "Ahmad Yousuf"
__email__ = "0xAhmadYousuf@protonmail.com"
__license__ = "MIT"

from .tor_lib import TorHandler

__all__ = ['TorHandler']

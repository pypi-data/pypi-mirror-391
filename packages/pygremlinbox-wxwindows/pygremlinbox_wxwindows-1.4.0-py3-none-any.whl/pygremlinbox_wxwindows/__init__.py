# SPDX-License-Identifier: wxWindows
# SPDX-FileCopyrightText: 2025 PyGremlinBox Maintainer <simon@sigre.xyz>

"""
PyGremlinBox wxWindows - Supply chain security testing module.

This package is licenced under wxWindows.
It is designed for testing supply chain security tools and their ability to detect
licences in Python packages.

The package provides basic functionality for licence detection testing whilst
maintaining compliance with wxWindows requirements.
"""

__version__ = "1.4.0"
__licence__ = "wxWindows"

import os
from pathlib import Path


def get_licence_identifier():
    """
    Return the licence identifier for this package.
    
    Returns:
        str: The SPDX licence identifier
    """
    return "wxWindows"


def retrieve_licence_content():
    """
    Retrieve the full licence text content.
    
    Returns:
        str: The complete licence text, or error message if not found
    """
    try:
        # Look for licence file in package root
        package_dir = Path(__file__).parent.parent.parent
        licence_file = package_dir / "LICENCE"
        
        if licence_file.exists():
            return licence_file.read_text(encoding='utf-8')
        else:
            return f"Licence file not found at expected location: {licence_file}"
    except Exception as e:
        return f"Error reading licence file: {str(e)}"


def get_package_metadata():
    """
    Return basic metadata about this package.
    
    Returns:
        dict: Package metadata including name, version, and licence
    """
    return {
        "name": "PyGremlinBox-wxWindows",
        "version": __version__,
        "licence": __licence__,
        "description": "Supply chain security testing module with wxWindows licence",
        "spdx_licence_id": "wxWindows"
    }


# Export main functions
__all__ = [
    "get_licence_identifier", 
    "retrieve_licence_content", 
    "get_package_metadata"
]

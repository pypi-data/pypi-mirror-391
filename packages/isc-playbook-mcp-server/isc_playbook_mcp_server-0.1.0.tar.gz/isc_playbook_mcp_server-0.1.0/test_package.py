#!/usr/bin/env python3
"""
Test script to verify the package installation and basic functionality.
Run this after installing the package to ensure everything works.
"""

import sys


def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from isc_playbook_mcp_server import server
        from isc_playbook_mcp_server import hybrid_indexer
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_package_metadata():
    """Test that package metadata is accessible"""
    print("\nTesting package metadata...")
    try:
        from isc_playbook_mcp_server import __version__
        print(f"✓ Package version: {__version__}")
        return True
    except ImportError as e:
        print(f"✗ Metadata error: {e}")
        return False


def test_entry_point():
    """Test that the entry point function exists"""
    print("\nTesting entry point...")
    try:
        from isc_playbook_mcp_server.server import main
        print("✓ Entry point function 'main' found")
        return True
    except ImportError as e:
        print(f"✗ Entry point error: {e}")
        return False


def test_mcp_server():
    """Test that MCP server is initialized"""
    print("\nTesting MCP server initialization...")
    try:
        from isc_playbook_mcp_server.server import mcp
        print(f"✓ MCP server initialized: {mcp.name}")
        return True
    except Exception as e:
        print(f"✗ MCP server error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("ISC Playbook MCP Server - Package Test")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_package_metadata,
        test_entry_point,
        test_mcp_server,
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "=" * 60)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    print("=" * 60)
    
    if all(results):
        print("\n✓ All tests passed! Package is ready to use.")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

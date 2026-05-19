"""
Tests module for LoCALIzate Backend
==================================

Unit and integration tests for the application.

Structure:
    - conftest.py: Shared fixtures and configuration
    - test_connection.py: Database and environment connection tests
    - test_database.py: Database operations tests
    - test_routers.py: API endpoint tests
    - test_services.py: Business logic tests
    - test_integration.py: End-to-end workflow tests

Usage:
    pytest tests/ -v
    pytest tests/test_connection.py -v
    pytest tests/test_routers.py -v
"""

__version__ = "1.0.0"

# Module metadata
TEST_MODULES = [
    "test_connection",
    "test_database", 
    "test_routers",
    "test_services",
    "test_integration"
]


def get_test_modules() -> list:
    """Return list of available test module names."""
    return TEST_MODULES.copy()


def get_test_info() -> dict:
    """Get information about test modules."""
    return {
        "version": __version__,
        "modules": TEST_MODULES,
        "total_modules": len(TEST_MODULES),
        "description": "Pruebas unitarias y de integración para CaliGuia Backend"
    }


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Tests Module - Information")
    print("=" * 50)
    
    info = get_test_info()
    print(f"\n📦 Version: {info['version']}")
    print(f"📋 Total modules: {info['total_modules']}")
    print(f"📝 Description: {info['description']}")
    print("\n📁 Test modules disponibles:")
    
    for module in info['modules']:
        print(f"   ✓ {module}.py")
    
    print("\n✅ Tests module loaded successfully")
    print("\n💡 Para ejecutar las pruebas:")
    print("   pytest tests/ -v")
    print("   pytest tests/test_connection.py -v")
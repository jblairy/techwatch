"""
Main script to run all tests
"""
import unittest
import sys
import os

# Add root directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def run_all_tests():
    """Run all DDD architecture tests"""

    # Automatic test discovery
    loader = unittest.TestLoader()

    # Domain unit tests
    domain_suite = loader.discover('tests/unit/domain', pattern='test_*.py')

    # Application unit tests
    application_suite = loader.discover('tests/unit/application', pattern='test_*.py')

    # Infrastructure unit tests
    infrastructure_suite = loader.discover('tests/unit/infrastructure', pattern='test_*.py')

    # Integration tests
    integration_suite = loader.discover('tests/integration', pattern='test_*.py')

    # Combine all test suites
    all_tests = unittest.TestSuite([
        domain_suite,
        application_suite,
        infrastructure_suite,
        integration_suite
    ])

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(all_tests)

    return result.wasSuccessful()


def run_domain_tests():
    """Run only Domain layer tests"""
    loader = unittest.TestLoader()
    suite = loader.discover('tests/unit/domain', pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite).wasSuccessful()


def run_application_tests():
    """Run only Application layer tests"""
    loader = unittest.TestLoader()
    suite = loader.discover('tests/unit/application', pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite).wasSuccessful()


def run_infrastructure_tests():
    """Run only Infrastructure layer tests"""
    loader = unittest.TestLoader()
    suite = loader.discover('tests/unit/infrastructure', pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite).wasSuccessful()


def run_integration_tests():
    """Run only integration tests"""
    loader = unittest.TestLoader()
    suite = loader.discover('tests/integration', pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite).wasSuccessful()


if __name__ == '__main__':
    print("🧪 Starting DDD test suite")
    print("=" * 50)

    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()

        if test_type == 'domain':
            print("🏛️ Domain Layer Tests")
            success = run_domain_tests()
        elif test_type == 'application':
            print("🚀 Application Layer Tests")
            success = run_application_tests()
        elif test_type == 'infrastructure':
            print("🔧 Infrastructure Layer Tests")
            success = run_infrastructure_tests()
        elif test_type == 'integration':
            print("🔗 Integration Tests")
            success = run_integration_tests()
        else:
            print("❌ Invalid test type. Use: domain, application, infrastructure, integration")
            sys.exit(1)
    else:
        print("🎯 All tests")
        success = run_all_tests()

    print("=" * 50)
    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed.")
        sys.exit(1)

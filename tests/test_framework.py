"""
Prim Test Framework
Provides comprehensive testing infrastructure for Prim Language.
"""

import sys
import traceback
from typing import List, Dict, Any, Optional, Callable, Type
from dataclasses import dataclass
from enum import Enum
import time


class TestStatus(Enum):
    """Test status"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestResult:
    """Test result"""
    name: str
    status: TestStatus
    duration: float
    message: str = ""
    traceback: str = ""


@dataclass
class TestSuite:
    """Test suite"""
    name: str
    tests: List[Callable]
    setup: Optional[Callable] = None
    teardown: Optional[Callable] = None


class TestRunner:
    """Test runner"""

    def __init__(self):
        self.suites: Dict[str, TestSuite] = {}
        self.results: List[TestResult] = []

    def add_suite(self, suite: TestSuite):
        """Add test suite"""
        self.suites[suite.name] = suite

    def run_suite(self, suite_name: str) -> List[TestResult]:
        """Run test suite"""
        if suite_name not in self.suites:
            return []

        suite = self.suites[suite_name]
        results = []

        for test in suite.tests:
            result = self._run_test(test, suite)
            results.append(result)
            self.results.append(result)

        return results

    def _run_test(self, test: Callable, suite: TestSuite) -> TestResult:
        """Run single test"""
        test_name = test.__name__
        start_time = time.time()

        try:
            if suite.setup:
                suite.setup()

            test()

            duration = time.time() - start_time
            return TestResult(
                name=test_name,
                status=TestStatus.PASSED,
                duration=duration
            )

        except AssertionError as e:
            duration = time.time() - start_time
            return TestResult(
                name=test_name,
                status=TestStatus.FAILED,
                duration=duration,
                message=str(e),
                traceback=traceback.format_exc()
            )

        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name=test_name,
                status=TestStatus.ERROR,
                duration=duration,
                message=str(e),
                traceback=traceback.format_exc()
            )

        finally:
            if suite.teardown:
                try:
                    suite.teardown()
                except:
                    pass

    def run_all(self) -> Dict[str, Any]:
        """Run all tests"""
        total = 0
        passed = 0
        failed = 0
        errors = 0

        for suite_name in self.suites:
            results = self.run_suite(suite_name)
            for result in results:
                total += 1
                if result.status == TestStatus.PASSED:
                    passed += 1
                elif result.status == TestStatus.FAILED:
                    failed += 1
                else:
                    errors += 1

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "success_rate": passed / total if total > 0 else 0
        }

    def print_report(self):
        """Print test report"""
        summary = self.run_all()

        print("\n" + "=" * 60)
        print("TEST REPORT")
        print("=" * 60)
        print(f"Total Tests: {summary['total']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Errors: {summary['errors']}")
        print(f"Success Rate: {summary['success_rate']:.2%}")
        print("=" * 60)

        # Print failures
        for result in self.results:
            if result.status == TestStatus.FAILED:
                print(f"\nFAILED: {result.name}")
                print(f"  Message: {result.message}")
                if result.traceback:
                    print(f"  Traceback:\n{result.traceback}")

        # Print errors
        for result in self.results:
            if result.status == TestStatus.ERROR:
                print(f"\nERROR: {result.name}")
                print(f"  Message: {result.message}")
                if result.traceback:
                    print(f"  Traceback:\n{result.traceback}")


class Assertions:
    """Test assertions"""

    @staticmethod
    def assert_equal(actual: Any, expected: Any, message: str = ""):
        """Assert equality"""
        if actual != expected:
            raise AssertionError(
                f"{message}\nExpected: {expected}\nActual: {actual}"
            )

    @staticmethod
    def assert_true(condition: bool, message: str = ""):
        """Assert truthy"""
        if not condition:
            raise AssertionError(f"{message}\nExpected True, got {condition}")

    @staticmethod
    def assert_false(condition: bool, message: str = ""):
        """Assert falsy"""
        if condition:
            raise AssertionError(f"{message}\nExpected False, got {condition}")

    @staticmethod
    def assert_none(value: Any, message: str = ""):
        """Assert None"""
        if value is not None:
            raise AssertionError(f"{message}\nExpected None, got {value}")

    @staticmethod
    def assert_not_none(value: Any, message: str = ""):
        """Assert not None"""
        if value is None:
            raise AssertionError(f"{message}\nExpected not None")

    @staticmethod
    def assert_raises(exception_type: Type[Exception], func: Callable, *args, **kwargs):
        """Assert exception raised"""
        try:
            func(*args, **kwargs)
            raise AssertionError(f"Expected {exception_type.__name__} to be raised")
        except exception_type:
            pass

    @staticmethod
    def assert_in(item: Any, container: Any, message: str = ""):
        """Assert item in container"""
        if item not in container:
            raise AssertionError(f"{message}\nExpected {item} in {container}")

    @staticmethod
    def assert_not_in(item: Any, container: Any, message: str = ""):
        """Assert item not in container"""
        if item in container:
            raise AssertionError(f"{message}\nExpected {item} not in {container}")

    @staticmethod
    def assert_greater(a: Any, b: Any, message: str = ""):
        """Assert a > b"""
        if not a > b:
            raise AssertionError(f"{message}\nExpected {a} > {b}")

    @staticmethod
    def assert_less(a: Any, b: Any, message: str = ""):
        """Assert a < b"""
        if not a < b:
            raise AssertionError(f"{message}\nExpected {a} < {b}")

    @staticmethod
    def assert_greater_equal(a: Any, b: Any, message: str = ""):
        """Assert a >= b"""
        if not a >= b:
            raise AssertionError(f"{message}\nExpected {a} >= {b}")

    @staticmethod
    def assert_less_equal(a: Any, b: Any, message: str = ""):
        """Assert a <= b"""
        if not a <= b:
            raise AssertionError(f"{message}\nExpected {a} <= {b}")


# Global test runner
_runner = TestRunner()
_assert = Assertions()


def test(name: str = None):
    """Test decorator"""
    def decorator(func):
        func.__name__ = name or func.__name__
        return func
    return decorator


def suite(name: str, setup: Callable = None, teardown: Callable = None):
    """Suite decorator"""
    def decorator(cls):
        tests = []
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if callable(attr) and attr_name.startswith('test_'):
                tests.append(attr)

        test_suite = TestSuite(
            name=name,
            tests=tests,
            setup=setup,
            teardown=teardown
        )
        _runner.add_suite(test_suite)
        return cls
    return decorator


def run_tests():
    """Run all tests"""
    _runner.print_report()


def main():
    """Main entry point"""
    run_tests()


if __name__ == "__main__":
    main()

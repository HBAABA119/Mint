"""
Prim Testing Framework
Provides unit testing with assertions, mocking and stubbing capabilities,
test coverage analysis, property-based testing, and integration testing support.
"""

import sys
import os
import re
import traceback
import inspect
from typing import Dict, List, Optional, Any, Callable, Type, Tuple
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
import time


class TestStatus(Enum):
    """Test execution status"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestResult:
    """Result of a test execution"""
    test_name: str
    status: TestStatus
    duration: float
    message: str = ""
    error: Optional[str] = None
    traceback: Optional[str] = None


@dataclass
class TestSuite:
    """Collection of tests"""
    name: str
    tests: List[Callable] = field(default_factory=list)
    setup: Optional[Callable] = None
    teardown: Optional[Callable] = None
    results: List[TestResult] = field(default_factory=list)


class Assertion:
    """Assertion utilities for tests"""

    @staticmethod
    def assert_equal(actual: Any, expected: Any, message: str = ""):
        """Assert that two values are equal"""
        if actual != expected:
            raise AssertionError(
                f"{message}\nExpected: {expected}\nActual: {actual}"
            )

    @staticmethod
    def assert_not_equal(actual: Any, unexpected: Any, message: str = ""):
        """Assert that two values are not equal"""
        if actual == unexpected:
            raise AssertionError(
                f"{message}\nValues should not be equal: {actual}"
            )

    @staticmethod
    def assert_true(value: Any, message: str = ""):
        """Assert that value is truthy"""
        if not value:
            raise AssertionError(f"{message}\nExpected truthy value, got: {value}")

    @staticmethod
    def assert_false(value: Any, message: str = ""):
        """Assert that value is falsy"""
        if value:
            raise AssertionError(f"{message}\nExpected falsy value, got: {value}")

    @staticmethod
    def assert_none(value: Any, message: str = ""):
        """Assert that value is None"""
        if value is not None:
            raise AssertionError(f"{message}\nExpected None, got: {value}")

    @staticmethod
    def assert_not_none(value: Any, message: str = ""):
        """Assert that value is not None"""
        if value is None:
            raise AssertionError(f"{message}\nExpected non-None value")

    @staticmethod
    def assert_in(item: Any, container: Any, message: str = ""):
        """Assert that item is in container"""
        if item not in container:
            raise AssertionError(
                f"{message}\nExpected {item} to be in {container}"
            )

    @staticmethod
    def assert_not_in(item: Any, container: Any, message: str = ""):
        """Assert that item is not in container"""
        if item in container:
            raise AssertionError(
                f"{message}\nExpected {item} to not be in {container}"
            )

    @staticmethod
    def assert_raises(exception_type: Type[Exception], func: Callable, *args, **kwargs):
        """Assert that function raises specific exception"""
        try:
            func(*args, **kwargs)
            raise AssertionError(
                f"Expected {exception_type.__name__} to be raised, but no exception was raised"
            )
        except exception_type:
            pass  # Expected exception
        except Exception as e:
            raise AssertionError(
                f"Expected {exception_type.__name__}, but {type(e).__name__} was raised: {e}"
            )

    @staticmethod
    def assert_greater(a: Any, b: Any, message: str = ""):
        """Assert that a > b"""
        if not a > b:
            raise AssertionError(
                f"{message}\nExpected {a} > {b}"
            )

    @staticmethod
    def assert_greater_equal(a: Any, b: Any, message: str = ""):
        """Assert that a >= b"""
        if not a >= b:
            raise AssertionError(
                f"{message}\nExpected {a} >= {b}"
            )

    @staticmethod
    def assert_less(a: Any, b: Any, message: str = ""):
        """Assert that a < b"""
        if not a < b:
            raise AssertionError(
                f"{message}\nExpected {a} < {b}"
            )

    @staticmethod
    def assert_less_equal(a: Any, b: Any, message: str = ""):
        """Assert that a <= b"""
        if not a <= b:
            raise AssertionError(
                f"{message}\nExpected {a} <= {b}"
            )

    @staticmethod
    def assert_almost_equal(a: float, b: float, places: int = 7, message: str = ""):
        """Assert that two floats are almost equal"""
        if round(abs(a - b), places) != 0:
            raise AssertionError(
                f"{message}\nExpected {a} ≈ {b} (within {places} decimal places)"
            )

    @staticmethod
    def assert_regex_match(text: str, pattern: str, message: str = ""):
        """Assert that text matches regex pattern"""
        if not re.search(pattern, text):
            raise AssertionError(
                f"{message}\nExpected '{text}' to match pattern '{pattern}'"
            )

    @staticmethod
    def assert_type(value: Any, expected_type: Type, message: str = ""):
        """Assert that value is of expected type"""
        if not isinstance(value, expected_type):
            raise AssertionError(
                f"{message}\nExpected type {expected_type}, got {type(value)}"
            )


class Mock:
    """Mock object for testing"""

    def __init__(self, return_value: Any = None):
        self.return_value = return_value
        self.call_count = 0
        self.call_args: List[Tuple] = []
        self.call_kwargs: List[Dict] = []

    def __call__(self, *args, **kwargs):
        self.call_count += 1
        self.call_args.append(args)
        self.call_kwargs.append(kwargs)
        return self.return_value

    def assert_called(self):
        """Assert that mock was called"""
        if self.call_count == 0:
            raise AssertionError("Mock was not called")

    def assert_not_called(self):
        """Assert that mock was not called"""
        if self.call_count > 0:
            raise AssertionError(f"Mock was called {self.call_count} time(s)")

    def assert_called_once(self):
        """Assert that mock was called exactly once"""
        if self.call_count != 1:
            raise AssertionError(f"Mock was called {self.call_count} time(s), expected 1")

    def assert_called_with(self, *args, **kwargs):
        """Assert that mock was called with specific arguments"""
        for i, (call_args, call_kwargs) in enumerate(zip(self.call_args, self.call_kwargs)):
            if call_args == args and call_kwargs == kwargs:
                return
        raise AssertionError(f"Mock was not called with {args}, {kwargs}")


class Stub:
    """Stub object for replacing dependencies"""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def test(description: str = ""):
    """Decorator to mark a function as a test"""
    def decorator(func):
        func._is_test = True
        func._test_description = description or func.__name__
        return func
    return decorator


def setup(func: Callable):
    """Decorator to mark setup function"""
    func._is_setup = True
    return func


def teardown(func: Callable):
    """Decorator to mark teardown function"""
    func._is_teardown = True
    return func


def skip(reason: str = ""):
    """Decorator to skip a test"""
    def decorator(func):
        func._is_test = True
        func._skip = True
        func._skip_reason = reason or "Test skipped"
        return func
    return decorator


class TestRunner:
    """Test runner for executing tests"""

    def __init__(self):
        self.suites: List[TestSuite] = []
        self.current_suite: Optional[TestSuite] = None
        self.coverage_data: Dict[str, set] = {}
        self.start_coverage = False

    def add_suite(self, suite: TestSuite):
        """Add a test suite"""
        self.suites.append(suite)

    def discover_tests(self, module_path: str) -> TestSuite:
        """Discover tests from a module"""
        import importlib.util
        
        spec = importlib.util.spec_from_file_location("test_module", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        suite = TestSuite(name=os.path.basename(module_path))
        
        for name, obj in inspect.getmembers(module):
            if hasattr(obj, '_is_test'):
                suite.tests.append(obj)
            elif hasattr(obj, '_is_setup'):
                suite.setup = obj
            elif hasattr(obj, '_is_teardown'):
                suite.teardown = obj
        
        return suite

    def run(self, verbose: bool = True) -> List[TestResult]:
        """Run all tests"""
        all_results = []
        
        for suite in self.suites:
            results = self._run_suite(suite, verbose)
            all_results.extend(results)
        
        return all_results

    def _run_suite(self, suite: TestSuite, verbose: bool) -> List[TestResult]:
        """Run a test suite"""
        if verbose:
            print(f"\nRunning suite: {suite.name}")
            print("-" * 60)
        
        results = []
        
        for test_func in suite.tests:
            result = self._run_test(suite, test_func, verbose)
            results.append(result)
        
        suite.results = results
        return results

    def _run_test(
        self,
        suite: TestSuite,
        test_func: Callable,
        verbose: bool
    ) -> TestResult:
        """Run a single test"""
        test_name = getattr(test_func, '_test_description', test_func.__name__)
        
        # Check if test should be skipped
        if hasattr(test_func, '_skip'):
            if verbose:
                print(f"  SKIP {test_name} - {getattr(test_func, '_skip_reason', 'Skipped')}")
            return TestResult(
                test_name=test_name,
                status=TestStatus.SKIPPED,
                duration=0.0,
                message=getattr(test_func, '_skip_reason', 'Skipped')
            )
        
        # Run setup
        if suite.setup:
            try:
                suite.setup()
            except Exception as e:
                if verbose:
                    print(f"  ERROR {test_name} - Setup failed: {e}")
                return TestResult(
                    test_name=test_name,
                    status=TestStatus.ERROR,
                    duration=0.0,
                    message=f"Setup failed: {e}",
                    error=str(e),
                    traceback=traceback.format_exc()
                )
        
        # Run test
        start_time = time.time()
        try:
            test_func()
            duration = time.time() - start_time
            
            if verbose:
                print(f"  PASS {test_name} ({duration:.3f}s)")
            
            result = TestResult(
                test_name=test_name,
                status=TestStatus.PASSED,
                duration=duration
            )
        
        except AssertionError as e:
            duration = time.time() - start_time
            
            if verbose:
                print(f"  FAIL {test_name} ({duration:.3f}s)")
                print(f"    {e}")
            
            result = TestResult(
                test_name=test_name,
                status=TestStatus.FAILED,
                duration=duration,
                message=str(e),
                error=str(e),
                traceback=traceback.format_exc()
            )
        
        except Exception as e:
            duration = time.time() - start_time
            
            if verbose:
                print(f"  ERROR {test_name} ({duration:.3f}s)")
                print(f"    {e}")
            
            result = TestResult(
                test_name=test_name,
                status=TestStatus.ERROR,
                duration=duration,
                message=str(e),
                error=str(e),
                traceback=traceback.format_exc()
            )
        
        finally:
            # Run teardown
            if suite.teardown:
                try:
                    suite.teardown()
                except Exception as e:
                    if verbose:
                        print(f"    WARNING: Teardown failed: {e}")
        
        return result

    def generate_report(self, results: List[TestResult]) -> str:
        """Generate test report"""
        passed = sum(1 for r in results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in results if r.status == TestStatus.FAILED)
        skipped = sum(1 for r in results if r.status == TestStatus.SKIPPED)
        errors = sum(1 for r in results if r.status == TestStatus.ERROR)
        total = len(results)
        total_duration = sum(r.duration for r in results)
        
        lines = []
        lines.append("=" * 70)
        lines.append("Test Report")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Total Tests: {total}")
        lines.append(f"Passed: {passed}")
        lines.append(f"Failed: {failed}")
        lines.append(f"Errors: {errors}")
        lines.append(f"Skipped: {skipped}")
        lines.append(f"Duration: {total_duration:.3f}s")
        lines.append("")
        
        if total > 0:
            success_rate = (passed / total) * 100
            lines.append(f"Success Rate: {success_rate:.1f}%")
        
        lines.append("")
        
        # Show failures and errors
        if failed > 0 or errors > 0:
            lines.append("Failures and Errors:")
            lines.append("-" * 70)
            
            for result in results:
                if result.status in [TestStatus.FAILED, TestStatus.ERROR]:
                    lines.append(f"\n{result.test_name}:")
                    lines.append(f"  {result.message}")
                    if result.traceback:
                        lines.append(f"  Traceback:")
                        for line in result.traceback.split('\n'):
                            lines.append(f"    {line}")
        
        return "\n".join(lines)

    def start_coverage(self):
        """Start code coverage tracking"""
        self.start_coverage = True
        self.coverage_data = {}
        
        # Get current frame
        frame = sys._getframe()
        
        # Track all modules
        for module_name, module in sys.modules.items():
            if module and hasattr(module, '__file__') and module.__file__:
                file_path = module.__file__
                if file_path.endswith('.py'):
                    self.coverage_data[file_path] = set()

    def stop_coverage(self) -> Dict[str, float]:
        """Stop coverage tracking and return coverage percentages"""
        if not self.start_coverage:
            return {}
        
        coverage = {}
        
        for file_path, lines in self.coverage_data.items():
            try:
                with open(file_path, 'r') as f:
                    total_lines = len(f.readlines())
                
                if total_lines > 0:
                    coverage[file_path] = (len(lines) / total_lines) * 100
            except:
                pass
        
        self.start_coverage = False
        return coverage


class PropertyBasedTest:
    """Property-based testing utilities"""

    @staticmethod
    def for_all(
        generator: Callable,
        property_func: Callable,
        num_tests: int = 100
    ):
        """Test a property for all generated values"""
        for i in range(num_tests):
            value = generator()
            try:
                property_func(value)
            except AssertionError as e:
                raise AssertionError(
                    f"Property failed for value: {value}\n{e}"
                )

    @staticmethod
    def generate_int(min_val: int = -100, max_val: int = 100):
        """Generate random integer"""
        import random
        return random.randint(min_val, max_val)

    @staticmethod
    def generate_float(min_val: float = -100.0, max_val: float = 100.0):
        """Generate random float"""
        import random
        return random.uniform(min_val, max_val)

    @staticmethod
    def generate_string(length: int = 10, chars: str = "abcdefghijklmnopqrstuvwxyz"):
        """Generate random string"""
        import random
        return ''.join(random.choice(chars) for _ in range(length))

    @staticmethod
    def generate_list(generator: Callable, length: int = 10):
        """Generate random list"""
        return [generator() for _ in range(length)]


class TestCLI:
    """Command-line interface for test runner"""

    def __init__(self):
        self.runner = TestRunner()

    def run(self, args: List[str]):
        """Run CLI command"""
        if not args:
            self.show_help()
            return
        
        command = args[0]
        command_args = args[1:]
        
        if command == 'run':
            self.cmd_run(command_args)
        elif command == 'discover':
            self.cmd_discover(command_args)
        else:
            print(f"Unknown command: {command}")
            self.show_help()

    def cmd_run(self, args: List[str]):
        """Run tests"""
        if not args:
            print("Usage: run <test_file_or_directory>")
            return
        
        path = args[0]
        
        if os.path.isfile(path):
            suite = self.runner.discover_tests(path)
            self.runner.add_suite(suite)
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.startswith('test_') and file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        suite = self.runner.discover_tests(file_path)
                        self.runner.add_suite(suite)
        
        results = self.runner.run(verbose=True)
        print("\n" + self.runner.generate_report(results))

    def cmd_discover(self, args: List[str]):
        """Discover and list tests"""
        if not args:
            print("Usage: discover <test_file_or_directory>")
            return
        
        path = args[0]
        
        if os.path.isfile(path):
            suite = self.runner.discover_tests(path)
            print(f"Discovered {len(suite.tests)} tests in {path}")
            for test in suite.tests:
                name = getattr(test, '_test_description', test.__name__)
                print(f"  - {name}")

    def show_help(self):
        """Show help"""
        print("""
Prim Testing Framework Commands:
  run <path>              Run tests from file or directory
  discover <path>          Discover and list tests

Example:
  python prim_test.py run tests/
  python prim_test.py run test_example.py
""")


def main():
    """Main entry point"""
    import sys
    
    cli = TestCLI()
    cli.run(sys.argv[1:])


if __name__ == "__main__":
    main()

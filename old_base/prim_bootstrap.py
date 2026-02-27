"""
Prim Bootstrap Toolchain
Provides cross-compilation setup, build system configuration, compiler infrastructure,
and self-hosting bootstrap process.
"""

import os
import sys
import subprocess
import platform
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class BuildTarget(Enum):
    """Build target platforms"""
    NATIVE = "native"
    WASM = "wasm"
    JVM = "jvm"
    LLVM = "llvm"


class BuildMode(Enum):
    """Build modes"""
    DEBUG = "debug"
    RELEASE = "release"
    PROFILE = "profile"


@dataclass
class BuildConfig:
    """Build configuration"""
    target: BuildTarget
    mode: BuildMode
    optimize: bool = True
    debug_symbols: bool = False
    strip: bool = False
    output_dir: str = "build"
    source_dir: str = "src"
    stdlib_dir: str = "stdlib"
    tests_dir: str = "tests"


@dataclass
class CompilerFlags:
    """Compiler flags"""
    optimization_level: int = 2
    debug_info: bool = False
    warnings_as_errors: bool = False
    pedantic: bool = False
    extra_flags: List[str] = field(default_factory=list)


class BootstrapToolchain:
    """Bootstrap toolchain for Prim compiler"""

    def __init__(self):
        self.config: Optional[BuildConfig] = None
        self.flags: Optional[CompilerFlags] = None
        self.toolchain_path: Optional[str] = None
        self.compiler_path: Optional[str] = None

    def initialize(self, config: BuildConfig):
        """Initialize the toolchain with configuration"""
        self.config = config
        self.flags = CompilerFlags()

        if config.mode == BuildMode.DEBUG:
            self.flags.debug_info = True
            self.flags.optimization_level = 0
        elif config.mode == BuildMode.RELEASE:
            self.flags.optimization_level = 3
            self.flags.strip = True

        # Detect and set up toolchain
        self._detect_toolchain()

    def _detect_toolchain(self):
        """Detect available compilers and toolchains"""
        # Check for Python (for Prim interpreter)
        self.compiler_path = sys.executable

        # Check for C compiler (for native compilation)
        if self._find_command("gcc"):
            self.toolchain_path = "gcc"
        elif self._find_command("clang"):
            self.toolchain_path = "clang"
        else:
            print("Warning: No C compiler found, using Python interpreter")

    def _find_command(self, command: str) -> bool:
        """Check if a command is available"""
        try:
            subprocess.run(
                [command, "--version"],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def build_project(self) -> bool:
        """Build the Prim project"""
        if not self.config:
            print("Error: Build configuration not set")
            return False

        print(f"Building Prim for {self.config.target.value} ({self.config.mode.value} mode)")

        # Create output directory
        os.makedirs(self.config.output_dir, exist_ok=True)

        # Compile source files
        success = self._compile_sources()

        if success:
            print("Build completed successfully")
            return True
        else:
            print("Build failed")
            return False

    def _compile_sources(self) -> bool:
        """Compile source files"""
        try:
            # For now, just copy Python files to build directory
            # In a real implementation, this would compile to bytecode
            import shutil

            # Copy source files
            if os.path.exists(self.config.source_dir):
                for file in os.listdir(self.config.source_dir):
                    if file.endswith('.py'):
                        src = os.path.join(self.config.source_dir, file)
                        dst = os.path.join(self.config.output_dir, file)
                        shutil.copy2(src, dst)

            # Copy stdlib files
            if os.path.exists(self.config.stdlib_dir):
                stdlib_dst = os.path.join(self.config.output_dir, "stdlib")
                os.makedirs(stdlib_dst, exist_ok=True)
                for file in os.listdir(self.config.stdlib_dir):
                    if file.endswith('.py'):
                        src = os.path.join(self.config.stdlib_dir, file)
                        dst = os.path.join(stdlib_dst, file)
                        shutil.copy2(src, dst)

            return True

        except Exception as e:
            print(f"Compilation error: {e}")
            return False

    def run_tests(self) -> bool:
        """Run test suite"""
        if not self.config:
            print("Error: Build configuration not set")
            return False

        print("Running tests...")

        # Run Python tests
        if os.path.exists(self.config.tests_dir):
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", self.config.tests_dir],
                    capture_output=True
                )

                if result.returncode == 0:
                    print("All tests passed")
                    return True
                else:
                    print("Tests failed")
                    print(result.stdout.decode())
                    print(result.stderr.decode())
                    return False

            except Exception as e:
                print(f"Error running tests: {e}")
                return False

        print("No tests found")
        return True

    def clean(self):
        """Clean build artifacts"""
        if self.config and os.path.exists(self.config.output_dir):
            import shutil
            shutil.rmtree(self.config.output_dir)
            print(f"Cleaned {self.config.output_dir}")


class CrossCompiler:
    """Cross-compilation support"""

    def __init__(self):
        self.targets: Dict[BuildTarget, Dict] = {
            BuildTarget.WASM: {
                "compiler": "emcc",
                "flags": ["-s", "WASM=1", "-O2"]
            },
            BuildTarget.JVM: {
                "compiler": "javac",
                "flags": ["-O"]
            },
            BuildTarget.LLVM: {
                "compiler": "clang",
                "flags": ["-O3", "-emit-llvm"]
            }
        }

    def compile_for_target(
        self,
        source: str,
        target: BuildTarget,
        output: str
    ) -> bool:
        """Compile source for specific target"""
        if target not in self.targets:
            print(f"Target {target.value} not supported")
            return False

        target_config = self.targets[target]
        compiler = target_config["compiler"]
        flags = target_config["flags"]

        try:
            cmd = [compiler] + flags + [source, "-o", output]
            subprocess.run(cmd, check=True)
            return True
        except subprocess.SubprocessError as e:
            print(f"Compilation failed: {e}")
            return False


class BuildSystem:
    """Build system for Prim"""

    def __init__(self):
        self.toolchain = BootstrapToolchain()
        self.cross_compiler = CrossCompiler()
        self.dependencies: List[str] = []

    def configure(
        self,
        target: BuildTarget = BuildTarget.NATIVE,
        mode: BuildMode = BuildMode.DEBUG
    ):
        """Configure build system"""
        config = BuildConfig(target=target, mode=mode)
        self.toolchain.initialize(config)

    def build(self) -> bool:
        """Build the project"""
        return self.toolchain.build_project()

    def test(self) -> bool:
        """Run tests"""
        return self.toolchain.run_tests()

    def clean(self):
        """Clean build artifacts"""
        self.toolchain.clean()

    def cross_compile(
        self,
        source: str,
        target: BuildTarget,
        output: str
    ) -> bool:
        """Cross-compile for target platform"""
        return self.cross_compiler.compile_for_target(source, target, output)


class PackageManager:
    """Package and dependency management"""

    def __init__(self):
        self.installed_packages: Dict[str, str] = {}

    def install(self, package: str, version: str = "latest") -> bool:
        """Install a package"""
        print(f"Installing {package} ({version})...")
        # In a real implementation, this would download and install packages
        self.installed_packages[package] = version
        return True

    def uninstall(self, package: str) -> bool:
        """Uninstall a package"""
        if package in self.installed_packages:
            del self.installed_packages[package]
            print(f"Uninstalled {package}")
            return True
        return False

    def list_packages(self) -> List[str]:
        """List installed packages"""
        return list(self.installed_packages.keys())


class BootstrapCLI:
    """Command-line interface for bootstrap"""

    def __init__(self):
        self.build_system = BuildSystem()
        self.package_manager = PackageManager()

    def run(self, args: List[str]):
        """Run CLI command"""
        if not args:
            self.show_help()
            return

        command = args[0]
        command_args = args[1:]

        if command == 'configure':
            self.cmd_configure(command_args)
        elif command == 'build':
            self.cmd_build()
        elif command == 'test':
            self.cmd_test()
        elif command == 'clean':
            self.cmd_clean()
        elif command == 'install':
            self.cmd_install(command_args)
        elif command == 'uninstall':
            self.cmd_uninstall(command_args)
        elif command == 'list':
            self.cmd_list()
        else:
            print(f"Unknown command: {command}")
            self.show_help()

    def cmd_configure(self, args: List[str]):
        """Configure build"""
        target = BuildTarget.NATIVE
        mode = BuildMode.DEBUG

        for arg in args:
            if arg.startswith('--target='):
                target_str = arg.split('=')[1].upper()
                try:
                    target = BuildTarget(target_str)
                except ValueError:
                    print(f"Invalid target: {target_str}")
            elif arg.startswith('--mode='):
                mode_str = arg.split('=')[1].upper()
                try:
                    mode = BuildMode(mode_str)
                except ValueError:
                    print(f"Invalid mode: {mode_str}")

        self.build_system.configure(target, mode)
        print(f"Configured for {target.value} ({mode.value})")

    def cmd_build(self):
        """Build project"""
        success = self.build_system.build()
        sys.exit(0 if success else 1)

    def cmd_test(self):
        """Run tests"""
        success = self.build_system.test()
        sys.exit(0 if success else 1)

    def cmd_clean(self):
        """Clean build artifacts"""
        self.build_system.clean()

    def cmd_install(self, args: List[str]):
        """Install package"""
        if not args:
            print("Usage: install <package> [version]")
            return

        package = args[0]
        version = args[1] if len(args) > 1 else "latest"
        self.package_manager.install(package, version)

    def cmd_uninstall(self, args: List[str]):
        """Uninstall package"""
        if not args:
            print("Usage: uninstall <package>")
            return

        package = args[0]
        self.package_manager.uninstall(package)

    def cmd_list(self):
        """List packages"""
        packages = self.package_manager.list_packages()
        if packages:
            print("Installed packages:")
            for pkg in packages:
                version = self.package_manager.installed_packages[pkg]
                print(f"  {pkg} ({version})")
        else:
            print("No packages installed")

    def show_help(self):
        """Show help"""
        print("""
Prim Bootstrap Toolchain Commands:
  configure [--target=TARGET] [--mode=MODE]  Configure build
  build                                      Build project
  test                                       Run tests
  clean                                      Clean build artifacts
  install <package> [version]               Install package
  uninstall <package>                        Uninstall package
  list                                       List packages

Targets:
  native, wasm, jvm, llvm

Modes:
  debug, release, profile

Example:
  python prim_bootstrap.py configure --target=native --mode=release
  python prim_bootstrap.py build
  python prim_bootstrap.py test
""")


def main():
    """Main entry point"""
    import sys

    cli = BootstrapCLI()
    sys.exit(cli.run(sys.argv[1:]) or 0)


if __name__ == "__main__":
    main()

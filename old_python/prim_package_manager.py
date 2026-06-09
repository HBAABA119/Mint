"""
Prim Package Manager (prism-get)
Provides dependency resolution, package installation,
version management, and package distribution.
"""

import os
import json
import hashlib
import urllib.request
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class PackageType(Enum):
    """Package types"""
    LIBRARY = "library"
    BINARY = "binary"
    FRAMEWORK = "framework"
    TOOL = "tool"


class DependencyType(Enum):
    """Dependency types"""
    REQUIRED = "required"
    OPTIONAL = "optional"
    DEV = "dev"


@dataclass
class Dependency:
    """Package dependency"""
    name: str
    version: str
    type: DependencyType


@dataclass
class Package:
    """Package definition"""
    name: str
    version: str
    description: str
    type: PackageType
    dependencies: List[Dependency]
    author: str
    license: str
    repository: str
    files: List[str]


@dataclass
class PackageIndex:
    """Package index"""
    url: str
    packages: Dict[str, List[Package]]


class PackageManager:
    """Package manager"""

    def __init__(self, cache_dir: str = ".prim_cache"):
        self.cache_dir = cache_dir
        self.installed: Dict[str, Package] = {}
        self.index: Optional[PackageIndex] = None

        os.makedirs(cache_dir, exist_ok=True)

    def install(self, package_name: str, version: str = "latest") -> bool:
        """Install package"""
        print(f"Installing {package_name} {version}...")

        # Check if already installed
        if package_name in self.installed:
            print(f"Package {package_name} already installed")
            return True

        # Download package
        package = self._download_package(package_name, version)
        if not package:
            print(f"Failed to download package {package_name}")
            return False

        # Install dependencies
        for dep in package.dependencies:
            if dep.type == DependencyType.REQUIRED:
                if not self.install(dep.name, dep.version):
                    print(f"Failed to install dependency {dep.name}")
                    return False

        # Install package files
        self._install_package_files(package)

        # Record installation
        self.installed[package_name] = package

        print(f"Successfully installed {package_name} {package.version}")
        return True

    def uninstall(self, package_name: str) -> bool:
        """Uninstall package"""
        if package_name not in self.installed:
            print(f"Package {package_name} not installed")
            return False

        package = self.installed[package_name]

        # Remove package files
        for file in package.files:
            file_path = os.path.join(self.cache_dir, file)
            if os.path.exists(file_path):
                os.remove(file_path)

        # Remove from installed
        del self.installed[package_name]

        print(f"Successfully uninstalled {package_name}")
        return True

    def update(self, package_name: str) -> bool:
        """Update package"""
        if package_name not in self.installed:
            print(f"Package {package_name} not installed")
            return False

        current = self.installed[package_name]

        # Get latest version
        latest = self._get_latest_version(package_name)
        if not latest or latest == current.version:
            print(f"{package_name} is already up to date")
            return True

        print(f"Updating {package_name} from {current.version} to {latest}...")

        # Uninstall current
        self.uninstall(package_name)

        # Install new version
        return self.install(package_name, latest)

    def list_installed(self) -> List[Package]:
        """List installed packages"""
        return list(self.installed.values())

    def search(self, query: str) -> List[Package]:
        """Search for packages"""
        results = []

        if self.index:
            for name, versions in self.index.packages.items():
                if query.lower() in name.lower():
                    results.extend(versions)

        return results

    def _download_package(self, package_name: str, version: str) -> Optional[Package]:
        """Download package from index"""
        # Simulated download - in production would fetch from package registry
        package = Package(
            name=package_name,
            version=version,
            description=f"Example package {package_name}",
            type=PackageType.LIBRARY,
            dependencies=[],
            author="Prim Team",
            license="MIT",
            repository=f"https://github.com/prim/{package_name}",
            files=[f"{package_name}.py"]
        )

        return package

    def _get_latest_version(self, package_name: str) -> Optional[str]:
        """Get latest package version"""
        # Simulated - in production would query package registry
        return "1.0.0"

    def _install_package_files(self, package: Package):
        """Install package files"""
        for file in package.files:
            # Simulated file installation
            pass


class ProjectManager:
    """Project manager"""

    def __init__(self, root_dir: str = "."):
        self.root_dir = root_dir
        self.config_file = os.path.join(root_dir, "prim_project.json")
        self.config: Dict[str, Any] = {}

    def init(self, name: str) -> bool:
        """Initialize new project"""
        self.config = {
            "name": name,
            "version": "0.1.0",
            "description": "",
            "dependencies": [],
            "dev_dependencies": [],
            "scripts": {}
        }

        self._save_config()
        print(f"Initialized project {name}")
        return True

    def add_dependency(self, name: str, version: str = "latest") -> bool:
        """Add dependency"""
        if "dependencies" not in self.config:
            self.config["dependencies"] = []

        self.config["dependencies"].append({
            "name": name,
            "version": version
        })

        self._save_config()
        print(f"Added dependency {name} {version}")
        return True

    def remove_dependency(self, name: str) -> bool:
        """Remove dependency"""
        if "dependencies" not in self.config:
            return False

        self.config["dependencies"] = [
            dep for dep in self.config["dependencies"]
            if dep["name"] != name
        ]

        self._save_config()
        print(f"Removed dependency {name}")
        return True

    def install_dependencies(self, package_manager: PackageManager) -> bool:
        """Install all dependencies"""
        if "dependencies" not in self.config:
            return True

        for dep in self.config["dependencies"]:
            if not package_manager.install(dep["name"], dep["version"]):
                return False

        return True

    def _load_config(self):
        """Load project configuration"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)

    def _save_config(self):
        """Save project configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)


class BuildSystem:
    """Build system"""

    def __init__(self, project_manager: ProjectManager):
        self.project_manager = project_manager
        self.build_dir = "build"
        self.dist_dir = "dist"

    def build(self, target: str = "default") -> bool:
        """Build project"""
        print(f"Building project {self.project_manager.config.get('name', 'project')}...")

        # Create build directories
        os.makedirs(self.build_dir, exist_ok=True)
        os.makedirs(self.dist_dir, exist_ok=True)

        # Compile source files
        self._compile_sources()

        # Link binaries
        self._link_binaries()

        # Package distribution
        self._package_distribution()

        print("Build completed successfully")
        return True

    def clean(self) -> bool:
        """Clean build artifacts"""
        import shutil

        if os.path.exists(self.build_dir):
            shutil.rmtree(self.build_dir)

        if os.path.exists(self.dist_dir):
            shutil.rmtree(self.dist_dir)

        print("Cleaned build artifacts")
        return True

    def _compile_sources(self):
        """Compile source files"""
        # Simulated compilation
        pass

    def _link_binaries(self):
        """Link binaries"""
        # Simulated linking
        pass

    def _package_distribution(self):
        """Package distribution"""
        # Simulated packaging
        pass


def main():
    """Main entry point"""
    print("Testing Package Manager...")

    # Test package manager
    pm = PackageManager()
    pm.install("test_package", "1.0.0")

    # Test project manager
    proj = ProjectManager()
    proj.init("test_project")
    proj.add_dependency("numpy", "1.0.0")

    # Test build system
    build = BuildSystem(proj)
    build.build()

    print("Package Manager initialized successfully")


if __name__ == "__main__":
    main()

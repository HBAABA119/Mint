"""
Prim Package Registry
Provides centralized package repository with semantic versioning,
dependency resolution, package metadata, security scanning, and private packages.
"""

import os
import json
import hashlib
import requests
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import re
from pathlib import Path
import shutil


class PackageType(Enum):
    """Package types"""
    LIBRARY = "library"
    FRAMEWORK = "framework"
    TOOL = "tool"
    EXAMPLE = "example"


@dataclass
class PackageVersion:
    """Package version information"""
    version: str
    dependencies: Dict[str, str] = field(default_factory=dict)
    files: List[str] = field(default_factory=list)
    checksum: str = ""
    size: int = 0
    release_date: str = ""
    changelog: str = ""


@dataclass
class PackageMetadata:
    """Package metadata"""
    name: str
    description: str
    author: str
    license: str
    repository: str
    homepage: str
    keywords: List[str] = field(default_factory=list)
    package_type: PackageType = PackageType.LIBRARY
    versions: Dict[str, PackageVersion] = field(default_factory=dict)
    latest_version: str = ""
    downloads: int = 0
    rating: float = 0.0
    security_score: float = 0.0


@dataclass
class Dependency:
    """Dependency information"""
    name: str
    version_constraint: str
    optional: bool = False


@dataclass
class SecurityReport:
    """Security report for a package"""
    package_name: str
    version: str
    vulnerabilities: List[Dict] = field(default_factory=list)
    security_score: float = 0.0
    scan_date: str = ""


class SemanticVersion:
    """Semantic version parsing and comparison"""

    @staticmethod
    def parse(version: str) -> Tuple[int, int, int, str]:
        """Parse semantic version string"""
        # Handle pre-release and build metadata
        match = re.match(r'^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.-]+))?(?:\+([a-zA-Z0-9.-]+))?$', version)
        if not match:
            raise ValueError(f"Invalid semantic version: {version}")
        
        major = int(match.group(1))
        minor = int(match.group(2))
        patch = int(match.group(3))
        prerelease = match.group(4) or ""
        
        return (major, minor, patch, prerelease)

    @staticmethod
    def compare(v1: str, v2: str) -> int:
        """Compare two semantic versions. Returns -1, 0, or 1"""
        p1 = SemanticVersion.parse(v1)
        p2 = SemanticVersion.parse(v2)
        
        # Compare major, minor, patch
        for i in range(3):
            if p1[i] < p2[i]:
                return -1
            elif p1[i] > p2[i]:
                return 1
        
        # Compare prerelease
        if p1[3] and not p2[3]:
            return -1
        elif not p1[3] and p2[3]:
            return 1
        elif p1[3] and p2[3]:
            if p1[3] < p2[3]:
                return -1
            elif p1[3] > p2[3]:
                return 1
        
        return 0

    @staticmethod
    def satisfies(version: str, constraint: str) -> bool:
        """Check if version satisfies constraint"""
        # Handle simple constraints
        if constraint.startswith('^'):
            # Caret range: ^1.2.3 means >=1.2.3 <2.0.0
            base_version = constraint[1:]
            parsed = SemanticVersion.parse(base_version)
            parsed_version = SemanticVersion.parse(version)
            
            if parsed_version[0] == parsed[0]:
                if parsed_version[1] > parsed[1]:
                    return True
                elif parsed_version[1] == parsed[1] and parsed_version[2] >= parsed[2]:
                    return True
            return False
        
        elif constraint.startswith('~'):
            # Tilde range: ~1.2.3 means >=1.2.3 <1.3.0
            base_version = constraint[1:]
            parsed = SemanticVersion.parse(base_version)
            parsed_version = SemanticVersion.parse(version)
            
            if parsed_version[0] == parsed[0] and parsed_version[1] == parsed[1]:
                if parsed_version[2] >= parsed[2]:
                    return True
            return False
        
        elif constraint.startswith('>'):
            # Greater than
            return SemanticVersion.compare(version, constraint[1:]) > 0
        
        elif constraint.startswith('>='):
            # Greater than or equal
            return SemanticVersion.compare(version, constraint[2:]) >= 0
        
        elif constraint.startswith('<'):
            # Less than
            return SemanticVersion.compare(version, constraint[1:]) < 0
        
        elif constraint.startswith('<='):
            # Less than or equal
            return SemanticVersion.compare(version, constraint[2:]) <= 0
        
        elif constraint.startswith('='):
            # Exact version
            return version == constraint[1:]
        
        else:
            # Exact version
            return version == constraint


class PackageRegistry:
    """Central package registry for Prim"""

    def __init__(self, registry_url: str = "https://registry.prim-lang.org"):
        self.registry_url = registry_url
        self.cache_dir = os.path.expanduser("~/.prim/packages")
        self.metadata_cache: Dict[str, PackageMetadata] = {}
        self.installed_packages: Dict[str, str] = {}  # name -> version
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Load installed packages
        self._load_installed_packages()

    def _load_installed_packages(self):
        """Load installed packages from disk"""
        installed_file = os.path.join(self.cache_dir, "installed.json")
        if os.path.exists(installed_file):
            with open(installed_file, 'r') as f:
                self.installed_packages = json.load(f)

    def _save_installed_packages(self):
        """Save installed packages to disk"""
        installed_file = os.path.join(self.cache_dir, "installed.json")
        with open(installed_file, 'w') as f:
            json.dump(self.installed_packages, f, indent=2)

    def search(self, query: str, limit: int = 10) -> List[PackageMetadata]:
        """Search for packages"""
        results = []
        
        # In a real implementation, this would query the registry API
        # For now, we'll search the local cache
        for metadata in self.metadata_cache.values():
            if query.lower() in metadata.name.lower() or \
               query.lower() in metadata.description.lower():
                results.append(metadata)
        
        return results[:limit]

    def get_package(self, name: str) -> Optional[PackageMetadata]:
        """Get package metadata"""
        # Check cache first
        if name in self.metadata_cache:
            return self.metadata_cache[name]
        
        # Fetch from registry
        try:
            metadata = self._fetch_package_metadata(name)
            if metadata:
                self.metadata_cache[name] = metadata
                return metadata
        except Exception as e:
            print(f"Error fetching package metadata: {e}")
        
        return None

    def _fetch_package_metadata(self, name: str) -> Optional[PackageMetadata]:
        """Fetch package metadata from registry"""
        # In a real implementation, this would make an API call
        # For now, return None
        return None

    def get_versions(self, name: str) -> List[str]:
        """Get all versions of a package"""
        metadata = self.get_package(name)
        if metadata:
            return sorted(metadata.versions.keys(), key=lambda v: SemanticVersion.parse(v), reverse=True)
        return []

    def install(
        self,
        name: str,
        version: Optional[str] = None,
        force: bool = False
    ) -> bool:
        """Install a package"""
        metadata = self.get_package(name)
        if not metadata:
            print(f"Package '{name}' not found")
            return False
        
        # Determine version to install
        if version is None:
            version = metadata.latest_version
            if not version and metadata.versions:
                version = max(metadata.versions.keys(), key=lambda v: SemanticVersion.parse(v))
        
        if version not in metadata.versions:
            print(f"Version '{version}' not found for package '{name}'")
            return False
        
        # Check if already installed
        if name in self.installed_packages and not force:
            print(f"Package '{name}' is already installed")
            return True
        
        # Resolve dependencies
        pkg_version = metadata.versions[version]
        if pkg_version.dependencies:
            print(f"Resolving dependencies for {name}...")
            for dep_name, dep_constraint in pkg_version.dependencies.items():
                if not self._install_dependency(dep_name, dep_constraint):
                    print(f"Failed to install dependency: {dep_name}")
                    return False
        
        # Install package
        print(f"Installing {name} {version}...")
        
        # Download package files
        package_dir = os.path.join(self.cache_dir, name, version)
        os.makedirs(package_dir, exist_ok=True)
        
        # In a real implementation, this would download from the registry
        # For now, just create a marker file
        marker_file = os.path.join(package_dir, ".installed")
        with open(marker_file, 'w') as f:
            f.write(json.dumps({
                'name': name,
                'version': version,
                'installed_at': str(__import__('datetime').datetime.now())
            }))
        
        # Update installed packages
        self.installed_packages[name] = version
        self._save_installed_packages()
        
        print(f"Successfully installed {name} {version}")
        return True

    def _install_dependency(self, name: str, constraint: str) -> bool:
        """Install a dependency with version constraint"""
        metadata = self.get_package(name)
        if not metadata:
            print(f"Dependency '{name}' not found")
            return False
        
        # Find satisfying version
        for version in sorted(metadata.versions.keys(), key=lambda v: SemanticVersion.parse(v), reverse=True):
            if SemanticVersion.satisfies(version, constraint):
                # Check if already installed
                if name in self.installed_packages:
                    if SemanticVersion.satisfies(self.installed_packages[name], constraint):
                        return True
                
                # Install
                return self.install(name, version)
        
        print(f"No version of '{name}' satisfies constraint: {constraint}")
        return False

    def uninstall(self, name: str) -> bool:
        """Uninstall a package"""
        if name not in self.installed_packages:
            print(f"Package '{name}' is not installed")
            return False
        
        version = self.installed_packages[name]
        
        # Remove package directory
        package_dir = os.path.join(self.cache_dir, name, version)
        if os.path.exists(package_dir):
            shutil.rmtree(package_dir)
        
        # Update installed packages
        del self.installed_packages[name]
        self._save_installed_packages()
        
        print(f"Successfully uninstalled {name}")
        return True

    def update(self, name: str) -> bool:
        """Update a package to the latest version"""
        metadata = self.get_package(name)
        if not metadata:
            print(f"Package '{name}' not found")
            return False
        
        current_version = self.installed_packages.get(name)
        if not current_version:
            print(f"Package '{name}' is not installed")
            return False
        
        # Get latest version
        latest_version = metadata.latest_version
        if not latest_version and metadata.versions:
            latest_version = max(metadata.versions.keys(), key=lambda v: SemanticVersion.parse(v))
        
        if not latest_version:
            print(f"No versions available for '{name}'")
            return False
        
        # Check if update needed
        if SemanticVersion.compare(latest_version, current_version) <= 0:
            print(f"{name} is already up to date ({current_version})")
            return True
        
        # Update
        print(f"Updating {name} from {current_version} to {latest_version}...")
        return self.install(name, latest_version, force=True)

    def list_installed(self) -> List[Tuple[str, str]]:
        """List all installed packages"""
        return sorted(self.installed_packages.items())

    def resolve_dependencies(
        self,
        dependencies: Dict[str, str]
    ) -> Dict[str, str]:
        """Resolve all dependencies and return version map"""
        resolved = {}
        queue = list(dependencies.items())
        
        while queue:
            name, constraint = queue.pop(0)
            
            if name in resolved:
                continue
            
            metadata = self.get_package(name)
            if not metadata:
                print(f"Warning: Could not find dependency '{name}'")
                continue
            
            # Find satisfying version
            version = None
            for v in sorted(metadata.versions.keys(), key=lambda v: SemanticVersion.parse(v), reverse=True):
                if SemanticVersion.satisfies(v, constraint):
                    version = v
                    break
            
            if not version:
                print(f"Warning: No version of '{name}' satisfies '{constraint}'")
                continue
            
            resolved[name] = version
            
            # Add transitive dependencies
            pkg_version = metadata.versions[version]
            for dep_name, dep_constraint in pkg_version.dependencies.items():
                if dep_name not in resolved:
                    queue.append((dep_name, dep_constraint))
        
        return resolved

    def scan_security(self, name: str, version: str) -> SecurityReport:
        """Scan a package for security vulnerabilities"""
        # In a real implementation, this would query a security database
        # For now, return a basic report
        return SecurityReport(
            package_name=name,
            version=version,
            vulnerabilities=[],
            security_score=100.0,
            scan_date=str(__import__('datetime').datetime.now())
        )

    def get_package_info(self, name: str) -> Optional[Dict]:
        """Get detailed package information"""
        metadata = self.get_package(name)
        if not metadata:
            return None
        
        info = {
            'name': metadata.name,
            'description': metadata.description,
            'author': metadata.author,
            'license': metadata.license,
            'repository': metadata.repository,
            'homepage': metadata.homepage,
            'keywords': metadata.keywords,
            'package_type': metadata.package_type.value,
            'latest_version': metadata.latest_version,
            'downloads': metadata.downloads,
            'rating': metadata.rating,
            'security_score': metadata.security_score,
            'versions': list(metadata.versions.keys())
        }
        
        return info


class RegistryCLI:
    """Command-line interface for package registry"""

    def __init__(self, registry: PackageRegistry):
        self.registry = registry

    def run(self, args: List[str]):
        """Run CLI command"""
        if not args:
            self.show_help()
            return
        
        command = args[0]
        command_args = args[1:]
        
        if command == 'search':
            self.cmd_search(command_args)
        elif command == 'install':
            self.cmd_install(command_args)
        elif command == 'uninstall':
            self.cmd_uninstall(command_args)
        elif command == 'update':
            self.cmd_update(command_args)
        elif command == 'list':
            self.cmd_list(command_args)
        elif command == 'info':
            self.cmd_info(command_args)
        elif command == 'versions':
            self.cmd_versions(command_args)
        else:
            print(f"Unknown command: {command}")
            self.show_help()

    def cmd_search(self, args: List[str]):
        """Search for packages"""
        if not args:
            print("Usage: search <query>")
            return
        
        query = args[0]
        limit = 10
        
        if len(args) > 1:
            try:
                limit = int(args[1])
            except ValueError:
                pass
        
        results = self.registry.search(query, limit)
        
        if not results:
            print(f"No packages found for '{query}'")
            return
        
        print(f"Found {len(results)} package(s) for '{query}':")
        print()
        
        for pkg in results:
            print(f"  {pkg.name} ({pkg.latest_version})")
            print(f"    {pkg.description}")
            print(f"    Downloads: {pkg.downloads} | Rating: {pkg.rating:.1f}")
            print()

    def cmd_install(self, args: List[str]):
        """Install a package"""
        if not args:
            print("Usage: install <package> [version]")
            return
        
        name = args[0]
        version = args[1] if len(args) > 1 else None
        
        self.registry.install(name, version)

    def cmd_uninstall(self, args: List[str]):
        """Uninstall a package"""
        if not args:
            print("Usage: uninstall <package>")
            return
        
        name = args[0]
        self.registry.uninstall(name)

    def cmd_update(self, args: List[str]):
        """Update a package"""
        if not args:
            print("Usage: update <package>")
            return
        
        name = args[0]
        self.registry.update(name)

    def cmd_list(self, args: List[str]):
        """List installed packages"""
        installed = self.registry.list_installed()
        
        if not installed:
            print("No packages installed")
            return
        
        print("Installed packages:")
        print()
        
        for name, version in installed:
            print(f"  {name} ({version})")

    def cmd_info(self, args: List[str]):
        """Show package information"""
        if not args:
            print("Usage: info <package>")
            return
        
        name = args[0]
        info = self.registry.get_package_info(name)
        
        if not info:
            print(f"Package '{name}' not found")
            return
        
        print(f"Package: {info['name']}")
        print(f"Description: {info['description']}")
        print(f"Author: {info['author']}")
        print(f"License: {info['license']}")
        print(f"Repository: {info['repository']}")
        print(f"Homepage: {info['homepage']}")
        print(f"Type: {info['package_type']}")
        print(f"Latest Version: {info['latest_version']}")
        print(f"Downloads: {info['downloads']}")
        print(f"Rating: {info['rating']:.1f}")
        print(f"Security Score: {info['security_score']:.1f}")

    def cmd_versions(self, args: List[str]):
        """List package versions"""
        if not args:
            print("Usage: versions <package>")
            return
        
        name = args[0]
        versions = self.registry.get_versions(name)
        
        if not versions:
            print(f"No versions found for '{name}'")
            return
        
        print(f"Available versions for {name}:")
        print()
        
        for version in versions:
            print(f"  {version}")

    def show_help(self):
        """Show help"""
        print("""
Prim Package Registry Commands:
  search <query> [limit]    Search for packages
  install <package> [ver]   Install a package
  uninstall <package>       Uninstall a package
  update <package>          Update a package
  list                      List installed packages
  info <package>            Show package information
  versions <package>        List package versions
""")


def main():
    """Main entry point"""
    import sys
    
    registry = PackageRegistry()
    cli = RegistryCLI(registry)
    
    cli.run(sys.argv[1:])


if __name__ == "__main__":
    main()

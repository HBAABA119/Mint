"""
Prim Package Manager - Prism-get

The official package manager for Prim language packages.
Manages dependencies, installations, and registries.
"""

import os
import json
import urllib.request
import zipfile
import shutil
from pathlib import Path


class PackageManager:
    """
    Prim Package Manager (prism-get)
    
    Manages Prim language packages, dependencies, and registries.
    """
    
    def __init__(self, install_dir="./prim_modules", registry_url="https://registry.prim-lang.org"):
        self.install_dir = Path(install_dir)
        self.registry_url = registry_url
        self.config_file = self.install_dir / "packages.json"
        
        # Ensure install directory exists
        self.install_dir.mkdir(exist_ok=True)
        
        # Load existing package configuration
        self.packages = self._load_config()
    
    def _load_config(self):
        """Load existing package configuration."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {"installed": {}, "dependencies": {}}
    
    def _save_config(self):
        """Save package configuration."""
        with open(self.config_file, 'w') as f:
            json.dump(self.packages, f, indent=2)
    
    def search(self, query):
        """Search for packages in the registry."""
        print(f"Searching for packages matching '{query}'...")
        # In a real implementation, this would query the online registry
        # For this prototype, we'll simulate the functionality
        print("Available packages (simulated):")
        print("- http-client: Simple HTTP client library")
        print("- template-engine: Template rendering engine")
        print("- db-driver: Database driver interface")
        return []
    
    def install(self, package_name, version="latest"):
        """Install a package."""
        print(f"Installing package: {package_name}@{version}")
        
        # Create package directory
        pkg_dir = self.install_dir / package_name
        pkg_dir.mkdir(exist_ok=True)
        
        # Simulate package download and extraction
        # In a real implementation, this would download from the registry
        print(f"Downloading {package_name}...")
        
        # Create a sample package file
        pkg_file = pkg_dir / f"{package_name}.prim"
        with open(pkg_file, 'w') as f:
            f.write(f"""# Prim package: {package_name}
# Version: {version}

# This is a sample package file
fn hello_world():
    return "Hello from {package_name}!"

# Export public functions
export hello_world
""")
        
        # Update config
        self.packages["installed"][package_name] = {
            "version": version,
            "path": str(pkg_dir.absolute()),
            "installed_at": "2023-01-01T00:00:00Z"  # In a real implementation, use actual timestamp
        }
        self._save_config()
        
        print(f"Successfully installed {package_name}@{version}")
        return True
    
    def uninstall(self, package_name):
        """Uninstall a package."""
        if package_name not in self.packages["installed"]:
            print(f"Package {package_name} is not installed")
            return False
        
        pkg_dir = self.install_dir / package_name
        if pkg_dir.exists():
            shutil.rmtree(pkg_dir)
        
        del self.packages["installed"][package_name]
        self._save_config()
        
        print(f"Successfully uninstalled {package_name}")
        return True
    
    def list_installed(self):
        """List all installed packages."""
        print("Installed packages:")
        for pkg_name, pkg_info in self.packages["installed"].items():
            print(f"- {pkg_name}@{pkg_info['version']} ({pkg_info['path']})")
        return self.packages["installed"]
    
    def update(self, package_name=None):
        """Update packages."""
        if package_name:
            print(f"Updating {package_name}...")
            # Update single package
            if package_name in self.packages["installed"]:
                current_version = self.packages["installed"][package_name]["version"]
                print(f"Updating {package_name} from {current_version} to latest...")
                # In a real implementation, check for newer version and update
                print(f"Updated {package_name} successfully")
            else:
                print(f"Package {package_name} not found")
        else:
            print("Updating all packages...")
            # Update all packages
            for pkg_name in self.packages["installed"].keys():
                print(f"Updating {pkg_name}...")
            print("All packages updated successfully")
    
    def init_project(self, project_name, description="", author=""):
        """Initialize a new Prim project."""
        proj_dir = Path(project_name)
        proj_dir.mkdir(exist_ok=True)
        
        # Create project structure
        (proj_dir / "src").mkdir(exist_ok=True)
        (proj_dir / "tests").mkdir(exist_ok=True)
        (proj_dir / "docs").mkdir(exist_ok=True)
        
        # Create prim.json manifest
        manifest = {
            "name": project_name,
            "version": "0.1.0",
            "description": description,
            "author": author,
            "dependencies": {},
            "devDependencies": {}
        }
        
        with open(proj_dir / "prim.json", 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"Initialized new Prim project: {project_name}")
        print(f"Directory structure created:")
        print(f"  {project_name}/")
        print(f"  ├── src/")
        print(f"  ├── tests/")
        print(f"  ├── docs/")
        print(f"  └── prim.json")
        
        return True


def main():
    """Command line interface for the package manager."""
    import sys
    
    if len(sys.argv) < 2:
        print("Prism-get: Prim Package Manager")
        print("Usage: prism-get <command> [options]")
        print("Commands:")
        print("  install <package>     Install a package")
        print("  uninstall <package>   Uninstall a package")
        print("  search <query>        Search for packages")
        print("  list                  List installed packages")
        print("  update [package]      Update packages")
        print("  init <project>        Initialize a new project")
        return
    
    cmd = sys.argv[1]
    pm = PackageManager()
    
    if cmd == "install":
        if len(sys.argv) < 3:
            print("Usage: prism-get install <package>")
            return
        package = sys.argv[2]
        version = sys.argv[3] if len(sys.argv) > 3 else "latest"
        pm.install(package, version)
    
    elif cmd == "uninstall":
        if len(sys.argv) < 3:
            print("Usage: prism-get uninstall <package>")
            return
        package = sys.argv[2]
        pm.uninstall(package)
    
    elif cmd == "search":
        if len(sys.argv) < 3:
            print("Usage: prism-get search <query>")
            return
        query = sys.argv[2]
        pm.search(query)
    
    elif cmd == "list":
        pm.list_installed()
    
    elif cmd == "update":
        package = sys.argv[2] if len(sys.argv) > 2 else None
        pm.update(package)
    
    elif cmd == "init":
        if len(sys.argv) < 3:
            print("Usage: prism-get init <project_name>")
            return
        project_name = sys.argv[2]
        description = sys.argv[3] if len(sys.argv) > 3 else ""
        pm.init_project(project_name, description)
    
    else:
        print(f"Unknown command: {cmd}")
        print("Use 'prism-get' without arguments to see help")


if __name__ == "__main__":
    main()
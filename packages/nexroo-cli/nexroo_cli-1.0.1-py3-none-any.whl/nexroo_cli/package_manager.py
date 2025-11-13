import sys
import subprocess
import json
import compileall
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger
import importlib.metadata
import httpx


class PackageRegistry:
    GITHUB_ORG = "nexroo-ai"
    CACHE_FILE = Path.home() / ".nexroo" / "package_cache.json"
    CACHE_TTL = 3600  # 1 hour

    @classmethod
    def _fetch_from_github(cls) -> List[Dict]:
        try:
            url = f"https://api.github.com/orgs/{cls.GITHUB_ORG}/repos"
            response = httpx.get(url, params={"per_page": 100}, timeout=10.0)
            response.raise_for_status()

            repos = response.json()
            packages = []

            for repo in repos:
                name = repo["name"]
                if name.endswith("-rooms-pkg"):
                    packages.append({
                        "name": name,
                        "description": repo.get("description", ""),
                        "url": f"git+https://github.com/{cls.GITHUB_ORG}/{name}.git",
                        "stars": repo.get("stargazers_count", 0),
                        "updated_at": repo.get("updated_at", "")
                    })

            return packages
        except Exception as e:
            logger.warning(f"Failed to fetch packages from GitHub: {e}")
            return []

    @classmethod
    def _load_cache(cls) -> Optional[Dict]:
        if not cls.CACHE_FILE.exists():
            return None

        try:
            with open(cls.CACHE_FILE) as f:
                cache = json.load(f)

            cached_at = datetime.fromisoformat(cache["cached_at"])
            age = (datetime.now() - cached_at).total_seconds()

            if age < cls.CACHE_TTL:
                return cache

            return None
        except Exception:
            return None

    @classmethod
    def _save_cache(cls, packages: List[Dict]):
        try:
            cls.CACHE_FILE.parent.mkdir(exist_ok=True, parents=True)
            with open(cls.CACHE_FILE, 'w') as f:
                json.dump({
                    "cached_at": datetime.now().isoformat(),
                    "packages": packages
                }, f, indent=2)
        except Exception as e:
            logger.debug(f"Failed to save cache: {e}")

    @classmethod
    def get_packages(cls, refresh: bool = False) -> List[Dict]:
        if not refresh:
            cache = cls._load_cache()
            if cache:
                logger.debug("Using cached package list")
                return cache["packages"]

        logger.debug(f"Fetching packages from GitHub ({cls.GITHUB_ORG})...")
        packages = cls._fetch_from_github()

        if packages:
            cls._save_cache(packages)

        return packages

    @classmethod
    def get_package(cls, name: str) -> Optional[Dict]:
        packages = cls.get_packages()
        for pkg in packages:
            if pkg["name"] == name:
                return pkg
        return None

    @classmethod
    def search_packages(cls, query: str) -> List[Dict]:
        packages = cls.get_packages()
        query_lower = query.lower()
        return [
            pkg for pkg in packages
            if query_lower in pkg["name"].lower() or query_lower in pkg["description"].lower()
        ]


class PackageManager:
    def __init__(self):
        self.registry = PackageRegistry()
        self.config_dir = Path.home() / ".nexroo"
        self.config_dir.mkdir(exist_ok=True, parents=True)

        self.plugin_dir = self.config_dir / "plugins"
        self.plugin_dir.mkdir(exist_ok=True, parents=True)

        self.installed_file = self.config_dir / "installed_packages.json"

    def _load_installed(self) -> Dict:
        if not self.installed_file.exists():
            return {}
        try:
            with open(self.installed_file) as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load installed packages: {e}")
            return {}

    def _save_installed(self, installed: Dict):
        try:
            with open(self.installed_file, 'w') as f:
                json.dump(installed, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save installed packages: {e}")

    def _is_in_plugin_dir(self, package_name: str) -> bool:
        pkg_dir = self.plugin_dir / package_name.replace("-", "_")
        if pkg_dir.exists() and pkg_dir.is_dir():
            return True

        dist_info_pattern = f"{package_name.replace('-', '_')}*.dist-info"
        matches = list(self.plugin_dir.glob(dist_info_pattern))
        return len(matches) > 0

    def is_installed(self, package_name: str) -> bool:
        if self._is_in_plugin_dir(package_name):
            return True

        try:
            importlib.metadata.version(package_name)
            return True
        except importlib.metadata.PackageNotFoundError:
            return False

    def get_installed_version(self, package_name: str) -> Optional[str]:
        try:
            return importlib.metadata.version(package_name)
        except importlib.metadata.PackageNotFoundError:
            installed = self._load_installed()
            if package_name in installed:
                return installed[package_name].get("version", "unknown")
            return None

    def get_installed_location(self, package_name: str) -> Optional[str]:
        if self._is_in_plugin_dir(package_name):
            return "plugin"

        try:
            dist = importlib.metadata.distribution(package_name)
            if str(self.plugin_dir) in str(dist._path):
                return "plugin"
            return "bundled"
        except importlib.metadata.PackageNotFoundError:
            return None

    def list_installed(self) -> List[Dict]:
        installed_meta = self._load_installed()
        result = []

        for name, info in installed_meta.items():
            location = self.get_installed_location(name)
            if location:
                result.append({
                    "name": name,
                    "version": info.get("version", "unknown"),
                    "description": info.get("description", ""),
                    "installed_at": info.get("installed_at", ""),
                    "location": location
                })

        return result

    async def install(self, package_name: str, version: Optional[str] = None,
                     url: Optional[str] = None, upgrade: bool = False) -> bool:
        package_info = self.registry.get_package(package_name)

        if not package_info and not url:
            logger.error(f"Package '{package_name}' not found in registry")
            logger.info("Run 'nexroo addon search' to see available packages")
            logger.info("Or provide a custom URL with --url")
            return False

        if self.is_installed(package_name) and not upgrade:
            current_version = self.get_installed_version(package_name)
            location = self.get_installed_location(package_name)
            logger.warning(f"Package '{package_name}' v{current_version} is already installed ({location})")
            logger.info("Use --upgrade to update the package")
            return False

        install_url = url or package_info["url"]

        cmd = [
            sys.executable, "-m", "pip", "install",
            "--target", str(self.plugin_dir),
            "--upgrade" if upgrade else "--no-deps"
        ]

        if version and not url:
            cmd.append(f"{package_name}=={version}")
        else:
            cmd.append(install_url)

        logger.info(f"Installing {package_name} to {self.plugin_dir}...")
        logger.debug(f"Command: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.debug(result.stdout)

            logger.debug("Compiling bytecode...")
            pkg_dir = self.plugin_dir / package_name.replace("-", "_")
            if pkg_dir.exists():
                compileall.compile_dir(pkg_dir, quiet=1, force=True)

            installed_version = self.get_installed_version(package_name) or "unknown"

            installed = self._load_installed()
            installed[package_name] = {
                "version": installed_version,
                "description": package_info["description"] if package_info else "",
                "installed_at": datetime.now().isoformat(),
                "source": install_url,
                "location": "plugin"
            }
            self._save_installed(installed)

            logger.success(f"✓ Successfully installed {package_name} v{installed_version}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Installation failed: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Installation failed: {e}")
            return False

    async def uninstall(self, package_name: str, force: bool = False) -> bool:
        location = self.get_installed_location(package_name)

        if not location:
            logger.warning(f"Package '{package_name}' is not installed")
            return False

        if location == "bundled":
            logger.error(f"Cannot uninstall bundled package '{package_name}'")
            return False

        if not force:
            logger.warning(f"Uninstall {package_name}?")
            response = input("Continue? [y/N]: ")
            if response.lower() != 'y':
                logger.info("Cancelled")
                return False

        logger.info(f"Uninstalling {package_name}...")

        try:
            import shutil

            pkg_dir = self.plugin_dir / package_name.replace("-", "_")
            if pkg_dir.exists():
                shutil.rmtree(pkg_dir)

            dist_info_pattern = f"{package_name.replace('-', '_')}*.dist-info"
            for dist_info in self.plugin_dir.glob(dist_info_pattern):
                shutil.rmtree(dist_info)

            installed = self._load_installed()
            if package_name in installed:
                del installed[package_name]
                self._save_installed(installed)

            logger.success(f"✓ Uninstalled {package_name}")
            return True

        except Exception as e:
            logger.error(f"Uninstallation failed: {e}")
            return False

    async def update(self, package_name: str) -> bool:
        location = self.get_installed_location(package_name)

        if not location:
            logger.warning(f"Package '{package_name}' is not installed")
            return False

        if location == "bundled":
            logger.warning(f"Cannot update bundled package '{package_name}'")
            return False

        return await self.install(package_name, upgrade=True)

    async def update_all(self) -> Dict[str, bool]:
        installed = self.list_installed()
        plugin_packages = [pkg for pkg in installed if pkg["location"] == "plugin"]

        if not plugin_packages:
            logger.info("No plugin packages to update")
            return {}

        results = {}
        for pkg in plugin_packages:
            name = pkg["name"]
            logger.info(f"Updating {name}...")
            results[name] = await self.update(name)

        return results

    def get_plugin_dir(self) -> Path:
        return self.plugin_dir

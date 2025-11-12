"""
Build script for sheep-herding-rl package.
Run this script to build distribution files.
"""

import subprocess
import sys
import shutil
from pathlib import Path


def clean_build_artifacts():
    """Remove old build artifacts."""
    print("🧹 Cleaning old build artifacts...")
    
    dirs_to_remove = ['build', 'dist', '*.egg-info']
    for pattern in dirs_to_remove:
        for path in Path('.').glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"   Removed: {path}")
    
    print("✅ Clean complete\n")


def install_build_tools():
    """Ensure build tools are installed."""
    print("📦 Installing/upgrading build tools...")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip", "build", "twine"],
            check=True,
            capture_output=True
        )
        print("✅ Build tools ready\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install build tools: {e}")
        return False


def build_package():
    """Build source distribution and wheel."""
    print("🔨 Building package...")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "build"],
            check=True
        )
        print("✅ Build complete\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False


def check_package():
    """Verify package with twine."""
    print("🔍 Checking package with twine...")
    
    try:
        result = subprocess.run(
            ["twine", "check", "dist/*"],
            check=True,
            capture_output=True,
            text=True,
            shell=True
        )
        print(result.stdout)
        print("✅ Package check passed\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Package check failed: {e}")
        if e.output:
            print(e.output)
        return False


def list_build_artifacts():
    """List created distribution files."""
    print("📦 Build artifacts created:")
    
    dist_path = Path('dist')
    if dist_path.exists():
        for file in dist_path.iterdir():
            size = file.stat().st_size / 1024  # KB
            print(f"   {file.name} ({size:.1f} KB)")
    else:
        print("   No dist/ directory found")
    
    print()


def main():
    """Main build process."""
    print("=" * 60)
    print("🚀 Sheep Herding RL Package Builder")
    print("=" * 60)
    print()
    
    # Step 1: Clean
    clean_build_artifacts()
    
    # Step 2: Install tools
    if not install_build_tools():
        print("❌ Build process failed at tool installation")
        return 1
    
    # Step 3: Build
    if not build_package():
        print("❌ Build process failed")
        return 1
    
    # Step 4: Check
    if not check_package():
        print("⚠️  Package has issues, but build completed")
        print("    Review the warnings above")
    
    # Step 5: List artifacts
    list_build_artifacts()
    
    print("=" * 60)
    print("✅ Build process complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  • Test locally: pip install dist/*.whl")
    print("  • Upload to TestPyPI: twine upload --repository testpypi dist/*")
    print("  • Upload to PyPI: twine upload dist/*")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

# scripts/release.py
import subprocess
import sys
import toml
from pathlib import Path
import os

def get_project_root():
    """Get the project root directory"""
    script_path = Path(os.path.abspath(__file__))
    return script_path.parent.parent

def load_pyproject():
    """Load pyproject.toml"""
    root = get_project_root()
    pyproject_path = root / "pyproject.toml"
    return toml.load(pyproject_path)

def save_pyproject(config):
    """Save pyproject.toml"""
    root = get_project_root()
    pyproject_path = root / "pyproject.toml"
    with open(pyproject_path, "w") as f:
        toml.dump(config, f)

def update_version(version_type="minor"):
    """Update version in pyproject.toml and __init__.py"""
    config = load_pyproject()
    current_version = config["tool"]["poetry"]["version"]
    major, minor, patch = map(int, current_version.split("."))
    
    if version_type == "major":
        new_version = f"{major + 1}.0.0"
    elif version_type == "minor":
        new_version = f"{major}.{minor + 1}.0"
    else:  # patch
        new_version = f"{major}.{minor}.{patch + 1}"
    
    # Update pyproject.toml
    config["tool"]["poetry"]["version"] = new_version
    save_pyproject(config)
    
    # Update __init__.py
    root = get_project_root()
    init_path = root / "src" / "scholarSparkObservability" / "__init__.py"
    
    with open(init_path, "r") as f:
        lines = f.readlines()
    
    with open(init_path, "w") as f:
        for line in lines:
            if line.startswith("__version__"):
                f.write(f'__version__ = "{new_version}"\n')
            else:
                f.write(line)
    
    print(f"Updated version from {current_version} to {new_version} in:")
    print(f"  - pyproject.toml")
    print(f"  - src/scholarSparkObservability/__init__.py")
    
    return new_version

def build_and_publish(test=True):
    """Build and publish package"""
    root = get_project_root()
    os.chdir(root)  # Change to project root directory
    
    # Clean previous builds
    subprocess.run(["rm", "-rf", "dist/"])
    
    # Build
    subprocess.run(["poetry", "build"])
    
    # Upload to TestPyPI or PyPI
    if test:
        subprocess.run(["twine", "upload", "-r", "testpypi", "dist/*"])
    else:
        subprocess.run(["twine", "upload", "dist/*"])

def main():
    # Get version type from command line
    version_type = input("Enter version type (major/minor/patch): ").lower()
    if version_type not in ["major", "minor", "patch"]:
        print("Invalid version type. Use major, minor, or patch.")
        sys.exit(1)
    
    # Update version
    new_version = update_version(version_type)
    print(f"Updated version to {new_version}")
    
    # Ask for deployment target
    deploy_target = input("Deploy to TestPyPI or PyPI or both? (test/prod/both): ").lower()
    if deploy_target not in ["test", "prod", "both"]:
        print("Invalid deployment target. Use test, prod, or both.")
        sys.exit(1)
    
    # Build and publish
    if deploy_target == "both":
        build_and_publish(test=True)
        build_and_publish(test=False)
        print(f"Published version {new_version} to both TestPyPI and PyPI")
    else:
        build_and_publish(test=(deploy_target == "test"))
        print(f"Published version {new_version} to {'TestPyPI' if deploy_target == 'test' else 'PyPI'}")

if __name__ == "__main__":
    main()
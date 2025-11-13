"""
Package management operations
"""
import subprocess
import json
from ..utils.logger import log, write_log
from ..utils.version import is_minor_update

def get_outdated_packages(project_path, minor_only=False):
    """Get outdated packages from npm"""
    result = subprocess.run(['npm', 'outdated', '--json'], cwd=project_path, capture_output=True, text=True)
    if result.returncode != 0 and result.stderr:
        error_msg = f"Error running npm outdated: {result.stderr}"
        print(error_msg)
        write_log(f"ERROR: {error_msg}")
        return {}
    
    try:
        outdated_packages = json.loads(result.stdout) if result.stdout.strip() else {}
        
        if minor_only:
            filtered = {}
            for package, details in outdated_packages.items():
                if is_minor_update(details.get("current", ""), details.get("latest", "")):
                    filtered[package] = details
            outdated_packages = filtered
            write_log(f"Filtered to {len(outdated_packages)} minor updates only")
        
        write_log(f"Found {len(outdated_packages)} outdated packages: {list(outdated_packages.keys())}")
        print_outdated_packages(outdated_packages)
    except Exception as e:
        error_msg = f"Error parsing npm outdated output: {e}"
        print(error_msg)
        write_log(f"ERROR: {error_msg}")
        return {}
    
    return outdated_packages

def print_outdated_packages(outdated_packages):
    """Print the outdated packages in a formatted table."""
    log("\nOutdated Packages:")
    log("{:<40} {:<10} {:<10} {:<10}".format("Package", "Current", "Wanted", "Latest"))
    log("-" * 70)
    for package, details in outdated_packages.items():
        current_version = details.get("current", "N/A")
        wanted_version = details.get("wanted", "N/A")
        latest_version = details.get("latest", "N/A")
        log("{:<40} {:<10} {:<10} {:<10}".format(package, current_version, wanted_version, latest_version))
    log("-" * 70)

def get_dependency_tree(project_path):
    """Fetch the dependency tree using npm ls."""
    try:
        result = subprocess.run(['npm', 'ls', '--json'], cwd=project_path, capture_output=True, text=True)
        sanitized_output = sanitize_json_output(result.stdout)
        dependency_tree = json.loads(sanitized_output)
    except Exception as e:
        error_msg = f"Error parsing npm ls output: {e}"
        print(error_msg)
        write_log(f"ERROR: {error_msg}")
        return {}
    
    return dependency_tree

def sanitize_json_output(output):
    """Sanitize JSON output to replace JavaScript-style values with Python-compatible values."""
    sanitized_output = output.replace("false", "false").replace("true", "true").replace("null", "null")
    return sanitized_output

def install_package(package, version, project_path, quiet_mode):
    """Install a specific package version."""
    try:
        log(f"\nUpdating {package} to {version}...")
        subprocess.run(["npm", "install", f"{package}@{version}"], cwd=project_path, check=True,
                      capture_output=quiet_mode, text=True)
    except subprocess.CalledProcessError as e:
        error_msg = f"Error installing {package}@{version}: {e}"
        write_log(f"ERROR: {error_msg}")
        raise Exception(error_msg)
    return True

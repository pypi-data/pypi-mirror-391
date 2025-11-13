"""
PackUpdate - Python Package Updater
Main entry point for the application
"""
import os
import sys
from .utils.logger import set_quiet_mode, write_log, log, get_log_file
from .utils.cli import parse_cli_args, handle_special_flags
from .services.report_service import generate_comprehensive_report
from .services.package_service import get_outdated_packages, get_dependency_tree, install_package
from .services.interactive_service import InteractiveService
from .services.version_service import VersionService

def validate_project_path(project_path):
    """Validate project path exists and is a directory"""
    if not os.path.isdir(project_path):
        error_msg = f"Error: {project_path} is not a valid directory."
        print(error_msg)
        write_log(f"ERROR: {error_msg}")
        sys.exit(1)

def resolve_update_order(outdated_packages, dependency_tree):
    """Determine the order of updates based on interdependencies among outdated packages."""
    resolved_order = []
    visited = set()

    def visit(package):
        if package in visited:
            return
        visited.add(package)
        dependencies = dependency_tree.get('dependencies', {}).get(package, {}).get('requires', {})
        for dep in dependencies:
            if dep in outdated_packages:
                visit(dep)
        resolved_order.append(package)

    for package in outdated_packages:
        visit(package)
    
    return resolved_order

def execute_script_if_exist(project_path, script_name, quiet_mode):
    """Check if the project has a script in package.json."""
    import json
    import subprocess
    
    package_json_path = os.path.join(project_path, "package.json")
    if not os.path.isfile(package_json_path):
        return False
        
    try:
        with open(package_json_path, "r") as f:
            package_data = json.load(f)
        script_exists = script_name in package_data.get("scripts", {})
        returnCode = 0
        if script_exists:
            script_execute = subprocess.run(["npm", "run", script_name], cwd=project_path, 
                                          capture_output=quiet_mode, text=True)
            returnCode = script_execute.returncode
        else:
            returnCode = 0
            log(f"No {script_name} script found in package.json. Skipping.")
        return returnCode == 0
    except Exception as e:
        error_msg = f"Error reading package.json: {e}"
        print(error_msg)
        write_log(f"ERROR: {error_msg}")
        return False

def run_tests(project_path, quiet_mode):
    """Run build and test scripts"""
    log("\nRunning build...")
    resultBuild = execute_script_if_exist(project_path, "build", quiet_mode)
    log("\nRunning tests...")
    resultTest = execute_script_if_exist(project_path, "test", quiet_mode)
    if resultBuild == False or resultTest == False:
        error_msg = "Tests failed."
        write_log(f"ERROR: {error_msg}")
        raise Exception(error_msg)

def update_packages_in_order(outdated_packages, dependency_tree, project_path, safe_mode, quiet_mode):   
    """Update packages in the resolved order."""
    from services.report_service import get_safe_packages_for_update
    
    original_order = resolve_update_order(outdated_packages, dependency_tree)
    
    # Get safe packages and prioritize them
    safe_packages = get_safe_packages_for_update(project_path)
    safe_in_order = [pkg for pkg in original_order if pkg in safe_packages]
    risky_in_order = [pkg for pkg in original_order if pkg not in safe_packages]
    
    log(f"\n🔍 UPDATE PRIORITIZATION:")
    log(f"✅ Safe packages (no breaking changes): {len(safe_in_order)}")
    log(f"⚠️  Risky packages (potential breaking changes): {len(risky_in_order)}")
    
    update_order = safe_in_order + risky_in_order
    log("\nFinal Update Order: " + ", ".join(update_order))
    
    failed_updates = []
    updated_packages = []

    for package in update_order:
        details = outdated_packages[package]
        current_version = details.get("current")
        latest_version = details.get("latest")
        final_version = current_version
        is_safe = package in safe_packages
        
        if safe_mode:
            log(f"\n{'✅' if is_safe else '⚠️'} Trying to update {package} to latest version {latest_version} ({'safe' if is_safe else 'risky'})...")
            try:
                install_package(package, latest_version, project_path, quiet_mode)
                run_tests(project_path, quiet_mode)
                final_version = latest_version
                write_log(f"SUCCESS: Updated {package} from {current_version} to {latest_version} ({'safe' if is_safe else 'risky'})")
            except:
                log(f"Update failed for {package}")
                failed_updates.append(package)
                write_log(f"FAILED: {package} update failed")
        else:
            if current_version and latest_version and current_version != latest_version:
                try:
                    log(f"\n{'✅' if is_safe else '⚠️'} Updating {package} ({'safe' if is_safe else 'risky'})...")
                    install_package(package, latest_version, project_path, quiet_mode)
                    run_tests(project_path, quiet_mode)
                    final_version = latest_version
                    write_log(f"SUCCESS: Updated {package} from {current_version} to {latest_version} ({'safe' if is_safe else 'risky'})")
                except Exception as e:
                    error_msg = f"Failed to update {package}: {e}"
                    write_log(f"ERROR: {error_msg}")
                    failed_updates.append(package)
                    write_log(f"FAILED: {package} update failed")
            else:
                log(f"Skipping {package}, already at latest version or missing version info.")
        
        updated_packages.append((package, current_version, final_version))
    return updated_packages, failed_updates

def run_update_process(project_path, safe_mode, passes, minor_only, quiet_mode, update_version=None):
    """Execute update process with multiple passes"""
    import subprocess
    
    all_updated_packages = []
    all_failed_updates = []
    
    for i in range(passes):
        log(f"\n=== Pass {i + 1} ===")
        outdated_packages = get_outdated_packages(project_path, minor_only)
        if not outdated_packages:
            log("No more outdated packages found.")
            break
        
        dependency_tree = get_dependency_tree(project_path)
        updated_packages, failed_updates = update_packages_in_order(outdated_packages, dependency_tree, project_path, safe_mode, quiet_mode)
        all_updated_packages.append((i + 1, updated_packages))
        all_failed_updates.extend(failed_updates)
    
    log("\nRunning final npm audit and build...")
    subprocess.run(["npm", "audit", "fix"], cwd=project_path, capture_output=quiet_mode, text=True)
    execute_script_if_exist(project_path, "build", quiet_mode)
    print_final_summary(all_updated_packages, all_failed_updates)

def print_final_summary(all_updated_packages, all_failed_updates):
    """Print the final summary of updated packages."""
    log("\nFinal Update Summary:")
    log("{:<40} {:<10} {:<10}".format("Package", "Old Version", "New Version"))
    log("-" * 60)
    for pass_num, updated_packages in all_updated_packages:
        log(f"\n=== Pass {pass_num} ===")
        for package, old_version, new_version in updated_packages:
            log("{:<40} {:<10} {:<10}".format(package, old_version, new_version))
    log("-" * 60)

    if all_failed_updates:
        log("\nPackages that failed to update:")
        for package in set(all_failed_updates):
            log(f"- {package}")
    
    # Update project version if requested and updates were successful
    if update_version and any(updated_packages for updated_packages, _ in all_results):
        VersionService.update_project_version(project_path, update_version, quiet_mode)

def run_interactive_mode(project_path, safe_mode, quiet_mode, update_version=None):
    """Execute interactive mode for selective package updates"""
    try:
        log("🔍 Checking for outdated packages...")
        outdated_packages = get_outdated_packages(project_path)
        
        if not outdated_packages:
            log("✅ All packages are up to date!")
            return

        selected_packages = InteractiveService.select_packages(outdated_packages)
        
        if not selected_packages:
            log("No packages selected for update.")
            return

        confirmed = InteractiveService.confirm_updates(selected_packages)
        if not confirmed:
            log("Update cancelled by user.")
            return

        log("\n🚀 Starting interactive updates...")
        
        # Process selected packages
        updated_packages = []
        failed_updates = []
        
        for choice in selected_packages:
            target_version = choice.latest if choice.update_type == 'major' else choice.wanted
            log(f"\nUpdating {choice.name} from {choice.current} to {target_version}...")
            
            try:
                success = install_package(choice.name, target_version, project_path, safe_mode, quiet_mode)
                if success:
                    updated_packages.append((choice.name, choice.current, target_version))
                    log(f"✅ Successfully updated {choice.name}")
                else:
                    failed_updates.append(choice.name)
                    log(f"❌ Failed to update {choice.name}")
            except Exception as error:
                failed_updates.append(choice.name)
                log(f"❌ Failed to update {choice.name}: {error}")

        # Print summary
        log("\n" + "=" * 60)
        log("Interactive Update Summary:")
        log("{:<40} {:<10} {:<10}".format("Package", "Old Version", "New Version"))
        log("-" * 60)
        
        if updated_packages:
            for package, old_version, new_version in updated_packages:
                log("{:<40} {:<10} {:<10}".format(package, old_version, new_version))
        
        if failed_updates:
            log("\nPackages that failed to update:")
            for package in failed_updates:
                log(f"- {package}")
        
        # Update project version if requested and updates were successful
        if update_version and updated_packages:
            VersionService.update_project_version(project_path, update_version, quiet_mode)
            
    except Exception as error:
        log(f"❌ Interactive mode failed: {error}")
        raise error

def handle_cleanup_operations(project_path, remove_unused, dedupe_packages, quiet_mode):
    """Handle cleanup operations"""
    from services.cleanup_service import remove_unused_packages, dedupe_packages as dedupe_func
    
    log("\n=== Package Cleanup Operations ===")
    
    if remove_unused:
        removed_packages = remove_unused_packages(project_path, quiet_mode)
        log(f"\n✅ Cleanup Summary: Removed {len(removed_packages)} unused packages")
    
    if dedupe_packages:
        package_count = dedupe_func(project_path, quiet_mode)
        log(f"\n✅ Dedupe Summary: {package_count} unique packages remaining")
    
    write_log(f"Cleanup operations completed - Log file: {get_log_file()}")
    print(f"Log file created: {get_log_file()}")

def main():
    """Main application entry point"""
    # Handle special flags first (help, version, type)
    if handle_special_flags():
        return

    # Parse CLI arguments
    cli_args = parse_cli_args()
    project_path = cli_args['project_path']
    safe_mode = cli_args['safe_mode']
    interactive = cli_args['interactive']
    minor_only = cli_args['minor_only']
    generate_report = cli_args['generate_report']
    remove_unused = cli_args['remove_unused']
    dedupe_packages = cli_args['dedupe_packages']
    quiet_mode = cli_args['quiet_mode']
    passes = cli_args['passes']
    update_version = cli_args['update_version']

    # Set up logging
    set_quiet_mode(quiet_mode)
    write_log(f"PackUpdate started - Project: {project_path}, Safe Mode: {safe_mode}, Interactive: {interactive}, Minor Only: {minor_only}, Generate Report: {generate_report}, Remove Unused: {remove_unused}, Dedupe: {dedupe_packages}, Passes: {passes}, Update Version: {update_version or 'none'}, Quiet: {quiet_mode}")
    
    # Validate project path
    validate_project_path(project_path)
    
    # Handle cleanup operations
    if remove_unused or dedupe_packages:
        handle_cleanup_operations(project_path, remove_unused, dedupe_packages, quiet_mode)
        return
    
    # Handle report generation (no updates)
    if generate_report:
        generate_comprehensive_report(project_path)
        return
    
    # Handle interactive mode
    if interactive:
        run_interactive_mode(project_path, safe_mode, quiet_mode, update_version)
        return
    
    # Execute update process
    run_update_process(project_path, safe_mode, passes, minor_only, quiet_mode, update_version)
    
    # Log completion
    write_log(f"PackUpdate completed - Log file: {get_log_file()}")
    print(f"Log file created: {get_log_file()}")

if __name__ == "__main__":
    main()

import os
import yaml
import time
import sys

# ANSI escape sequences for text styling
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"


def is_flutter_project(project_path):
    pubspec_path = os.path.join(project_path, "pubspec.yaml")
    lib_path = os.path.join(project_path, "lib")
    return os.path.exists(pubspec_path) or os.path.exists(lib_path)


def load_pubspec(project_path):
    pubspec_path = os.path.join(project_path, "pubspec.yaml")
    with open(pubspec_path, "r") as f:
        return yaml.safe_load(f)


def collect_dart_files(project_path):
    dart_files = []
    for root, dirs, files in os.walk(project_path):
        for file in files:
            if file.endswith(".dart"):
                dart_files.append(os.path.join(root, file))
    return dart_files


def is_package_used(package, dart_files):
    for file in dart_files:
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
            if f"package:{package}" in content:
                return True
    return False


def find_unused_packages(project_path):
    pubspec = load_pubspec(project_path)
    dependencies = pubspec.get("dependencies", {}).keys()
    dev_dependencies = pubspec.get("dev_dependencies", {}).keys()
    dart_files = collect_dart_files(project_path)

    unused_dependencies = [
        pkg for pkg in dependencies if not is_package_used(pkg, dart_files)
    ]
    unused_dev_dependencies = [
        pkg for pkg in dev_dependencies if not is_package_used(pkg, dart_files)
    ]

    print("\n🎯 Unused dependencies in pubspec.yaml:")
    for pkg in unused_dependencies:
        print(f"{RED}- {pkg}{RESET}")

    print("\n🎯 Unused dev_dependencies in pubspec.yaml:")
    for pkg in unused_dev_dependencies:
        print(f"{RED}- {pkg}{RESET}")


def is_file_used(file, dart_files):
    for other_file in dart_files:
        if other_file != file:
            with open(other_file, "r", encoding="utf-8") as f:
                content = f.read()
                if os.path.basename(file).replace(".dart", "") in content:
                    return True
    return False


def find_unused_dart_files(project_path):
    dart_files = collect_dart_files(project_path)
    unused_dart_files = [
        file for file in dart_files if not is_file_used(file, dart_files)
    ]

    print("\n🗃️ Unused Dart files:")
    for idx, file in enumerate(unused_dart_files):
        print(f"{RED}- [{idx + 1}] {file}{RESET}")

    return unused_dart_files


def show_loading(message, duration=2):
    print(f"{CYAN}{message} {RESET}", end="")
    for _ in range(duration):
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(1)
    print("")


def prompt_delete_files(unused_files):
    choice = (
        input(f"\n{BOLD}Do you want to delete these unused files? (yes/no): {RESET}")
        .strip()
        .lower()
    )
    if choice == "yes":
        for file in unused_files:
            try:
                os.remove(file)
                print(f"{GREEN}Deleted: {file}{RESET}")
            except Exception as e:
                print(f"{RED}Error deleting {file}: {e}{RESET}")
    else:
        print(f"{YELLOW}No files were deleted.{RESET}")


def main():
    print(f"{BOLD}{YELLOW}=== 🚀 Flutter Project Analysis Tool 🚀 ==={RESET}")
    print(
        f"{BOLD}Welcome to the Flutter Project Analysis Tool! This tool helps you analyze your Flutter project to find and manage unused dependencies and Dart files.{RESET}"
    )

    # Get project path from user
    project_path = input(
        f"\n{BOLD}Enter the path to your Flutter project (press Enter for current directory):\n{RESET}"
    ).strip()

    if not project_path:
        project_path = os.getcwd()
        print(
            f"{YELLOW}No path entered. Defaulting to current directory: {project_path}{RESET}"
        )

    if not is_flutter_project(project_path):
        print(
            f"{RED}Error: The provided path '{project_path}' is not a valid Flutter project directory.{RESET}"
        )
        return

    # Get user choice
    print(f"\n{BOLD}{BLUE}Choose an option:{RESET}")
    print(f"{GREEN}1. Find unused Flutter packages{RESET}")
    print(f"{GREEN}2. Find unused Dart files{RESET}")
    print(f"{GREEN}3. Do both{RESET}")

    choice = input(f"{BOLD}Enter your choice (1, 2, or 3):\n{RESET}").strip()

    if choice == "1":
        show_loading("Finding unused Flutter packages")
        find_unused_packages(project_path)
    elif choice == "2":
        show_loading("Finding unused Dart files")
        unused_dart_files = find_unused_dart_files(project_path)
        if unused_dart_files:
            prompt_delete_files(unused_dart_files)
    elif choice == "3":
        show_loading("Finding unused Flutter packages and Dart files")
        find_unused_packages(project_path)
        unused_dart_files = find_unused_dart_files(project_path)
        if unused_dart_files:
            prompt_delete_files(unused_dart_files)
    else:
        print(f"{RED}Invalid choice. Please enter 1, 2, or 3.{RESET}")


if __name__ == "__main__":
    main()

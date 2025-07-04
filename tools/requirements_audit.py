import os
import ast
import argparse
import sys
import importlib.util

# Python built-in modules
BUILTINS = set(sys.builtin_module_names)

def find_imports(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return set()
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.add(name.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split(".")[0])
    return imports

def gather_project_imports(root_dir, exclude_dirs=None):
    all_imports = set()
    for folder, _, files in os.walk(root_dir):
        if exclude_dirs and any(ex in folder for ex in exclude_dirs):
            continue
        for file in files:
            if file.endswith(".py"):
                all_imports.update(find_imports(os.path.join(folder, file)))
    return sorted(all_imports)

def is_third_party(module):
    if module in BUILTINS or module == "__main__":
        return False
    try:
        spec = importlib.util.find_spec(module)
        return spec and "site-packages" in str(spec.origin)
    except (ValueError, AttributeError, ModuleNotFoundError):
        return False


def get_third_party_imports(imports):
    return sorted([mod for mod in imports if is_third_party(mod)])

def write_requirements(modules, output_file):
    with open(output_file, "w") as f:
        for mod in modules:
            f.write(f"{mod}\n")
    print(f"📦 Saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean Python requirements audit")
    parser.add_argument("--output", type=str, help="Write to requirements.txt")
    parser.add_argument("--exclude", nargs="*", default=["tools", "tests"], help="Folders to exclude")
    args = parser.parse_args()

    project_imports = gather_project_imports(".", exclude_dirs=args.exclude)
    third_party = get_third_party_imports(project_imports)

    print("✅ Third-party imports used in your project:")
    for mod in third_party:
        print(f"  - {mod}")

    if args.output:
        write_requirements(third_party, args.output)

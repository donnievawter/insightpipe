# 🧰 Dev Tools for InsightPipe

Welcome to the developer utility zone for InsightPipe. This folder contains standalone tools that support development, auditing, and maintenance—but are not part of the runtime pipeline.

---

## 📦 `requirements_audit.py`

Scans the project and identifies all third-party Python modules used across `.py` files.

### Features
- Recursively walks your project folders (excluding optional paths like `tools/`, `tests/`)
- Extracts imports from Python source files using AST parsing
- Filters out built-in modules and standard library components
- Cross-references with installed packages via `importlib.util`
- Outputs a deduplicated list of third-party modules
- Optional: Saves directly to `requirements.txt`

### Example Usage
```bash
python tools/requirements_audit.py --summary
python tools/requirements_audit.py --output requirements.txt
```
### Why It Exists
Keeps your `requirements.txt` accurate by reflecting actual project dependencies—not global environment clutter or unused pip packages.

---

## 🧭 Best Practices

These tools are:
- Executable scripts, **not packages**—no `__init__.py` required
- Optional helpers for maintenance and release prep
- Safe to modify or extend as InsightPipe evolves

If you add more utilities (e.g. model benchmarks, logging validators, EXIF scrubbers), document them here to keep this space clean and collaborative.

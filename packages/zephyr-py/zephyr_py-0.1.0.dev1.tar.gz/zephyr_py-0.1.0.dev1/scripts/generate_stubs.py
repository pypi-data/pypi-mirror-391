#!/usr/bin/env python3
"""
Stub file generation script for Zephyr framework and applications.

This script generates .pyi stub files for better type checking and IDE support.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List


def run_command(cmd: List[str], cwd: Path | None = None) -> bool:
    """Run a command and return success status."""
    try:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False


def generate_zephyr_stubs(output_dir: Path) -> bool:
    """Generate stub files for the Zephyr framework."""
    print("🔧 Generating Zephyr framework stubs...")
    
    zephyr_modules = [
        "zephyr",
        "zephyr.app",
        "zephyr.app.application", 
        "zephyr.app.requests",
        "zephyr.app.responses",
        "zephyr.app.routing",
        "zephyr.app.middleware",
        "zephyr.core",
        "zephyr.security",
        "zephyr.middleware",
    ]
    
    success = True
    for module in zephyr_modules:
        cmd = ["stubgen", "-p", module, "-o", str(output_dir)]
        if not run_command(cmd):
            print(f"⚠️  Failed to generate stubs for {module}")
            success = False
        else:
            print(f"✅ Generated stubs for {module}")
    
    return success


def generate_example_stubs(example_path: Path, output_dir: Path) -> bool:
    """Generate stub files for example applications."""
    print(f"📱 Generating stubs for example: {example_path.name}")
    
    if not example_path.exists():
        print(f"❌ Example path does not exist: {example_path}")
        return False
    
    # Find Python files to generate stubs for
    python_files = []
    for pattern in ["*.py", "**/*.py"]:
        python_files.extend(example_path.glob(pattern))
    
    # Filter out __pycache__ and test files
    python_files = [
        f for f in python_files 
        if "__pycache__" not in str(f) and not f.name.startswith("test_")
    ]
    
    if not python_files:
        print(f"⚠️  No Python files found in {example_path}")
        return True
    
    # Create example-specific output directory
    example_output = output_dir / example_path.name
    example_output.mkdir(parents=True, exist_ok=True)
    
    success = True
    for py_file in python_files:
        # Generate stub for individual file
        cmd = ["stubgen", str(py_file), "-o", str(example_output)]
        if not run_command(cmd):
            print(f"⚠️  Failed to generate stub for {py_file}")
            success = False
        else:
            print(f"✅ Generated stub for {py_file.name}")
    
    return success


def generate_taskflow_stubs(backend_path: Path, output_dir: Path) -> bool:
    """Generate stub files specifically for TaskFlow OIDC example."""
    print("🔐 Generating TaskFlow OIDC stubs...")
    
    if not backend_path.exists():
        print(f"❌ Backend path does not exist: {backend_path}")
        return False
    
    # Create taskflow-specific output directory
    taskflow_output = output_dir / "taskflow_oidc"
    taskflow_output.mkdir(parents=True, exist_ok=True)
    
    # Key modules to generate stubs for
    key_modules = [
        "app.py",
        "config.py", 
        "database.py",
        "auth/",
        "models/",
        "routes/"
    ]
    
    success = True
    for module in key_modules:
        module_path = backend_path / module
        if not module_path.exists():
            print(f"⚠️  Module not found: {module_path}")
            continue
        
        if module_path.is_file():
            cmd = ["stubgen", str(module_path), "-o", str(taskflow_output)]
        else:
            cmd = ["stubgen", "-p", module.rstrip("/"), "-o", str(taskflow_output)]
        
        if not run_command(cmd, cwd=backend_path):
            print(f"⚠️  Failed to generate stub for {module}")
            success = False
        else:
            print(f"✅ Generated stub for {module}")
    
    return success


def main():
    """Main entry point for stub generation."""
    parser = argparse.ArgumentParser(description="Generate stub files for Zephyr framework and applications")
    parser.add_argument(
        "--output-dir", 
        type=Path, 
        default=Path("stubs"),
        help="Output directory for stub files (default: stubs/)"
    )
    parser.add_argument(
        "--zephyr-only", 
        action="store_true",
        help="Generate only Zephyr framework stubs"
    )
    parser.add_argument(
        "--examples-only", 
        action="store_true",
        help="Generate only example application stubs"
    )
    parser.add_argument(
        "--taskflow-only", 
        action="store_true",
        help="Generate only TaskFlow OIDC example stubs"
    )
    parser.add_argument(
        "--clean", 
        action="store_true",
        help="Clean output directory before generating"
    )
    
    args = parser.parse_args()
    
    # Clean output directory if requested
    if args.clean and args.output_dir.exists():
        print(f"🧹 Cleaning output directory: {args.output_dir}")
        import shutil
        shutil.rmtree(args.output_dir)
    
    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Output directory: {args.output_dir.absolute()}")
    
    success = True
    
    # Generate Zephyr framework stubs
    if not args.examples_only and not args.taskflow_only:
        if not generate_zephyr_stubs(args.output_dir):
            success = False
    
    # Generate example stubs
    if not args.zephyr_only and not args.taskflow_only:
        examples_dir = Path("examples")
        if examples_dir.exists():
            for example_dir in examples_dir.iterdir():
                if example_dir.is_dir() and not example_dir.name.startswith("."):
                    if not generate_example_stubs(example_dir, args.output_dir):
                        success = False
    
    # Generate TaskFlow OIDC stubs specifically
    if args.taskflow_only or not (args.zephyr_only or args.examples_only):
        taskflow_backend = Path("examples/taskflow-oidc/backend")
        if taskflow_backend.exists():
            if not generate_taskflow_stubs(taskflow_backend, args.output_dir):
                success = False
    
    if success:
        print("\n🎉 Stub generation completed successfully!")
        print(f"📂 Stub files are available in: {args.output_dir.absolute()}")
        print("\n💡 Usage tips:")
        print("  - Add 'stubs/' to your IDE's Python path")
        print("  - Configure mypy to use the stubs directory")
        print("  - Import from stub files for better type checking")
    else:
        print("\n❌ Some stub generation failed. Check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

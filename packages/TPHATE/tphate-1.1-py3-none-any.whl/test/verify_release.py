#!/usr/bin/env python3
"""
Pre-release verification script for TPHATE v1.2.1
Run this script to verify all changes are correct before releasing to PyPI.
"""

import sys
import importlib.util
import subprocess
from pathlib import Path

def check_version():
    """Check that version is correctly set and accessible."""
    print("🔍 Checking version...")
    
    # Check version.py
    version_file = Path("tphate/version.py")
    if not version_file.exists():
        print("❌ tphate/version.py not found")
        return False
    
    with open(version_file) as f:
        content = f.read()
        if '__version__ = "1.2.1"' not in content:
            print("❌ Version not set to 1.2.1 in version.py")
            return False
    
    # Check that version is importable
    try:
        import tphate
        if tphate.__version__ != "1.2.1":
            print(f"❌ Import version mismatch: {tphate.__version__} != 1.2.1")
            return False
        print("✅ Version 1.2.1 correctly set and importable")
        return True
    except ImportError as e:
        print(f"❌ Cannot import tphate: {e}")
        return False

def check_dependencies():
    """Check that dependencies are correctly cleaned."""
    print("\n🔍 Checking dependencies...")
    
    setup_file = Path("setup.py")
    if not setup_file.exists():
        print("❌ setup.py not found")
        return False
    
    with open(setup_file) as f:
        content = f.read()
        
        # Check removed dependencies
        if '"phate"' in content or "'phate'" in content:
            print("❌ PHATE dependency still present in setup.py")
            return False
            
        if '"scprep' in content or "'scprep" in content:
            print("❌ SCPREP dependency still present in setup.py")
            return False
        
        # Check expected dependencies are present
        expected_deps = [
            "numpy>=1.16.0", "scipy>=1.1.0", "scikit-learn>=0.24",
            "tasklogger>=1.0", "graphtools>=1.5.3", "matplotlib>=3.0",
            "s_gd2>=1.8.1", "pygsp", "Deprecated"
        ]
        
        missing_deps = []
        for dep in expected_deps:
            if dep.split(">=")[0] not in content and dep.split("==")[0] not in content:
                missing_deps.append(dep)
        
        if missing_deps:
            print(f"❌ Missing dependencies: {missing_deps}")
            return False
    
    print("✅ Dependencies correctly cleaned (phate & scprep removed)")
    return True

def check_functionality():
    """Test core TPHATE functionality."""
    print("\n🔍 Testing core functionality...")
    
    try:
        import numpy as np
        import tphate
        
        # Create test data
        np.random.seed(42)
        data = np.random.randn(50, 10)
        
        # Test TPHATE embedding
        tphate_op = tphate.TPHATE(n_components=2, verbose=False)
        embedding = tphate_op.fit_transform(data)
        
        # Check result shape
        if embedding.shape != (50, 2):
            print(f"❌ Embedding shape incorrect: {embedding.shape} != (50, 2)")
            return False
        
        # Check attributes
        required_attrs = ['diff_op', 'autocorr_op', 'phate_diffop']
        for attr in required_attrs:
            if not hasattr(tphate_op, attr):
                print(f"❌ Missing attribute: {attr}")
                return False
        
        print("✅ Core functionality working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def check_tests():
    """Run unit tests."""
    print("\n🔍 Running unit tests...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", "test/", "-v", "--tb=short"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            print("❌ Tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
        
        print("✅ All tests pass")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Tests timed out")
        return False
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

def check_files():
    """Check for clean workspace and required files."""
    print("\n🔍 Checking file status...")
    
    # Check for build artifacts (ignore pytest cache as it's created during testing)
    build_dirs = ["build/", "dist/", "*.egg-info/", "__pycache__/"]
    found_artifacts = []
    
    for pattern in build_dirs:
        if pattern.endswith("/"):
            # Directory check
            if Path(pattern.rstrip("/")).exists():
                found_artifacts.append(pattern)
        else:
            # Glob check
            import glob
            if glob.glob(pattern):
                found_artifacts.extend(glob.glob(pattern))
    
    if found_artifacts:
        print(f"⚠️  Build artifacts found (should clean): {found_artifacts}")
    
    # Check required files
    required_files = [
        "setup.py", "tphate/__init__.py", "tphate/version.py", 
        "CHANGELOG.md", "RELEASE_GUIDE.md", "requirements.txt"
    ]
    
    missing_files = [f for f in required_files if not Path(f).exists()]
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    print("✅ All required files present")
    return len(found_artifacts) == 0

def main():
    """Run all verification checks."""
    print("=" * 60)
    print("TPHATE v1.2.1 Pre-Release Verification")
    print("=" * 60)
    
    checks = [
        ("Version Check", check_version),
        ("Dependencies Check", check_dependencies),
        ("Functionality Check", check_functionality),
        ("Unit Tests", check_tests),
        ("File Status", check_files),
    ]
    
    all_passed = True
    
    for name, check_func in checks:
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"❌ {name} failed with exception: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL CHECKS PASSED - Ready for release!")
        print("\nNext steps:")
        print("1. Review CHANGELOG.md")
        print("2. Follow RELEASE_GUIDE.md")
        print("3. Run: python setup.py sdist bdist_wheel")
        print("4. Run: twine upload dist/*")
    else:
        print("❌ SOME CHECKS FAILED - Fix issues before releasing")
        return 1
    
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())

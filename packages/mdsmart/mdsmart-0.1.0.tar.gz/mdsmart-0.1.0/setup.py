"""
Setup configuration for MDSmart package.

This setup builds Cython extension modules for the package to avoid
shipping readable .py source files in wheels. Source distribution (sdist)
will still contain sources; prefer uploading wheels only if you want to
hide code.
"""

from setuptools import find_packages, Extension
from setuptools.command.build_py import build_py as _build_py

try:
    from Cython.Build import cythonize
    CYTHON_AVAILABLE = True
except Exception:
    CYTHON_AVAILABLE = False


class build_py_no_pure(_build_py):
    """Skip copying .py modules into the wheel.

    We compile modules with Cython; this prevents pure Python sources
    from being included in the built wheel, leaving only compiled
    extension modules (.pyd/.so).
    """

    def find_package_modules(self, package, package_dir):
        # Return no pure-Python modules to build/copy
        return []


def _get_extensions():
    patterns = ["mdsmart/**/*.py"]
    exclude = ["mdsmart/tests/**", "mdsmart/examples/**", "mdsmart/__pycache__/**"]
    if CYTHON_AVAILABLE:
        return cythonize(
            patterns,
            exclude=exclude,
            language_level=3,
            compiler_directives={"binding": False, "embedsignature": False},
        )
    # Fallback: no extensions (source-only build)
    return []


# Use pyproject.toml as the single source of truth
from setuptools import setup

setup(
    ext_modules=_get_extensions(),
    cmdclass={"build_py": build_py_no_pure},
)

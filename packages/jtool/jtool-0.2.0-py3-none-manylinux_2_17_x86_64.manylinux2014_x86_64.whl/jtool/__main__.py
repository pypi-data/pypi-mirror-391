"""Entry point for jtool CLI - calls the Rust binary"""
import sys
import subprocess
from pathlib import Path


def find_binary():
    """Locate the jtool Rust binary bundled by maturin"""
    import jtool
    pkg_dir = Path(jtool.__file__).parent

    # Maturin places binaries in the package directory
    for name in ["jtool", "jtool.exe"]:
        binary = pkg_dir / name
        if binary.exists():
            return binary

    raise RuntimeError(f"jtool binary not found in {pkg_dir}")


def main():
    """Execute the jtool binary with the same arguments"""
    binary = find_binary()
    sys.exit(subprocess.call([str(binary)] + sys.argv[1:]))


if __name__ == "__main__":
    main()

"""Temporary file management utilities."""

import tempfile
import shutil
from pathlib import Path
from contextlib import contextmanager


class TempManager:
    """Manage temporary files and directories for md-convert."""

    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self._created_files = []

    def create_temp_file(self, suffix: str = "", prefix: str = "mdconvert_") -> Path:
        """Create a temporary file and track it for cleanup."""
        fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=self.temp_dir)
        import os
        os.close(fd)
        path = Path(path)
        self._created_files.append(path)
        return path

    def create_temp_dir(self, prefix: str = "mdconvert_") -> Path:
        """Create a temporary directory."""
        path = Path(tempfile.mkdtemp(prefix=prefix, dir=self.temp_dir))
        self._created_files.append(path)
        return path

    def cleanup(self):
        """Remove all tracked temporary files and directories."""
        for path in self._created_files:
            try:
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    shutil.rmtree(path)
            except Exception:
                pass
        self._created_files.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        return False


@contextmanager
def temp_file(suffix: str = "", prefix: str = "mdconvert_"):
    """Context manager for a temporary file that auto-cleans."""
    fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
    import os
    os.close(fd)
    path = Path(path)
    try:
        yield path
    finally:
        try:
            path.unlink()
        except Exception:
            pass


@contextmanager
def temp_dir(prefix: str = "mdconvert_"):
    """Context manager for a temporary directory that auto-cleans."""
    path = Path(tempfile.mkdtemp(prefix=prefix))
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)

"""Make Pillow 3 backward compatible with PIL again.

Pillow 3.0.0 removes, among others, Image.tostring().
This module provides a context manager, patch(), and a decorator,
patch_function(), to patch it back in.

"""

from contextlib import contextmanager
from functools import wraps

try:
    from PIL import Image
except ImportError:
    import Image


__all__ = ['patch', 'patch_function']


@contextmanager
def patch():
    """Make Pillow 3 backward compatible in the with-block."""
    old_tostring = Image.Image.tostring

    def patched_tostring(self, *args, **kwargs):
        try:
            result = old_tostring(self, *args, **kwargs)
        except Exception:
            result = self.tobytes(*args, **kwargs)
        return result

    Image.Image.tostring = patched_tostring

    try:
        yield
    finally:
        Image.Image.tostring = old_tostring

def patch_function(fn):
    """Make Pillow 3 backward compatible in the decorated function."""
    @wraps(fn)
    def patched_fn(*args, **kwargs):
        with patch():
            f(*args, **kwargs)

    return patched_fn

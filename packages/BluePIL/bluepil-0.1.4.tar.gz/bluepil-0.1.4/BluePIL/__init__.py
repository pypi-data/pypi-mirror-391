import weakref
from PIL import Image as PILImage
from PIL import *

_image_registry = set()

def _cleanup_image(img_id, img_close):
    _image_registry.discard(img_id)
    try:
        img_close()
    except:
        pass

class _AutoCloseImage(PILImage.Image):
    """Image subclass with automatic cleanup"""
    def __init__(self):
        super().__init__()
        img_id = id(self)
        _image_registry.add(img_id)
        self._finalizer = weakref.finalize(self, _cleanup_image, img_id, super().close)

PILImage.Image = _AutoCloseImage

Image = PILImage
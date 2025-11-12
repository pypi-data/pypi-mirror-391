import weakref
from PIL import Image as PILImage
from PIL.Image import *

_image_registry = set()


def _cleanup_image(img_id, img_close):
    _image_registry.discard(img_id)
    try:
        img_close()
    except:
        pass


class _ImageWrapper:
    def __init__(self, pil_image):
        self._img = pil_image
        img_id = id(self)
        _image_registry.add(img_id)
        self._finalizer = weakref.finalize(
            self, _cleanup_image, img_id, pil_image.close
        )

    def __getattr__(self, name):
        return getattr(self._img, name)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._img.close()

    def close(self):
        self._img.close()


def open(*args, **kwargs):
    pil_image = PILImage.open(*args, **kwargs)
    return _ImageWrapper(pil_image)


def new(*args, **kwargs):
    pil_image = PILImage.new(*args, **kwargs)
    return _ImageWrapper(pil_image)


def fromarray(*args, **kwargs):
    pil_image = PILImage.fromarray(*args, **kwargs)
    return _ImageWrapper(pil_image)


Image = type(
    "Image",
    (),
    {
        "open": staticmethod(open),
        "new": staticmethod(new),
        "fromarray": staticmethod(fromarray),
    },
)

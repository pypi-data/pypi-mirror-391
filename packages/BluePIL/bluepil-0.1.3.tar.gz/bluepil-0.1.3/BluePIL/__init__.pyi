from PIL.Image import Image as PILImage
from PIL import (
    ImageChops as ImageChops,
    ImageCms as ImageCms,
    ImageColor as ImageColor,
    ImageDraw as ImageDraw,
    ImageEnhance as ImageEnhance,
    ImageFile as ImageFile,
    ImageFilter as ImageFilter,
    ImageFont as ImageFont,
    ImageGrab as ImageGrab,
    ImageMath as ImageMath,
    ImageMode as ImageMode,
    ImageOps as ImageOps,
    ImagePalette as ImagePalette,
    ImagePath as ImagePath,
    ImageQt as ImageQt,
    ImageSequence as ImageSequence,
    ImageShow as ImageShow,
    ImageStat as ImageStat,
    ImageTk as ImageTk,
    ImageTransform as ImageTransform,
    ImageWin as ImageWin,
)

class Image:
    @staticmethod
    def open(fp, mode: str = ..., formats=...) -> PILImage: ...
    @staticmethod
    def new(mode: str, size, color=...) -> PILImage: ...
    @staticmethod
    def fromarray(obj, mode=...) -> PILImage: ...

def open(fp, mode: str = ..., formats=...) -> PILImage: ...
def new(mode: str, size, color=...) -> PILImage: ...
def fromarray(obj, mode=...) -> PILImage: ...

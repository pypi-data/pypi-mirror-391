from collections.abc import Iterator, Sequence
import enum
import os
from typing import Annotated, overload

from numpy.typing import ArrayLike


class Gmic:
    """G'MIC interpreter"""

    def __init__(self) -> None: ...

    def run(self, cmd: str, img_list: ImageList | None = None, img_names: StringList | None = None) -> ImageList: ...

    def __str__(self) -> str: ...

class GmicException(Exception):
    pass

class Image:
    """G'MIC Image"""

    @overload
    def __init__(self) -> None:
        """
        Construct an empty image. Beware that any attempt at reading the image will raise a RuntimeError

        Binds CImg<T>()
        """

    @overload
    def __init__(self, other: Image, is_shared: bool = False) -> None:
        """
        Copy or proxy existing image

        Binds CImg<T>(cimg_library::CImg<float>, bool)
        """

    @overload
    def __init__(self, width: int, height: int, depth: int = 0, channels: int, value: float = 0) -> None:
        """
        Construct image with specified size and initialize pixel values

        Binds CImg<T>(unsigned int, unsigned int, unsigned int, unsigned int, float)
        """

    @overload
    def __init__(self, width: int, height: int, depth: int, channels: int, value_string: str, repeat: bool) -> None:
        """
        Construct image with specified size and initialize pixel values from a value string

        Binds CImg<T>(unsigned int, unsigned int, unsigned int, unsigned int, char const*, bool)
        """

    @overload
    def __init__(self, filename: str | os.PathLike) -> None:
        """
        Construct image from reading an image file

        Binds CImg<T>(std::filesystem::__cxx11::path)
        """

    @overload
    def __init__(self, other: Image, dimensions: str) -> None:
        """
        Construct image with dimensions borrowed from another image

        Binds CImg<T>(cimg_library::CImg<float>, char const*)
        """

    @overload
    def __init__(self, array: Annotated[ArrayLike, dict(dtype='float32', device='cpu', writable=False)]) -> None:
        """
        Construct an image from an array-like object. Array are taken as xyzc, if it has less than 4, then the missing ones are assigned a size of 1.
        Be aware that most image processing libraries use a different order for dimensions (yxc), so this method will not work as expected with such libraries. Use Image.from_yxc(array) or img.yxc = array in that case.

        Binds CImg<T>(nanobind::ndarray<float const, nanobind::device::cpu>)
        """

    def __dlpack__(self, *, stream: int | Any | None = None, max_version: tuple[int, int] | None = None, dl_device: tuple[Enum, int] | None = None, copy: bool | None = None) → PyCapsule: ...

    def __dlpack_device__(self) -> tuple: ...

    @property
    def __array_interface__(self) -> object: ...

    def as_numpy(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(None, None, None, None), device='cpu')]:
        """Returns a writable view of the underlying data as a Numpy NDArray"""

    def to_numpy(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(None, None, None, None), device='cpu')]:
        """Returns a copy of the underlying data as a Numpy NDArray"""

    def at(self, x: int, y: int, z: int | None = None) -> tuple:
        """
        Returns a spectrum-sized (e.g 3 for RGB, 4 for RGBA) tuple, of the values at [x, y, z]. Z may be omitted if the image depth is 1.
        Negative values are relative to the end of the axis.
        """

    @property
    def shape(self) -> tuple[int, int, int, int]:
        """
        Returns the shape (size along each axis) tuple of the image in xyzc order
        """

    @property
    def strides(self) -> tuple[int, int, int, int]:
        """
        Returns the stride tuple (step size along each axis) of the image in xyzc order
        """

    @property
    def width(self) -> int:
        """Width (1st dimension) of the image"""

    @property
    def height(self) -> int:
        """Height (2nd dimension) of the image"""

    @property
    def depth(self) -> int:
        """Depth (3rd dimension) of the image"""

    @property
    def spectrum(self) -> int:
        """Spectrum (i.e. channels, 4th dimension) of the image"""

    @property
    def size(self) -> int:
        """Total number of values in the image (product of all dimensions)"""

    def __repr__(self) -> str: ...

    def __getitem__(self, arg: tuple, /) -> float:
        """
        Returns the value at the given coordinate. Takes between 2 and 4 arguments depending on image dimensions :
        - [x, y, z, c]
        - [x, y, c] if depth = 1
        - [x, y] if depth = 1 and spectrum = 1
        Value must be between -size and size-1 on the corresponding axis. Negative values are relative to the end of the axis.
        Raises a ValueError if condition is not met
        """

    def __pos__(self) -> Image:
        """Returns a copy of the image"""

    def __neg__(self) -> Image: ...

    def __eq__(self, arg: Image, /) -> bool: ...

    @overload
    def __add__(self, arg: Image, /) -> Image: ...

    @overload
    def __add__(self, arg: int, /) -> Image: ...

    @overload
    def __add__(self, arg: float, /) -> Image: ...

    @overload
    def __iadd__(self, arg: Image, /) -> Image: ...

    @overload
    def __iadd__(self, arg: int, /) -> Image: ...

    @overload
    def __iadd__(self, arg: float, /) -> Image: ...

    @overload
    def __sub__(self, arg: Image, /) -> Image: ...

    @overload
    def __sub__(self, arg: int, /) -> Image: ...

    @overload
    def __sub__(self, arg: float, /) -> Image: ...

    @overload
    def __isub__(self, arg: Image, /) -> Image: ...

    @overload
    def __isub__(self, arg: int, /) -> Image: ...

    @overload
    def __isub__(self, arg: float, /) -> Image: ...

    @overload
    def __mul__(self, arg: int, /) -> Image: ...

    @overload
    def __mul__(self, arg: float, /) -> Image: ...

    @overload
    def __imul__(self, arg: int, /) -> Image: ...

    @overload
    def __imul__(self, arg: float, /) -> Image: ...

    @overload
    def __truediv__(self, arg: int, /) -> Image: ...

    @overload
    def __truediv__(self, arg: float, /) -> Image: ...

    @overload
    def __itruediv__(self, arg: int, /) -> Image: ...

    @overload
    def __itruediv__(self, arg: float, /) -> Image: ...

    def fill(self, expression: str, repeat_values: bool = True, allow_formula: bool = True, list_images: "cimg_library::CImgList<float>" | None = None) -> Image:
        """
        Fills the image with the given value string. Like assign_dims_valstr with the image's current dimensions
        """

    def assign_empty(self) -> Image:
        """
        Construct an empty image. Beware that any attempt at reading the image will raise a RuntimeError

        Binds CImg<T>::assign()
        """

    def assign_copy(self, other: Image, is_shared: bool = False) -> Image:
        """
        Copy or proxy existing image

        Binds CImg<T>::assign(cimg_library::CImg<float>, bool)
        """

    def assign_dims(self, width: int, height: int, depth: int = 0, channels: int, value: float = 0) -> Image:
        """
        Construct image with specified size and initialize pixel values

        Binds CImg<T>::assign(unsigned int, unsigned int, unsigned int, unsigned int, float)
        """

    def assign_dims_valstr(self, width: int, height: int, depth: int, channels: int, value_string: str, repeat: bool) -> Image:
        """
        Construct image with specified size and initialize pixel values from a value string

        Binds CImg<T>::assign(unsigned int, unsigned int, unsigned int, unsigned int, char const*, bool)
        """

    def assign_load_file(self, filename: str | os.PathLike) -> Image:
        """
        Construct image from reading an image file

        Binds CImg<T>::assign(std::filesystem::__cxx11::path)
        """

    def assign_copy_dims(self, other: Image, dimensions: str) -> Image:
        """
        Construct image with dimensions borrowed from another image

        Binds CImg<T>::assign(cimg_library::CImg<float>, char const*)
        """

    def assign_ndarray(self, array: Annotated[ArrayLike, dict(dtype='float32', device='cpu', writable=False)]) -> Image:
        """
        Construct an image from an array-like object. Array are taken as xyzc, if it has less than 4, then the missing ones are assigned a size of 1.
        Be aware that most image processing libraries use a different order for dimensions (yxc), so this method will not work as expected with such libraries. Use Image.from_yxc(array) or img.yxc = array in that case.

        Binds CImg<T>::assign(nanobind::ndarray<float const, nanobind::device::cpu>)
        """

    class CastPolicy(enum.Enum):
        """Datatype casting policy for OOB (out-of-bounds) values"""

        CLAMP = 1
        """OOB values will be clamped to nearest bound (default)"""

        THROW = 0
        """Exception will be raised if any OOB value is found"""

        NOCHECK = 2
        """
        Disable checking for OOB values. Can increase performances at the risk of running into undefined behaviour on OOB values (see C++ rules for Floating-integral conversion).
        """

    CLAMP: Image.CastPolicy = Image.CastPolicy.CLAMP

    THROW: Image.CastPolicy = Image.CastPolicy.THROW

    NOCHECK: Image.CastPolicy = Image.CastPolicy.NOCHECK

    class YXCWrapper:
        """
        Wrapper around a gmic.Image to exchange with libraries using YXC axe order
        """

        dtypes: list[str] = ...
        """(arg: object, /) -> list[str]"""

        @property
        def image(self) -> Image: ...

        @property
        def z(self) -> int | None: ...

        @property
        def dtype(self) -> str: ...

        @property
        def cast_policy(self) -> Image.CastPolicy: ...

        def __getitem__(self, args: object) -> Image.YXCWrapper:
            """Sets the wrapper's z, target datatype and/or casting policy"""

        def __setitem__(self, arg0: object, arg1: object, /) -> None: ...

        def __dlpack__(self) -> Annotated[ArrayLike, dict(shape=(None, None, None), device='cpu', writable=False)]: ...

        def __dlpack_device__(self) -> tuple: ...

        @property
        def __array_interface__(self) -> object: ...

        def __repr__(self) -> str: ...

        def to_numpy(self) -> object:
            """Returns a copy of the underlying data as a Numpy NDArray"""

        def tobytes(self) -> object:
            """
            Returns the image data converted to the wrapper dtype as a bytes object
            """

        @property
        def shape(self) -> tuple[int, int, int]:
            """
            Returns the shape (size along each axis) tuple of the image in xyzc order
            """

        def assign(self, image: object, same_dims: bool = True) -> None:
            """
            Assigns the given object's data to the image. Object must be readable through either the buffer protocol, DLPack or the NumPy Array Interface
            """

    @property
    def yxc(self) -> Image.YXCWrapper:
        """Tuple[int | str | gmic.CastPolicy, ...]"""

    @yxc.setter
    def yxc(self, arg: object, /) -> None: ...

    @staticmethod
    def from_yxc(source: object) -> Image:
        """
        Constructs an image from the given object. Object must be readable through either the buffer protocol, DLPack or the NumPy Array Interface
        """

class ImageList:
    """List of G'MIC images"""

    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, arg: Sequence, /) -> None: ...

    def __iter__(self) -> Iterator[Image]: ...

    def __len__(self) -> int: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    def __getitem__(self, i: int) -> Image: ...

    def __setitem__(self, i: int, v: Image) -> None: ...

class StringList:
    """List of strings"""

    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, arg: Sequence, /) -> None: ...

    def __iter__(self) -> Iterator[str]: ...

    def __len__(self) -> int: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    def __getitem__(self, i: int) -> str: ...

    def __setitem__(self, i: int, v: str) -> None: ...

__build__: str = 'Built on Nov 13 2025 at 16:04:36'

__build_flags__: dict = ...

__pyversion__: str = '3.6.3.post1'

def run(cmd: str, img_list: ImageList | None = None, img_names: StringList | None = None) -> ImageList: ...

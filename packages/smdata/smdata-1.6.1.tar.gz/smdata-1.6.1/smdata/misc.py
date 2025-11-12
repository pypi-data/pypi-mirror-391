import typing
import ctypes


# ==-----------------------------------------------------------------------------== #
# Classes                                                                           #
# ==-----------------------------------------------------------------------------== #
class WinMutex:
    """Windows system mutex to make cross-process communication safe and consistent."""

    def __init__(self, name: str, is_global: bool = True) -> None:
        """Creates new mutex with given name or gets existing if it already existed."""

        # Mutex initialization
        if not (handle := ctypes.windll.kernel32.CreateMutexW(None, False, ("Global\\" if is_global else str()) + name)):
            raise Exception("Unable to retrieve mutex handle")

        # Class instance attributes
        self.handle = handle

    def __enter__(self) -> None:
        """Context manager opening overloading."""

        ctypes.windll.kernel32.WaitForSingleObject(self.handle, -1)

    def __exit__(self, exception_type: BaseException | None, exception_value: BaseException | None, traceback: typing.Any) -> None:
        """Context manager closing overloading."""

        # Mutex closing
        ctypes.windll.kernel32.ReleaseMutex(self.handle)


class PosixMutex:
    """Windows system mutex to make cross-process communication safe and consistent."""

    def __init__(self, name: str, is_global: bool = True) -> None:
        """Creates new mutex with given name or gets existing if it already existed."""

        # LibC loading
        self.libc = ctypes.CDLL("libc.so.6")

        # Mutex initialization
        if not (handle := self.libc.sem_open((("Global\\" if is_global else str()) + name).encode(), 0x200, 0o666, 1)) == -1:
            raise Exception("Unable to retrieve mutex handle")

        self.handle = handle

    def __enter__(self) -> None:
        """Context manager opening overloading."""

        self.libc.sem_wait(self.handle)

    def __exit__(self, exception_type: BaseException | None, exception_value: BaseException | None, traceback: typing.Any) -> None:
        """Context manager closing overloading."""

        # Mutex closing
        self.libc.sem_post(self.handle)


# ==-----------------------------------------------------------------------------== #
# Functions                                                                         #
# ==-----------------------------------------------------------------------------== #
def is_process_admin() -> bool:
    """Checks is process started with admin rights."""

    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())

    except Exception:
        return False

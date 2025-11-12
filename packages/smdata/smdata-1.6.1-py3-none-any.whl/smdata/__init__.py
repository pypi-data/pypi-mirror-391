import re
import sys
import typing
import ctypes
import contextlib
import multiprocessing
import multiprocessing.shared_memory

# Package local import
from .misc import *
from .serealizers import *


# ==-----------------------------------------------------------------------------== #
# Classes                                                                           #
# ==-----------------------------------------------------------------------------== #
class Dict:
    """Dictionary located at shared named memory of OS. Can be acessed by any other process."""

    # ==-----------------------------------------------------------------------------== #
    # Method                                                                            #
    # ==-----------------------------------------------------------------------------== #
    def __init__(self, name: str, file_mapping_size: str = "8M", oninit_content: dict = dict(), is_global: bool = True, serealizer: Serealizer = OrjsonSerealizer()) -> None:
        """Creates or gets named shared memory dictionary."""

        # Check process started with admin right
        if is_global and not is_process_admin():
            raise Exception("Global shared memory accessable only with admin rights")

        # Check file mapping size is valid
        if not re.match(file_mapping_size_pattern := r"^(\d+)(?i:b|k|m|g)$", file_mapping_size):
            raise Exception("Invalid file mapping size `%s`, have to valdidate `%s` pattern" % (file_mapping_size, file_mapping_size_pattern))

        # Class instance attributes
        self.__mutex = WinMutex(name + "_mutex_", is_global=is_global) if sys.platform == "win32" else PosixMutex(name, is_global=is_global)
        self.serealizer = serealizer

        # Retriveing memory size in bytes
        self.memory_size_bytes = int(file_mapping_size[:-1]) * {"b": 1, "k": 1024, "m": 1024**2, "g": 1024**3, "t": 1024**4}[file_mapping_size[-1].lower()] + 8

        # IF memory size is zero
        if self.memory_size_bytes <= 8:
            raise Exception("File mapping size to be greater that `0`")

        # Memory allocating and initialization
        with self.__mutex:

            # Allocating new memory or geting already created
            self.memory = self.__get_or_alloc_memory(("Global\\" if is_global else str()) + name, self.memory_size_bytes)

            # Check if memory inited
            self.__init_memory(oninit_content)

    @contextlib.contextmanager
    def access(self, read_only: bool = False) -> typing.Generator[dict, None, None]:
        """Creates context to safely operate with dict avoiding `read-modify-write` problem."""

        # Mutex acquire
        with self.__mutex:

            # Read and modify current dict
            yield (current_dict := self.__read_dict())

            # Update new dict
            if not read_only:
                self.__write_dict(current_dict)

    # ==-----------------------------------------------------------------------------== #
    # Private Methods                                                                   #
    # ==-----------------------------------------------------------------------------== #
    def __write_dict(self, value: dict) -> None:
        """Serealizes dict and writes it to the named shared memory."""

        # Write serealized value into named shared memory
        self.memory.buf[:8 + len(serealized_value)] = bytes(ctypes.c_uint64(len(serealized_value := self.serealizer.dumps(value)))) + serealized_value

    def __read_dict(self) -> dict:
        """Reads bytestring from named shared memory and deserealizes it to dict."""

        # Read bytesting and deserealizing it as dict
        return self.serealizer.loads(self.memory.buf[8:8 + ctypes.c_uint64.from_buffer_copy(self.memory.buf[:8]).value])

    def __get_or_alloc_memory(self, name: str, size_bytes: int) -> multiprocessing.shared_memory.SharedMemory:
        """Tries to get named shared memory, allocated buffer if if doesn't exists."""

        try:
            return multiprocessing.shared_memory.SharedMemory(name)

        except Exception:
            return multiprocessing.shared_memory.SharedMemory(name, create=True, size=size_bytes)

    def __init_memory(self, content: dict = dict()) -> None:
        """Inits named shared memory with Python dict."""

        # Check memory buffer is empty
        if not ctypes.c_uint64.from_buffer_copy(self.memory.buf[:8]).value:
            self.__write_dict(content)

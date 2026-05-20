"""
MemoryPatcher: Handles low-level memory operations for the Atomic Heart process.
Uses ctypes to read/write process memory on Windows.
"""

import ctypes
import ctypes.wintypes
from typing import Optional


class MemoryPatcher:
    """Attaches to a target process and provides memory read/write utilities."""

    def __init__(self, process_name: str):
        self.process_name = process_name
        self.process_handle: Optional[int] = None
        self._open_process()

    def _open_process(self) -> None:
        """Find and open a handle to the target process by name."""
        kernel32 = ctypes.windll.kernel32
        # Snapshot of processes
        CreateToolhelp32Snapshot = kernel32.CreateToolhelp32Snapshot
        Process32First = kernel32.Process32First
        Process32Next = kernel32.Process32Next
        CloseHandle = kernel32.CloseHandle

        # Process entry structure
        class PROCESSENTRY32(ctypes.Structure):
            _fields_ = [
                ("dwSize", ctypes.wintypes.DWORD),
                ("cntUsage", ctypes.wintypes.DWORD),
                ("th32ProcessID", ctypes.wintypes.DWORD),
                ("th32DefaultHeapID", ctypes.POINTER(ctypes.wintypes.ULONG)),
                ("th32ModuleID", ctypes.wintypes.DWORD),
                ("cntThreads", ctypes.wintypes.DWORD),
                ("th32ParentProcessID", ctypes.wintypes.DWORD),
                ("pcPriClassBase", ctypes.wintypes.LONG),
                ("dwFlags", ctypes.wintypes.DWORD),
                ("szExeFile", ctypes.c_char * 260),
            ]

        snapshot = CreateToolhelp32Snapshot(0x00000002, 0)  # TH32CS_SNAPPROCESS
        if snapshot == -1:
            raise RuntimeError("Failed to create process snapshot")

        pe = PROCESSENTRY32()
        pe.dwSize = ctypes.sizeof(PROCESSENTRY32)

        if Process32First(snapshot, ctypes.byref(pe)):
            while True:
                if pe.szExeFile.decode("utf-8", errors="ignore") == self.process_name:
                    pid = pe.th32ProcessID
                    break
                if not Process32Next(snapshot, ctypes.byref(pe)):
                    CloseHandle(snapshot)
                    raise RuntimeError(f"Process '{self.process_name}' not found")
        else:
            CloseHandle(snapshot)
            raise RuntimeError("Failed to enumerate processes")

        CloseHandle(snapshot)

        # Open process with required access
        PROCESS_ALL_ACCESS = 0x1F0FFF
        self.process_handle = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
        if not self.process_handle:
            raise RuntimeError("Failed to open process handle (run as admin?)")

    def read_memory(self, address: int, size: int) -> bytes:
        """Read bytes from process memory."""
        buffer = ctypes.create_string_buffer(size)
        bytes_read = ctypes.c_size_t(0)
        kernel32 = ctypes.windll.kernel32
        if not kernel32.ReadProcessMemory(
            self.process_handle,
            ctypes.c_void_p(address),
            buffer,
            size,
            ctypes.byref(bytes_read),
        ):
            raise RuntimeError(f"Failed to read memory at 0x{address:X}")
        return buffer.raw[:bytes_read.value]

    def write_memory(self, address: int, data: bytes) -> None:
        """Write bytes to process memory."""
        kernel32 = ctypes.windll.kernel32
        bytes_written = ctypes.c_size_t(0)
        if not kernel32.WriteProcessMemory(
            self.process_handle,
            ctypes.c_void_p(address),
            data,
            len(data),
            ctypes.byref(bytes_written),
        ):
            raise RuntimeError(f"Failed to write memory at 0x{address:X}")

    def close(self) -> None:
        """Close the process handle."""
        if self.process_handle:
            ctypes.windll.kernel32.CloseHandle(self.process_handle)
            self.process_handle = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

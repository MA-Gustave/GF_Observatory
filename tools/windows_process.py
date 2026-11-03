"""Windows subprocess creation policy for Observatory's background operations.

The GUI intentionally captures process output to its own logs; a child console
is never useful. CREATE_NO_WINDOW suppresses the extra Windows command window
whether the child is python.exe, gf.exe or taskkill.exe. The option is not passed
on POSIX systems. Keep process group behaviour for the WordBench timeout path.
"""
from __future__ import annotations

import os
import subprocess

# Numeric fallbacks make the policy testable on Linux without pretending that
# Windows-only subprocess attributes are present there.
_CREATE_NO_WINDOW = 0x08000000
_CREATE_NEW_PROCESS_GROUP = 0x00000200


def background_process_options(
    *, new_process_group: bool = False, windows: bool | None = None
) -> dict[str, int | bool]:
    """Return portable Popen/run keyword options for a background child.

    On Windows: never allocate a visible console. On POSIX: preserve the
    existing new-session behaviour for cancellable processes.
    """
    is_windows = (os.name == "nt") if windows is None else windows
    if is_windows:
        flags = getattr(subprocess, "CREATE_NO_WINDOW", _CREATE_NO_WINDOW)
        if new_process_group:
            flags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", _CREATE_NEW_PROCESS_GROUP)
        return {"creationflags": flags}
    return {"start_new_session": True} if new_process_group else {}

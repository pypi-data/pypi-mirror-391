"""liru - High-performance Python wrapper for Spout 2.007 GPU texture sharing.

liru provides zero-copy GPU texture sharing between Python processes using
Spout 2.007's DirectX shared texture mechanism.

Example:
    >>> import moderngl
    >>> import liru
    >>> ctx = moderngl.create_context()
    >>> texture = ctx.texture((1920, 1080), 4)
    >>> sender = liru.Sender("MySource", 1920, 1080)
    >>> sender.send_texture(texture.glo)
"""

import sys

# Platform check: liru requires Windows (Spout uses DirectX 11)
if sys.platform != "win32":
    raise ImportError(
        f"liru is only supported on Windows (current platform: {sys.platform}). "
        "liru requires Spout 2.007 which depends on DirectX 11. "
        "For macOS, consider using Syphon instead."
    )

from liru.__version__ import __version__
from liru.receiver import Receiver
from liru.sender import Sender

__all__ = ["Sender", "Receiver", "__version__"]

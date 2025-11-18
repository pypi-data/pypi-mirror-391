"""Spout sender implementation."""

from __future__ import annotations

import types

try:
    from . import _liru_core  # type: ignore[import-not-found,attr-defined]
except ImportError as e:
    raise ImportError(
        "Failed to import _liru_core extension. "
        "Ensure liru is properly installed with: pip install liru"
    ) from e


class Sender:
    """Spout sender for sharing GPU textures.

    Wraps a Spout sender that shares OpenGL textures with other processes
    via DirectX shared texture handles.

    Args:
        name: Unique sender name (visible to receivers)
        width: Texture width in pixels
        height: Texture height in pixels

    Raises:
        ValueError: If name is empty or dimensions are invalid
        RuntimeError: If sender creation fails

    Example:
        >>> import moderngl
        >>> import liru
        >>> ctx = moderngl.create_context()
        >>> texture = ctx.texture((1920, 1080), 4)
        >>> sender = liru.Sender("MySource", 1920, 1080)
        >>> sender.send_texture(texture.glo)
        >>> print(f"FPS: {sender.get_fps():.1f}")
    """

    def __init__(self, name: str, width: int, height: int) -> None:
        """Initialize Spout sender.

        Args:
            name: Unique sender name
            width: Texture width in pixels
            height: Texture height in pixels

        Raises:
            ValueError: If name is empty or dimensions are invalid
            RuntimeError: If sender creation fails
        """
        if not name:
            raise ValueError("Sender name cannot be empty")
        if width <= 0 or height <= 0:
            raise ValueError(f"Invalid dimensions: {width}x{height}")

        try:
            self._impl = _liru_core.SenderWrapper(name, width, height)
        except RuntimeError as e:
            raise RuntimeError(f"Failed to create sender '{name}': {e}") from e

        self._name = name
        self._width = width
        self._height = height
        self._released = False

    def send_texture(self, texture_id: int) -> None:
        """Send OpenGL texture via Spout.

        Shares the texture with receivers using DirectX shared handles.
        The texture must be a valid OpenGL texture ID from the current context.

        Args:
            texture_id: OpenGL texture ID (e.g., from texture.glo in ModernGL)

        Raises:
            ValueError: If texture_id is invalid
            RuntimeError: If send operation fails or sender already released

        Example:
            >>> texture = ctx.texture((1920, 1080), 4)
            >>> sender.send_texture(texture.glo)
        """
        if self._released:
            raise RuntimeError("Sender has been released and cannot be used")
        if texture_id <= 0:
            raise ValueError(f"Invalid texture ID: {texture_id}")

        try:
            if not self._impl.send_texture(texture_id):
                raise RuntimeError("Failed to send texture")
        except Exception as e:
            raise RuntimeError(f"Texture send error: {e}") from e

    def release(self) -> None:
        """Release Spout sender resources.

        Should be called when done sending. The sender cannot be used after release.

        Example:
            >>> sender.release()
        """
        if not self._released and hasattr(self, "_impl"):
            self._impl.release()
            self._released = True

    def get_fps(self) -> float:
        """Get current frames per second.

        Returns rolling average FPS over recent frames.

        Returns:
            Current FPS as a float

        Example:
            >>> fps = sender.get_fps()
            >>> print(f"Sending at {fps:.1f} FPS")
        """
        fps: float = self._impl.get_fps()
        return fps

    @property
    def last_send_time_ms(self) -> float:
        """Get last send latency in milliseconds.

        Returns:
            Time taken for last send_texture() call in milliseconds

        Example:
            >>> sender.send_texture(texture.glo)
            >>> print(f"Send latency: {sender.last_send_time_ms:.3f}ms")
        """
        latency: float = self._impl.get_last_send_time_ms()
        return latency

    @property
    def name(self) -> str:
        """Get sender name.

        Returns:
            Sender name
        """
        return self._name

    @property
    def width(self) -> int:
        """Get texture width.

        Returns:
            Width in pixels
        """
        return self._width

    @property
    def height(self) -> int:
        """Get texture height.

        Returns:
            Height in pixels
        """
        return self._height

    def __enter__(self) -> Sender:
        """Enter context manager.

        Returns:
            Self for use in with statement

        Example:
            >>> with liru.Sender("MySource", 1920, 1080) as sender:
            ...     sender.send_texture(texture.glo)
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Exit context manager and release resources.

        Args:
            exc_type: Exception type if an error occurred
            exc_val: Exception value if an error occurred
            exc_tb: Exception traceback if an error occurred
        """
        self.release()

    def __repr__(self) -> str:
        """Get string representation.

        Returns:
            String representation of sender
        """
        return f"Sender(name='{self._name}', size={self._width}x{self._height})"

    def __del__(self) -> None:
        """Cleanup on deletion."""
        # Only issue warning and release if initialization completed successfully
        if not hasattr(self, "_released"):
            return  # __init__ failed before setting _released

        if not self._released:
            import warnings

            name = self._name if hasattr(self, "_name") else "unknown"
            warnings.warn(
                f"Sender '{name}' was not explicitly released. "
                "Call sender.release() or use 'with' statement for proper cleanup.",
                ResourceWarning,
                stacklevel=2,
            )
        self.release()

"""Spout receiver implementation."""

from __future__ import annotations

import types

try:
    from . import _liru_core  # type: ignore[import-not-found,attr-defined]
except ImportError as e:
    raise ImportError(
        "Failed to import _liru_core extension. "
        "Ensure liru is properly installed with: pip install liru"
    ) from e


class Receiver:
    """Spout receiver for receiving GPU textures.

    Wraps a Spout receiver that receives OpenGL textures from senders
    via DirectX shared texture handles.

    Args:
        sender_name: Name of sender to connect to (optional, can connect later)

    Raises:
        RuntimeError: If receiver creation fails

    Example:
        >>> import moderngl
        >>> import liru
        >>> ctx = moderngl.create_context()
        >>> receiver = liru.Receiver("MySource")
        >>> texture = ctx.texture((1, 1), 4)  # Placeholder
        >>> if receiver.is_updated():
        ...     width, height = receiver.receive_texture(texture.glo)
    """

    def __init__(self, sender_name: str | None = None) -> None:
        """Initialize Spout receiver.

        Args:
            sender_name: Name of sender to connect to (optional)

        Raises:
            RuntimeError: If receiver creation fails
        """
        try:
            self._impl = _liru_core.ReceiverWrapper(sender_name or "")
        except RuntimeError as e:
            raise RuntimeError(f"Failed to create receiver: {e}") from e

    def receive_texture(self, texture_id: int) -> tuple[int, int]:
        """Receive texture from Spout sender.

        Updates the specified OpenGL texture with content from the sender.
        The texture must exist in the current OpenGL context.

        Args:
            texture_id: OpenGL texture ID to receive into

        Returns:
            Tuple of (width, height) of received texture

        Raises:
            ValueError: If texture_id is invalid
            RuntimeError: If receive operation fails

        Example:
            >>> texture = ctx.texture((1920, 1080), 4)
            >>> width, height = receiver.receive_texture(texture.glo)
            >>> print(f"Received {width}x{height} texture")
        """
        if texture_id <= 0:
            raise ValueError(f"Invalid texture ID: {texture_id}")

        try:
            result: tuple[int, int] = self._impl.receive_texture(texture_id)
            return result
        except Exception as e:
            raise RuntimeError(f"Texture receive error: {e}") from e

    def is_updated(self) -> bool:
        """Check if new frame is available.

        Returns:
            True if sender has new frame available

        Example:
            >>> if receiver.is_updated():
            ...     receiver.receive_texture(texture.glo)
        """
        updated: bool = self._impl.is_updated()
        return updated

    def select_sender(self, name: str) -> None:
        """Connect to a different sender.

        Args:
            name: Name of sender to connect to

        Raises:
            ValueError: If name is empty
            RuntimeError: If connection fails

        Example:
            >>> receiver.select_sender("AnotherSource")
        """
        if not name:
            raise ValueError("Sender name cannot be empty")

        try:
            self._impl.select_sender(name)
        except Exception as e:
            raise RuntimeError(f"Failed to select sender '{name}': {e}") from e

    def get_sender_list(self) -> list[str]:
        """Get list of available Spout senders.

        Returns:
            List of sender names currently broadcasting

        Example:
            >>> senders = receiver.get_sender_list()
            >>> print(f"Available senders: {senders}")
        """
        senders: list[str] = self._impl.get_sender_list()
        return senders

    @property
    def active_sender(self) -> str:
        """Get name of currently connected sender.

        Returns:
            Active sender name (empty string if not connected)
        """
        sender: str = self._impl.get_active_sender()
        return sender

    @property
    def width(self) -> int:
        """Get current texture width.

        Returns:
            Width in pixels (0 if not connected)
        """
        width: int = self._impl.get_width()
        return width

    @property
    def height(self) -> int:
        """Get current texture height.

        Returns:
            Height in pixels (0 if not connected)
        """
        height: int = self._impl.get_height()
        return height

    @property
    def last_receive_time_ms(self) -> float:
        """Get last receive latency in milliseconds.

        Returns:
            Time taken for last receive_texture() call in milliseconds

        Example:
            >>> receiver.receive_texture(texture.glo)
            >>> print(f"Receive latency: {receiver.last_receive_time_ms:.3f}ms")
        """
        latency: float = self._impl.get_last_receive_time_ms()
        return latency

    def __enter__(self) -> Receiver:
        """Enter context manager.

        Returns:
            Self for use in with statement

        Example:
            >>> with liru.Receiver("MySource") as receiver:
            ...     if receiver.is_updated():
            ...         receiver.receive_texture(texture.glo)
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Exit context manager.

        Args:
            exc_type: Exception type if an error occurred
            exc_val: Exception value if an error occurred
            exc_tb: Exception traceback if an error occurred

        Note:
            Receiver cleanup is handled by C++ destructor, no explicit release needed.
        """
        # Receiver cleanup handled by C++ destructor
        pass

    def __repr__(self) -> str:
        """Get string representation.

        Returns:
            String representation of receiver
        """
        sender = self.active_sender or "not connected"
        return f"Receiver(sender='{sender}', size={self.width}x{self.height})"

    def __del__(self) -> None:
        """Cleanup on deletion."""
        # Receiver cleanup handled by C++ destructor
        pass

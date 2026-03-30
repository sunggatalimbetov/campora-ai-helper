from __future__ import annotations

import asyncio
import time

from telegram import Message
from telegram.error import BadRequest, RetryAfter


class StreamingResponder:
    """Progressively edits a Telegram message with streamed text chunks.

    Handles throttling (to respect Telegram rate limits), message splitting
    (when text exceeds the 4096-char limit), and final formatting.
    """

    EDIT_INTERVAL = 1.5  # minimum seconds between edits
    SAFE_LENGTH = 3800  # split before hitting 4096 limit
    CURSOR = " \u258d"  # ▍ typing cursor shown during streaming

    def __init__(self, message: Message) -> None:
        self._message = message
        self._messages: list[Message] = [message]
        self._buffer = ""
        self._last_edit_time = 0.0

    async def push(self, delta: str) -> None:
        """Append a text delta and flush to Telegram if enough time has passed."""
        self._buffer += delta
        await self._maybe_flush()

    async def _maybe_flush(self) -> None:
        now = time.monotonic()
        if now - self._last_edit_time < self.EDIT_INTERVAL:
            return

        # If buffer is getting long, finalize current message and start a new one
        if len(self._buffer) > self.SAFE_LENGTH:
            split_at = self._buffer.rfind("\n", 0, self.SAFE_LENGTH)
            if split_at <= 0:
                split_at = self._buffer.rfind(" ", 0, self.SAFE_LENGTH)
            if split_at <= 0:
                split_at = self.SAFE_LENGTH

            finalize_text = self._buffer[:split_at]
            self._buffer = self._buffer[split_at:].lstrip()

            await self._edit(self._message, finalize_text)
            self._message = await self._message.reply_text(self._buffer + self.CURSOR)
            self._messages.append(self._message)
            self._last_edit_time = now
            return

        await self._edit(self._message, self._buffer + self.CURSOR)
        self._last_edit_time = now

    async def finalize(self, references: str = "", keyboard=None) -> None:
        """Remove cursor, append references, apply Markdown, and attach keyboard."""
        # Flush any remaining buffer that hasn't been sent yet
        if len(self._buffer) > self.SAFE_LENGTH and references:
            # Buffer is long and we still need to add references — split first
            split_at = self._buffer.rfind("\n", 0, self.SAFE_LENGTH)
            if split_at <= 0:
                split_at = self._buffer.rfind(" ", 0, self.SAFE_LENGTH)
            if split_at <= 0:
                split_at = self.SAFE_LENGTH

            finalize_text = self._buffer[:split_at]
            self._buffer = self._buffer[split_at:].lstrip()

            await self._edit(self._message, finalize_text)
            self._message = await self._message.reply_text("...")
            self._messages.append(self._message)

        final_text = self._buffer + references
        # If final text is too long, split it
        if len(final_text) > self.SAFE_LENGTH:
            split_at = self._buffer.rfind("\n", 0, self.SAFE_LENGTH)
            if split_at <= 0:
                split_at = self._buffer.rfind(" ", 0, self.SAFE_LENGTH)
            if split_at <= 0:
                split_at = self.SAFE_LENGTH

            await self._edit(self._message, self._buffer[:split_at])
            remainder = self._buffer[split_at:].lstrip() + references
            self._message = await self._message.reply_text("...")
            self._messages.append(self._message)
            final_text = remainder

        kwargs = {"reply_markup": keyboard} if keyboard else {}
        try:
            await self._message.edit_text(final_text, parse_mode="Markdown", **kwargs)
        except BadRequest:
            await self._edit(self._message, final_text, **kwargs)

    async def _edit(self, message: Message, text: str, **kwargs) -> None:
        """Edit a message with RetryAfter handling."""
        if not text.strip():
            return
        try:
            await message.edit_text(text, **kwargs)
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
            try:
                await message.edit_text(text, **kwargs)
            except Exception:
                pass  # skip this edit; next flush will include accumulated text
        except BadRequest:
            pass  # message unchanged or other non-critical error

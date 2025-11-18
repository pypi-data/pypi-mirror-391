import time

from biolib.biolib_binary_format.utils import IndexableBuffer
from biolib.biolib_logging import logger
from biolib.typing_utils import Iterable


class StreamSeeker:
    def __init__(
            self,
            upstream_buffer: IndexableBuffer,
            files_data_start: int,
            files_data_end: int,
            max_chunk_size: int,
    ):
        self._upstream_buffer = upstream_buffer
        self._files_data_end = files_data_end
        self._download_chunk_size_in_bytes = 100_000
        self._min_chunk_size = min(100_000, max_chunk_size)
        self._max_chunk_size = max_chunk_size
        self._target_download_time_seconds = 1.0

        self._buffer_start = files_data_start
        self._buffer = bytearray()

    def seek_and_read(self, file_start: int, file_length: int) -> Iterable[bytes]:
        assert file_start >= self._buffer_start
        self._buffer = self._buffer[file_start - self._buffer_start:]  # Returns empty array if "out of bounds"
        self._buffer_start = file_start

        while True:
            file_byte_count_remaining = file_length - (self._buffer_start - file_start)
            if file_byte_count_remaining == 0:
                return

            start_of_fetch = self._buffer_start + len(self._buffer)
            byte_count_left_in_stream = self._files_data_end - start_of_fetch

            if byte_count_left_in_stream != 0:
                # Only fetch if there is still data left upstream
                if self._download_chunk_size_in_bytes > len(self._buffer):
                    # Only fetch if size of buffer is below chunk size
                    fetch_size = min(byte_count_left_in_stream, self._download_chunk_size_in_bytes)

                    start_time = time.monotonic()
                    fetched_data = self._upstream_buffer.get_data(
                        start=start_of_fetch,
                        length=fetch_size,
                    )
                    download_time = time.monotonic() - start_time

                    self._buffer.extend(fetched_data)

                    if download_time > 0:
                        self._adjust_chunk_size(download_time, fetch_size)

            bytes_to_yield = self._buffer[:file_byte_count_remaining]  # Returns empty array if "out of bounds"
            yield bytes_to_yield
            self._buffer = self._buffer[file_byte_count_remaining:]  # Returns empty array if "out of bounds"
            self._buffer_start += len(bytes_to_yield)

    def _adjust_chunk_size(self, download_time: float, _bytes_downloaded: int) -> None:
        new_chunk_size = self._download_chunk_size_in_bytes
        time_ratio = download_time / self._target_download_time_seconds

        if time_ratio > 1.1:
            adjustment_factor = 1.0 / time_ratio
            adjustment_factor = max(adjustment_factor, 0.5)
            new_chunk_size = int(self._download_chunk_size_in_bytes * adjustment_factor)
        elif time_ratio < 0.9:
            adjustment_factor = 1.0 / time_ratio
            new_chunk_size = int(self._download_chunk_size_in_bytes * adjustment_factor)

        new_chunk_size = max(
            self._min_chunk_size,
            min(self._max_chunk_size, new_chunk_size)
        )

        if new_chunk_size != self._download_chunk_size_in_bytes:
            logger.debug(
                f"Adjusting chunk size: {self._download_chunk_size_in_bytes} -> {new_chunk_size} bytes "
                f"(download_time={download_time:.2f}s, time_ratio={time_ratio:.2f})"
            )
            self._download_chunk_size_in_bytes = new_chunk_size

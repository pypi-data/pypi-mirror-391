"""Smu logger with bounded queue and file-per-day writer (patched with RotatingFileHandler).

- Stores timestamps in UTC (ISO) and epoch ms.
- Uses a bounded queue between poller (producer) and writer (consumer).
- Writer creates a new file per UTC date: device-YYYY-MM-DD.csv and writes header if needed.
- Debug logging uses RotatingFileHandler (size-based rotation).
- Graceful shutdown: stop(), join(), flush queue, close files and handlers.
- SMU interface is pluggable (works with SMUBase implementations).
"""

from __future__ import annotations
import threading
import logging
import time
import os
import csv
from datetime import datetime, timezone, date
from queue import Queue, Empty, Full
from typing import Dict, Any, Optional
from logging.handlers import RotatingFileHandler
from test2.smu_lib import SMUBase

CSV_HEADERS = ["timestamp_utc", "timestamp_epoch_ms", "voltage_v", "current_a"]

class SmuLogger:
    def __init__(self,
                 smu: SMUBase,
                 data_request_interval: float = 1.0,
                 log_voltage: bool = True,
                 log_current: bool = True,
                 data_dir: str | None = None,
                 queue_maxsize: int = 1000,
                 batch_size: int = 100,
                 batch_timeout: float = 0.5,
                 debug_log_file: str | None = None,
                 debug_max_file_size_bytes: int = 5 * 1024 * 1024,
                 debug_backup_count: int = 5,
                 encoding: str = 'utf-8'):
        
        self.smu = smu
        self.data_request_interval = data_request_interval
        self.log_voltage = log_voltage
        self.log_current = log_current
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.encoding = encoding

        safe_port = str(getattr(self.smu, 'port', 'unknown')).replace('/', '_').replace('\\', '_')
        if data_dir is None: base_path = os.path.abspath('.')
        else: base_path = os.path.abspath(data_dir)
        self.data_dir = os.path.join(base_path, safe_port)
        os.makedirs(self.data_dir, exist_ok=True)

        if debug_log_file: self.debug_log_file = debug_log_file
        else: self.debug_log_file = os.path.join(self.data_dir, 'smu_debug.log')
        # self.debug_log_file = debug_log_file or os.path.join(self.data_dir, 'smu_debug.log')
        os.makedirs(os.path.dirname(self.debug_log_file), exist_ok=True)

        handler = RotatingFileHandler(
            self.debug_log_file,
            maxBytes=debug_max_file_size_bytes,
            backupCount=debug_backup_count,
            encoding=self.encoding
        )
        formatter = logging.Formatter('%(asctime)s - %(levelname)s\t- %(message)s')
        handler.setFormatter(formatter)

        self.debug_logger = logging.getLogger(f'smu.debug.{safe_port}')
        self.debug_logger.propagate = False
        # remove old handlers if present
        for h in list(self.debug_logger.handlers):
            try:
                self.debug_logger.removeHandler(h)
            except Exception:
                pass
            try:
                h.close()
            except Exception:
                pass
        self.debug_logger.addHandler(handler)
        self.debug_logger.setLevel(logging.DEBUG)
        self.debug_logger.debug('RotatingFileHandler initialized: maxBytes=%d, backupCount=%d', debug_max_file_size_bytes, debug_backup_count)

        # queue and metrics
        self.queue: Queue = Queue(maxsize=queue_maxsize)
        self.samples_dropped = 0
        self.samples_written = 0

        # threads and control
        self._poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._writer_thread = threading.Thread(target=self._writer_loop, daemon=True)
        self._stop_event = threading.Event()
        self._running_event = threading.Event()
        self._settings_lock = threading.Lock()

    def start_data_logging(self):
        self._stop_event.clear()
        self._running_event.clear()
        if not self._writer_thread.is_alive():
            self._writer_thread = threading.Thread(target=self._writer_loop, daemon=True)
            self._writer_thread.start()
        if not self._poll_thread.is_alive():
            self._poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
            self._poll_thread.start()
        self.debug_logger.debug('Poll and Writer threads started')
        self._ensure_header_for_date(datetime.now(timezone.utc).date())
        self._running_event.set()
        self.debug_logger.info('Data logging started')

    def stop_data_logging(self):
        # signal threads to stop
        self.debug_logger.info('Stopping data logging...')
        self._running_event.clear()
        self._stop_event.set()
        # wake threads
        self._running_event.set()
        # join threads
        try:
            self._poll_thread.join(timeout=2)
        except Exception:
            pass
        try:
            self._writer_thread.join(timeout=2)
        except Exception:
            pass
        self.debug_logger.info('Data logging stopped')

    def close(self,):
        # close debug logger handlers
        handlers = list(self.debug_logger.handlers)
        for h in handlers:
            try:
                h.flush()
            except Exception:
                pass
            try:
                h.close()
            except Exception:
                pass
            try:
                self.debug_logger.removeHandler(h)
            except Exception:
                pass

    def set_logging_parameters(self, log_voltage: Optional[bool] = None, log_current: Optional[bool] = None, data_request_interval: Optional[float] = None):
        with self._settings_lock:
            if log_voltage is not None:
                self.log_voltage = log_voltage
            if log_current is not None:
                self.log_current = log_current
            if data_request_interval is not None:
                self.data_request_interval = data_request_interval
        self.debug_logger.debug('Parameters updated: Log_V=%s Log_I=%s data_request_interval=%s', self.log_voltage, self.log_current, self.data_request_interval)

    @property
    def queue_size(self) -> int:
        return self.queue.qsize()

    def _poll_loop(self):
        self.debug_logger.debug('Poller thread running')
        while not self._stop_event.is_set():
            loop_start = time.monotonic()
            with self._settings_lock:
                log_v = self.log_voltage
                log_c = self.log_current
                data_request_interval = self.data_request_interval
            # build row
            now = datetime.now(timezone.utc)
            row: Dict[str, Any] = {
                CSV_HEADERS[0]: now.isoformat(),
                CSV_HEADERS[1]: int(now.timestamp() * 1000),
                CSV_HEADERS[2]: '',
                CSV_HEADERS[3]: ''
            }
            try:
                if log_v:
                    row['voltage_v'] = self.smu.measure_voltage()
                if log_c:
                    row['current_a'] = self.smu.measure_current()
            except Exception as e:
                self.debug_logger.exception('Error reading SMU: %s', e)
                # attempt reconnect once
                try:
                    self.smu.reconnect()
                except Exception:
                    self.debug_logger.exception('Reconnect failed')
            # enqueue non-blocking; drop if full
            try:
                self.queue.put_nowait(row)
            except Full:
                self.samples_dropped += 1
                self.debug_logger.warning('Queue full; sample dropped (total dropped=%d)', self.samples_dropped)
            # sleep respecting desired interval
            elapsed = time.monotonic() - loop_start
            to_sleep = max(0.0, data_request_interval - elapsed)
            if self._stop_event.wait(to_sleep):
                break
        self.debug_logger.debug('Poller thread exiting')

    def _current_filename_for_date(self, d: date) -> str:
        safe_port = str(getattr(self.smu, 'port', 'unknown')).replace('/', '_').replace('\\', '_')
        return os.path.join(self.data_dir, f"{safe_port}-{d.isoformat()}.csv")

    def _ensure_header_for_date(self, d: date):
        filename = self._current_filename_for_date(d)
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            if os.path.exists(filename) and os.path.getsize(filename) != 0: return
            with open(filename, 'a', encoding=self.encoding, newline='') as fh:
                writer = csv.DictWriter(fh, fieldnames=CSV_HEADERS)
                writer.writeheader()
        except Exception:
            self.debug_logger.exception('Failed to ensure header for %s', filename)

    def _writer_loop(self):
        self.debug_logger.debug('Writer thread running')
        buffer = []
        current_date = None
        fh = None
        writer = None

        def open_for_date(d: date):
            nonlocal fh, writer
            if fh:
                try:
                    fh.flush()
                except Exception:
                    pass
                try:
                    fh.close()
                except Exception:
                    pass
            fn = self._current_filename_for_date(d)
            os.makedirs(os.path.dirname(fn), exist_ok=True)
            need_header = (not os.path.exists(fn)) or os.path.getsize(fn) == 0
            fh = open(fn, 'a', encoding=self.encoding, newline='')
            writer = csv.DictWriter(fh, fieldnames=CSV_HEADERS)
            if need_header:
                writer.writeheader()
            return fn

        try:
            while not (self._stop_event.is_set() and self.queue.empty()):
                try:
                    item = self.queue.get(timeout=self.batch_timeout)
                    buffer.append(item)
                    # try to get up to batch_size quickly
                    while len(buffer) < self.batch_size:
                        try:
                            item = self.queue.get_nowait()
                            buffer.append(item)
                        except Empty:
                            break
                except Empty:
                    # timeout, flush if buffer not empty
                    pass

                if not buffer:
                    continue

                # determine date (use timestamp_utc of first row)
                first_ts = buffer[0]['timestamp_utc']
                try:
                    first_dt = datetime.fromisoformat(first_ts)
                except Exception:
                    first_dt = datetime.now(timezone.utc)
                d = first_dt.date()

                if current_date != d:
                    current_date = d
                    _ = open_for_date(d)
                    self.debug_logger.debug('Opened file for date %s', current_date)

                # write buffered rows
                for r in buffer:
                    try:
                        writer.writerow(r)
                        self.samples_written += 1
                    except Exception:
                        self.debug_logger.exception('Failed to write row: %s', r)
                try:
                    fh.flush()
                except Exception:
                    pass
                buffer.clear()
        finally:
            # flush remaining buffer and close file handle
            try:
                if fh:
                    for r in buffer:
                        try:
                            writer.writerow(r)
                            self.samples_written += 1
                        except Exception:
                            self.debug_logger.exception('Failed to write row during shutdown: %s', r)
                    try:
                        fh.flush()
                    except Exception:
                        pass
                    try:
                        fh.close()
                    except Exception:
                        pass
            except Exception:
                self.debug_logger.exception('Error while flushing/closing file on writer exit')
            self.debug_logger.debug('Writer thread exiting')

if __name__ == '__main__':
    print('SmuLogger module (queue-based) loaded.')
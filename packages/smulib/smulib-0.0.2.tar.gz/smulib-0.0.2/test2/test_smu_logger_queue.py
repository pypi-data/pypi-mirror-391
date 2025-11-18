import unittest
import random
import os
import time
from test2.smu_lib import SMUBase
from smu_logger import SmuLogger

class MockSMU(SMUBase):
    def __init__(self):
        self._port = 'MOCKPORT'

    @property
    def port(self):
        return self._port

    def measure_voltage(self):
        return random.uniform(-15, 15)

    def measure_current(self):
        return random.uniform(-15, 15)

    def reconnect(self):
        # do nothing for test
        pass

class TestSmuLoggerQueue(unittest.TestCase):
    def test_write_and_rotate_by_date(self):
        mock = MockSMU()
        td = os.curdir
        logger = SmuLogger(smu=mock, data_request_interval=0.05, log_voltage=True, log_current=False,
                            data_dir=td, queue_maxsize=10, batch_size=5, batch_timeout=0.1)
        logger.start()
        try:
            logger.start_logging()
            time.sleep(5)
            logger.stop_logging()
            # wait a bit to let writer flush
            logger.stop()
            # check files in data dir
            files = os.listdir(os.path.join(td, mock.port))
            self.assertTrue(len(files) >= 1)
            # find the csv file
            csv_files = [f for f in files if f.endswith('.csv')]
            self.assertTrue(len(csv_files) >= 1)
            fn = os.path.join(td, mock.port, csv_files[0])
            with open(fn, 'r', encoding='utf-8') as fh:
                lines = [l.strip() for l in fh.readlines() if l.strip()]
            # header + at least one row
            self.assertGreaterEqual(len(lines), 2)
            self.assertIn('timestamp_utc', lines[0])
        finally:
            # ensure stop cleanup
            logger.stop()
    # end test

if __name__ == '__main__':
    unittest.main()

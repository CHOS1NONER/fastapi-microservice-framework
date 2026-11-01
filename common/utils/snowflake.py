import hashlib
import os
import socket
import threading
import time


class SnowflakeGenerator:

    EPOCH = 1577836800000

    WORKER_ID_BITS = 5
    DATACENTER_ID_BITS = 5
    SEQUENCE_BITS = 12

    MAX_WORKER_ID = (1 << WORKER_ID_BITS) - 1
    MAX_DATACENTER_ID = (1 << DATACENTER_ID_BITS) - 1
    MAX_SEQUENCE = (1 << SEQUENCE_BITS) - 1

    WORKER_ID_SHIFT = SEQUENCE_BITS
    DATACENTER_ID_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS
    TIMESTAMP_SHIFT = (
        SEQUENCE_BITS + WORKER_ID_BITS + DATACENTER_ID_BITS
    )

    def __init__(self, worker_id=None, datacenter_id=0):

        if worker_id is None:
            worker_id = self._auto_worker_id()

        self.worker_id = worker_id
        self.datacenter_id = datacenter_id

        self.sequence = 0
        self.last_timestamp = -1

        self._lock = threading.Lock()

    def _auto_worker_id(self):
        base = f"{socket.gethostname()}-{os.getpid()}"
        h = hashlib.md5(base.encode()).hexdigest()
        return int(h, 16) % (self.MAX_WORKER_ID + 1)

    def _current_millis(self):
        return int(time.time() * 1000)

    def _wait_next_millis(self, last_timestamp):
        ts = self._current_millis()
        while ts <= last_timestamp:
            ts = self._current_millis()
        return ts

    def get_id(self):

        with self._lock:

            timestamp = self._current_millis()

            if timestamp < self.last_timestamp:
                time.sleep(
                    (self.last_timestamp - timestamp) / 1000
                )
                timestamp = self._current_millis()

            if timestamp == self.last_timestamp:
                self.sequence = (
                    self.sequence + 1
                ) & self.MAX_SEQUENCE

                if self.sequence == 0:
                    timestamp = self._wait_next_millis(
                        self.last_timestamp
                    )
            else:
                self.sequence = 0

            self.last_timestamp = timestamp

            return (
                ((timestamp - self.EPOCH)
                 << self.TIMESTAMP_SHIFT)
                | (self.datacenter_id
                   << self.DATACENTER_ID_SHIFT)
                | (self.worker_id
                   << self.WORKER_ID_SHIFT)
                | self.sequence
            )


_snowflake = SnowflakeGenerator()


def get_snowflake_id():
    return _snowflake.get_id()
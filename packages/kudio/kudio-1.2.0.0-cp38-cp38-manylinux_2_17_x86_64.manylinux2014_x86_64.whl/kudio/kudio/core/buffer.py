import threading
import numpy as np
from threading import Lock, Semaphore
from queue import Queue

__all__ = ['AudioBuffer', 'FetchBuffer']


class AudioBuffer:
    def __init__(self, size: int = 2):
        self.buffer_size = size
        self.free_slots = Semaphore(self.buffer_size)
        self.used_slots = Semaphore(0)
        self.clear_add = Semaphore(1)
        self.clear_get = Semaphore(1)

        self.queue_mutex = Lock()
        self.data_queue = Queue(self.buffer_size)

        self.rec_mutex = Lock()
        self.rec_free_slots = Semaphore(0)
        self.rec_queue = Queue()

    def add(self, data, drop_full=True):
        self.clear_add.acquire()
        if drop_full:  # If dropping is enabled, do not block if buffer is full
            # Try and acquire semaphore to add item
            with self.queue_mutex:
                if self.rec_free_slots._value > 0:
                    self.rec_free_slots.acquire()
                    # print(f"[bf] data_queue: {self.rec_queue.qsize()}")
                    self.rec_queue.put(data)
                    if self.rec_queue.full():
                        # print("[bf] rec_queue full")
                        self.rec_mutex.release()
                # print(f"[bf] free slots :{self.free_slots._value}")
                # Drop oldest frame
                if self.free_slots._value > 0:
                    # print("[bf] free_slots acq")
                    self.free_slots.acquire()
                    self.used_slots.release()
                else:
                    # print("[bf] data_queue Drop")
                    self.data_queue.get()

                self.data_queue.put(data)

        else:  # If buffer is full, wait on semaphore
            self.free_slots.acquire()
            with self.queue_mutex:
                # print("[bf] bf full")
                self.data_queue.put(data)
            self.used_slots.release()
        self.clear_add.release()

    def get_fixed_size_data(self, queue_size):
        # 計時錄音, 為了得到較完整的資料, 寫在放入data_queue之前
        # 若寫在 data_queue 取出資料後, 雖然較簡潔, 但可能因為畫圖而造成延遲
        with self.rec_queue.mutex:
            self.rec_queue.maxsize = queue_size
            self.rec_queue.queue.clear()
            # self.rec_free_slots.release(queue_size)
            self.rec_free_slots._value = queue_size

        self.rec_mutex.acquire()
        print(f"[kd.] Buffer: {queue_size} frames")
        with self.rec_mutex:
            pass
            # print("[kd.] Buffer: Done")
        # return b''.join(list(self.rec_queue.queue))
        return np.hstack(list(self.rec_queue.queue))

    def get(self):
        # print('[bf] get')
        self.clear_get.acquire()
        self.used_slots.acquire()
        with self.queue_mutex:
            data = self.data_queue.get()
        self.free_slots.release()
        self.clear_get.release()
        return data

    def clear(self):
        # Check if buffer contains items
        if self.data_queue.qsize() > 0:
            # Stop adding items to buffer (will retumrn false if an item is currently being added to the buffer)
            if self.clear_add._value > 0:
                self.clear_add.acquire()
                # Stop taking items from buffer (will return false if an item is currently being taken from the buffer)
                if self.clear_get._value > 0:
                    self.clear_get.acquire()
                    # Release all remaining slots in data_queue
                    # self.free_slots.release(self.data_queue.qsize())
                    self.free_slots._value = self.data_queue.qsize()
                    # Acquire all data_queue slots
                    while self.free_slots._value > 0:
                        self.free_slots.acquire()
                    # Reset used_slots to zero
                    while self.used_slots._value > 0:
                        self.used_slots.acquire()
                    # Clear buffer
                    self.data_queue.queue.clear()
                    # Release all slots
                    # self.free_slots.release(self.buffer_size)
                    self.free_slots._value = self.buffer_size
                    # Allow get method to resume
                    self.clear_get.release()
                    print("[kd.] Buffer: Clear")
                else:
                    return False
                # Allow add method to resume
                self.clear_add.release()
                return True
            else:
                return False
        else:
            return False

    def size(self):
        return self.data_queue.qsize()

    def max_size(self):
        return self.data_queue.maxsize

    def is_full(self):
        return self.data_queue.full()

    def is_empty(self):
        return self.data_queue.empty()


class FetchBuffer(threading.Thread):
    def __init__(self, buffer):
        super(FetchBuffer, self).__init__()
        assert isinstance(buffer, AudioBuffer), "Buffer error"
        self.buffer = buffer

        self.data = None

    def get_data(self, desired_queue_size, timeout: float = None):
        self.queue_size = desired_queue_size
        self.start()
        return self.join(timeout)

    def run(self):
        if isinstance(self.queue_size, int):
            self.data = self.buffer.get_fixed_size_data(self.queue_size)
            # print("get data done")

    def join(self, timeout: float = None):
        super(FetchBuffer, self).join()
        return self.data


def display_after_fetch(lck: threading.Event):
    lck.wait()

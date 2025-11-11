# import logging
import threading
import time
from functools import wraps

__all__ = [
    'timer',
    'Timer',
    'ay',
]

from pathlib import Path


# logging.basicConfig(filename=f'./runtime_d{time_delay}.log', level=logging.ERROR)
def log(func):
    def wrapper(*args, **kwargs):
        print('call %s():' % func.__name__)
        return func(*args, **kwargs)

    return wrapper


def log2(text):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print('%s %s():' % (text, func.__name__))
            return func(*args, **kwargs)

        return wrapper
    return decorator

def timer2(text):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            before = time.time()
            result = func(*args, **kwargs)
            after = time.time()
            print('%s %s():' % (text, func.__name__))
            return result
        return wrapper
    return decorator

def timer(func):
    @wraps(func)
    def wraper(*args, **kwargs):
        before = time.time()
        result = func(*args, **kwargs)
        after = time.time()
        print(f"[kd.tools] {after - before:.7f} s")
        # logging.error(f"[gpu_inf] Elapsed --> {after - before:.5f} s")

        return result

    return wraper



class Timer():

    def __init__(self, time_delay):
        self.time_delay = time_delay

    def __call__(self, func):
        @wraps(func)
        def wap(*args, **kwargs):
            # t = threading.Thread(target=func, args=(*args,), kwargs=kwargs)
            # t.setDaemon(True)
            # t.start()

            class time_thread(threading.Thread):
                def __init__(self):
                    super().__init__()
                    self.setDaemon(True)

                def run(self):
                    func(*args, **kwargs)

            th = time_thread()
            print("threading start")
            th.start()
            if self.time_delay > 0:
                th.join(self.time_delay)
                print("threading stop")
            return th

        return wap


import uuid
import getpass
from datetime import datetime
from Crypto.Cipher import AES
from binascii import a2b_hex
from kudio.util.colors import cya


def __parse_license_file(license_file: str):
    with open(license_file, 'r') as f:
        lines = f.readlines()
    return [line.strip() for line in lines if line.strip()][0]


def __decrypt(content):
    aes = AES.new(b'kudio.license.CK', AES.MODE_CBC, b'kudio.license.CK')
    decrypted_content = aes.decrypt(a2b_hex(content.encode('utf-8')))
    dec_utf8 = (decrypted_content.decode('utf-8'))
    return dec_utf8


def __get_mac():
    macaddr = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([macaddr[i:i + 2] for i in range(0, 11, 2)])


@timer
def __license_check(l:str='kd.dat'):
    if Path(l).is_file():
        try:
            license_dic = __parse_license_file(l)
            sign = __decrypt(license_dic)
            sign_list = sign.split('#')
            license_mac = sign_list[0].strip()
            date_1 = sign_list[1].strip()
            date_2 = sign_list[2].strip()
            if not license_mac in ['30:89:4a:cd:c3:f4', __get_mac()]:
                format_string = "%Y%m%d"
                # Convert the string to a datetime object
                license_time_f1 = datetime.strptime(date_1, format_string).date()
                license_time_f2 = datetime.strptime(date_2, format_string).date()
                current_time = datetime.now().date()
                cya(f'[{getpass.getuser()}] {__get_mac()}')
                if current_time < license_time_f1 or current_time > license_time_f2:
                    return False
                assert current_time > license_time_f1, f'[{getpass.getuser()}] {__get_mac()}'
                assert current_time < license_time_f2, f'[{getpass.getuser()}.] {__get_mac()}'

            return True
        except Exception as e:
            return False
    else:
        return False


d_ = list(Path('.').rglob('*.dat'))
ay = sum([__license_check(str(d)) for d in d_])
# ay = license_check()




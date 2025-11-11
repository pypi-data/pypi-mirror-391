import pyaudio
from pprint import pprint

from kudio.util.tools import timer
from kudio.util.colors import color_test

__all__ = [
    'is_available',
    'check_device',
    'CheckDevice',
]


def is_available():
    rt_color = color_test('[kd.] Color test')
    rt_audio = check_device()
    return rt_color and rt_audio


@timer
def check_device():
    try:
        help(CheckDevice)
        with CheckDevice() as cd:
            audio_devices = cd.system_devices()
            device_, rate_, channels_ = cd.input_device()
        print("[kd.] Audio test")
        return True
    except Exception as e:
        print(e)
        return False


class CheckDevice:
    standard_rate = [192000, 96000, 88200, 64000,
                     48000, 44100, 32000, 22050,
                     16000, 11025, 8000, 6000]

    def __init__(self, frame_size=1024):
        self.p = pyaudio.PyAudio()
        self.frame_size = frame_size
        self.device = None
        self.rate = None

    def __call__(self, m='device'):
        print(m)
        return self.system_devices()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.terminate()

    def terminate(self):
        self.p.terminate()

    def system_devices(self):
        device_list = []
        info = self.p.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')
        print("====================================================")
        for i in range(0, num_devices):
            index = self.p.get_device_info_by_host_api_device_index(0, i).get('index')
            sample = self.p.get_device_info_by_host_api_device_index(0, i).get('defaultSampleRate')
            name = self.p.get_device_info_by_host_api_device_index(0, i).get('name')
            out_channels = self.p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')
            in_channels = self.p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')
            device_list.append(
                {'Device': name,
                 'index': index,
                 'fs': sample,
                 'out': out_channels,
                 'in': in_channels,
                 })
            print(f"[kd.] Name:{name}, index:{index}, in:{in_channels}, out:{out_channels}")

        print("====================================================\n")
        # # use sounddevice
        # import sounddevice as sd
        # device_list = list(sd.query_devices())

        # input = device_list[sd.default.device[0]]
        # output = device_list[sd.default.device[1]]
        # sd.default.device = 24, 31
        # sd.default.reset()
        # sd.default.samplerate
        # sd.default.channels = 2

        # recording = sd.rec(frames=16000 * 3, samplerate=16000, blocking=True,channels=input['max_input_channels'])
        # sd.play(recording,16000)
        return device_list

    def get_device_info(self, device_index):
        return self.p.get_device_info_by_index(device_index)

    def _is_input_device(self, device, sr=None, channels=None):
        try:
            info = self.get_device_info(device)
            if not info["maxInputChannels"] > 0:
                return False
            sr = int(info["defaultSampleRate"]) if sr is None else sr
            # ch =
            stream = self.p.open(
                # format=pyaudio.paFloat32,
                format=pyaudio.paInt16,
                channels=1,
                input=True,
                input_device_index=device,
                rate=sr,
                frames_per_buffer=self.frame_size)
            stream.close()
            return True
        except Exception as e:
            print(f"[kd.] {e} [device:{device}, sr:{sr}]")
            return False

    def check_available_rate(self, device: int):
        if not self._is_input_device(device):
            print(f"[kd.] 此裝置無法使用: {self.get_device_info(device)}")
            return False
        else:
            available_rates = list()
            for rt in self.standard_rate:  # define the lowest sample rate
                if self._is_input_device(device, rt):
                    available_rates.append(rt)
            return available_rates

    def input_device(self, device=None, rate=None, channels=None):
        # check device
        if device is None:
            mics = [device for device in range(self.p.get_device_count()) if self._is_input_device(device)]
            # for i in range(self.p.get_device_count()):
            #     if self._is_input_device(i):
            #         mics.append(i)
            assert not len(mics) == 0, "[kd.] 系統沒有找到麥克風"

            print(f"[kd.] 找到 {len(mics)} 個麥克風")
            # [self.print_mic_info(m) for m in mics]
            device = mics[-1]
        assert self._is_input_device(device), f"[kd.] 此裝置無法使用: {self.get_device_info(device)}"

        # check sample rate
        if rate is not None and self._is_input_device(device, rate):
            pass
        else:
            for r in (16000, 22050, 44100):  # define the lowest sample rate
                if self._is_input_device(device, r):
                    rate = r
                    break
                else:
                    rate = None
            if rate is None:
                rate = int(self.get_device_info(device)["defaultSampleRate"])
        if not self._is_input_device(device, rate):
            raise Exception(f"[kd.] 此裝置取樣頻率錯誤: {self.get_device_info(device)}")
        else:
            print(f"[kd.] 裝置{device}, 取樣頻率: {rate}")

        # check channels
        if channels is not None:
            if not self.get_device_info(device)["maxInputChannels"] >= channels:
                print(
                    f"[kd.] 使用者設定通道數無法使用(可能設定值大於裝置最大通道數): {self.get_device_info(device)}")
                channels = 1
        else:
            channels = 1
        if not self._is_input_device(device, rate, channels):
            raise Exception(f"[kd.] 此裝置通道設定({channels})錯誤: {self.get_device_info(device)}")

        self.device, self.rate, self.channels = device, rate, channels
        self.show_current_device_info()
        return self.device, self.rate, self.channels

    def show_current_device_info(self):
        if self.device is not None and self.rate is not None:
            # print("\033[5;37;41mStarting program. Fan speed: 200\033[0m")
            _device = self.get_device_info(self.device)
            print("====================================================")
            print("[kd.] 選擇裝置:")
            pprint(_device)
            # self.print_device_info(self.device)
            print(f'裝置名稱: {_device["name"]}')
            print(f'裝置編號: {_device["index"]}')
            print(f'最大輸入通道: {_device["maxInputChannels"]}')
            print(f'最大輸出通道: {_device["maxOutputChannels"]}')
            print(f'預設取樣頻率: {_device["defaultSampleRate"]}')
            print(f'取樣頻率: {self.rate} Hz')
            print(f'通道數: {self.channels}')
            print(f'框大小: {self.frame_size}')
            print(f'預測更新頻率: {(self.rate / self.frame_size):.2f}')
            print("====================================================")
            print("\n")
        else:
            self.input_device()


if __name__ == '__main__':
    rt = is_available()

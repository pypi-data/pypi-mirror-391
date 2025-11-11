# -*- coding: utf-8 -*-
import socket
import threading
import wave
import librosa
import numpy as np
import pyaudio
import scipy
import scipy.signal
from pathlib import Path
from scipy.io import wavfile
from kudio.core.buffer import AudioBuffer
from kudio.core.io import check_file
from kudio.util.check import CheckDevice

__all__ = [
    'wave_decode',
    'wave_encode',
    'play_audio',
    'Recorder',
    'RemoteStreamReader',
    'LocalStreamReader',
]


def wave_decode(in_data, channels):
    result = np.frombuffer(in_data, dtype=np.int16)

    chunk_length = int(len(result) / channels)
    assert chunk_length == chunk_length

    result = np.reshape(result, (chunk_length, channels))
    return result


def wave_encode(signal):
    interleaved = signal.flatten()
    out_data = interleaved.astype(np.int16).tostring()
    return out_data


def play_audio(wav, rate=None, channels=1):
    # if isinstance(wav, str):
    pya = pyaudio.PyAudio()
    try:
        if isinstance(wav, str) or isinstance(wav, wave.Wave_read):
            if isinstance(wav, str):
                if Path(wav).is_file():
                    wav = wave.open(wav, "rb")
                else:
                    return "input file can't be play 1"

            if isinstance(wav, wave.Wave_read):
                stream = pya.open(format=pya.get_format_from_width(wav.getsampwidth()),
                                  channels=wav.getnchannels(),
                                  rate=wav.getframerate(),
                                  output=True)
                data = wav.readframes(1024)
                while data != b'':
                    stream.write(data)
                    data = wav.readframes(1024)
                # print(data)
                stream.stop_stream()
                stream.close()
            else:
                return "input file can't be play 2"

        elif isinstance(wav, np.ndarray):
            if wav.dtype not in ['int16', 'float32']:
                print(f'[Play] Input data type error! -> {wav.dtype}')
                return
            try:
                import sounddevice as sd
                sd.play(wav, rate)
            except:
                try:
                    if wav.dtype == 'int16':
                        stream = pya.open(format=pyaudio.paInt16,
                                          channels=channels,
                                          rate=rate,
                                          output=True)
                        data = wav.astype(np.int16).tostring()
                        stream.write(data)
                        stream.stop_stream()
                        stream.close()

                    elif wav.dtype == 'float32':
                        stream = pya.open(format=pyaudio.paFloat32,
                                          channels=channels,
                                          rate=rate,
                                          output=True)

                        data = wav.astype(np.float32).tostring()
                        stream.write(data)
                        stream.stop_stream()
                        stream.close()
                    else:
                        return "can't be play by pyaudio"
                except:
                    return "can't be play by pyaudio"
        else:
            return "can't play!!!"
    except Exception as e:
        print(e)
    finally:
        # close PyAudio
        pya.terminate()


#
# class CheckDevice:
#     standard_rate = [192000, 96000, 88200, 64000,
#                      48000, 44100, 32000, 22050,
#                      16000, 11025, 8000, 6000]
#
#     def __init__(self, frame_size=1024):
#         self.p = pyaudio.PyAudio()
#         self.frame_size = frame_size
#         self.device = None
#         self.rate = None
#
#     def __call__(self, m='device'):
#         print(m)
#         return self.system_devices()
#
#     def __enter__(self):
#         return self
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         self.terminate()
#
#     def terminate(self):
#         self.p.terminate()
#
#     def system_devices(self):
#         device_list = []
#         info = self.p.get_host_api_info_by_index(0)
#         num_devices = info.get('deviceCount')
#         print("====================================================")
#         for i in range(0, num_devices):
#             index = self.p.get_device_info_by_host_api_device_index(0, i).get('index')
#             sample = self.p.get_device_info_by_host_api_device_index(0, i).get('defaultSampleRate')
#             name = self.p.get_device_info_by_host_api_device_index(0, i).get('name')
#             out_channels = self.p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')
#             in_channels = self.p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')
#             device_list.append(
#                 {'Device': name,
#                  'index': index,
#                  'fs': sample,
#                  'out': out_channels,
#                  'in': in_channels,
#                  })
#             print(f"[kd.] Name:{name}, index:{index}, in:{in_channels}, out:{out_channels}")
#
#         print("====================================================\n")
#         # # use sounddevice
#         # import sounddevice as sd
#         # device_list = list(sd.query_devices())
#
#         # input = device_list[sd.default.device[0]]
#         # output = device_list[sd.default.device[1]]
#         # sd.default.device = 24, 31
#         # sd.default.reset()
#         # sd.default.samplerate
#         # sd.default.channels = 2
#
#         # recording = sd.rec(frames=16000 * 3, samplerate=16000, blocking=True,channels=input['max_input_channels'])
#         # sd.play(recording,16000)
#         return device_list
#
#     def get_device_info(self, device_index):
#         return self.p.get_device_info_by_index(device_index)
#
#     def _is_input_device(self, device, sr=None, channels=None):
#         try:
#             info = self.get_device_info(device)
#             if not info["maxInputChannels"] > 0:
#                 return False
#             sr = int(info["defaultSampleRate"]) if sr is None else sr
#             # ch =
#             stream = self.p.open(
#                 format=pyaudio.paFloat32,
#                 channels=1,
#                 input=True,
#                 input_device_index=device,
#                 rate=sr,
#                 frames_per_buffer=self.frame_size)
#             stream.close()
#             return True
#         except Exception as e:
#             print(f"[kd.] {e}")
#             return False
#
#     def check_available_rate(self, device: int):
#         if not self._is_input_device(device):
#             print(f"[kd.] 此裝置無法使用: {self.get_device_info(device)}")
#             return False
#         else:
#             available_rates = list()
#             for rt in self.standard_rate:  # define the lowest sample rate
#                 if self._is_input_device(device, rt):
#                     available_rates.append(rt)
#             return available_rates
#
#     def input_device(self, device=None, rate=None, channels=None):
#         # check device
#         if device is None:
#             mics = [device for device in range(self.p.get_device_count()) if self._is_input_device(device)]
#             # for i in range(self.p.get_device_count()):
#             #     if self._is_input_device(i):
#             #         mics.append(i)
#             assert not len(mics) == 0, "[kd.] 系統沒有找到麥克風"
#
#             print(f"[kd.] 找到 {len(mics)} 個麥克風")
#             # [self.print_mic_info(m) for m in mics]
#             device = mics[-1]
#         assert self._is_input_device(device), f"[kd.] 此裝置無法使用: {self.get_device_info(device)}"
#
#         # check sample rate
#         if rate is not None and self._is_input_device(device, rate):
#             pass
#         else:
#             for r in (16000, 22050, 44100):  # define the lowest sample rate
#                 if self._is_input_device(device, r):
#                     rate = r
#                     break
#                 else:
#                     rate = None
#             if rate is None:
#                 rate = int(self.get_device_info(device)["defaultSampleRate"])
#         if not self._is_input_device(device, rate):
#             raise Exception(f"[kd.] 此裝置取樣頻率錯誤: {self.get_device_info(device)}")
#         else:
#             print(f"[kd.] 裝置{device}, 取樣頻率: {rate}")
#
#         # check channels
#         if channels is not None:
#             if not self.get_device_info(device)["maxInputChannels"] >= channels:
#                 print(
#                     f"[kd.] 使用者設定通道數無法使用(可能設定值大於裝置最大通道數): {self.get_device_info(device)}")
#                 channels = 1
#         else:
#             channels = 1
#         if not self._is_input_device(device, rate, channels):
#             raise Exception(f"[kd.] 此裝置通道設定({channels})錯誤: {self.get_device_info(device)}")
#
#         self.device, self.rate, self.channels = device, rate, channels
#         self.show_current_device_info()
#         return self.device, self.rate, self.channels
#
#     def show_current_device_info(self):
#         if self.device is not None and self.rate is not None:
#             # print("\033[5;37;41mStarting program. Fan speed: 200\033[0m")
#             _device = self.get_device_info(self.device)
#             print("====================================================")
#             print("[kd.] 選擇裝置:")
#             pprint(_device)
#             # self.print_device_info(self.device)
#             print(f'裝置名稱: {_device["name"]}')
#             print(f'裝置編號: {_device["index"]}')
#             print(f'最大輸入通道: {_device["maxInputChannels"]}')
#             print(f'最大輸出通道: {_device["maxOutputChannels"]}')
#             print(f'預設取樣頻率: {_device["defaultSampleRate"]}')
#             print(f'取樣頻率: {self.rate} Hz')
#             print(f'通道數: {self.channels}')
#             print(f'框大小: {self.frame_size}')
#             print(f'預測更新頻率: {(self.rate / self.frame_size):.2f}')
#             print("====================================================")
#             print("\n")
#         else:
#             self.input_device()
#

class Recorder:
    """ Recorder 錄音
    ------------

    ------------

    使用方法
    ------------
    - 基本錄音方法: 設定設備編號 11, 錄製時間3秒, 通道數量6, 取樣頻率16000, chunk=1024, 儲存在'kudio_test.wav' \n
    Example 1.
       with Recorder(device=11,record_times=3,channels=6,rate=16000,frames_per_buffer=1024) as r:
           wave = r.start_record() \n
           rt = r.save('kudio_test.wav') \n
    Example 2.
       rec = Recorder(device=11,record_times=3,channels=6,rate=16000,frames_per_buffer=1024) \n
       wave = rec.start_record() \n
       rt = rec.save('kudio_test.wav') \n
       rec.close() \n
    """

    def __init__(self, device=None, record_times=3, rate=16000, channels=1, frames_per_buffer=512):
        self.formate = pyaudio.paInt16
        self.input_device_index = device
        self.record_times = record_times
        self.rate = rate
        self.channels = channels
        self.frames_per_buffer = frames_per_buffer
        self.p = pyaudio.PyAudio()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.terminate()

    def terminate(self):
        if hasattr(self, 'stream'):
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()

    close = terminate

    def start_record(self):
        self.stream = self.p.open(
            format=self.formate,
            channels=self.channels,
            input_device_index=self.input_device_index,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.frames_per_buffer)

        print(f"[kd.] Recording -----> {self.record_times} secconds <----- \n")
        self.frames = []
        for _ in range(0, int(self.rate / self.frames_per_buffer * self.record_times)):
            rec = self.stream.read(self.frames_per_buffer)
            rec = np.fromstring(rec, dtype=np.short)
            self.frames.extend(rec)
        rt_frames = [self.frames[c::self.channels] for c in range(self.channels)]
        rt_frames = np.array(rt_frames).T
        return rt_frames.squeeze()

    def save(self, file_dir, rename=False, resample=None):
        file_dir = check_file(file_dir, rename=rename)
        try:
            if resample is not None and resample != self.rate:
                self.frames = scipy.signal.resample(self.frames, resample * self.record_times)
            wf = wave.open(file_dir, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(resample)
            wf.writeframes(b''.join(self.frames))
            wf.close()
            print(f"[kd.] 儲存 --> {file_dir}")
            return True
        except Exception as e:
            print(e)
            return False

    write = save


class RemoteStreamReader(threading.Thread):
    def __init__(self, buffer):
        super(RemoteStreamReader, self).__init__()
        self.audio_buffer = buffer
        self.frame_size_ = None
        self.receive_buffer_size_ = None

        self.p = None
        self.isReceiving = threading.Event()
        self.isPlaying = threading.Event()

        # play remote audio
        self.play_stream = None

        # socket
        self.sk = None
        self.break_count = 10

    def connect_remote_device(self, ip: str, port: int):
        try:
            self.sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sk.connect((ip, port))
            self.sk.settimeout(5)
            print('[kd.] Stream:  connect success')
            return True
        except Exception as e:
            print(f'[kd.] Stream:  {e}')
            return False

    def sock_send(self, input_data, recv_buffer_size):
        if input_data == '':
            print("[kd.] Stream:  input data error")
            return
        self.sk.send(input_data.encode(encoding="utf-8"))
        # if input_data == 's':
        #     print(f"Local BS {recv_buffer_size}")
        data = self.sk.recv(recv_buffer_size)
        try:
            print(data.decode(encoding='UTF-8'))
        except KeyboardInterrupt:
            self.sk.close()
        except Exception as e:
            # print(e)
            while len(data) < recv_buffer_size:
                data += self.sk.recv(recv_buffer_size)
            waves = np.frombuffer(data, dtype=np.int16)
            print(f"[kd.] Stream:  Wave shape: {waves.shape}")
            return waves

    def initialize_params(self, frame_size=2048, wav_format: str = '16bit'):
        _format = 1 if wav_format.lower() == '32bit' else 8
        self.p = pyaudio.PyAudio()
        self.frame_size_ = frame_size
        self.receive_buffer_size_ = frame_size * 2 if _format == 8 else frame_size * 4
        if _format in [pyaudio.paFloat32, pyaudio.paInt16]:
            self.stream_dtype = _format
            self.data_type = np.int16 if _format == pyaudio.paInt16 else np.float32
        else:
            raise Exception("[kd.] Stream:  data type Error")

    def play_remote_audio(self, rate, channels=1):
        self.play_stream = self.p.open(format=self.stream_dtype,
                                       channels=channels,
                                       rate=rate,
                                       output=True,
                                       frames_per_buffer=self.frame_size_)
        if self.play_stream.is_active():
            self.isPlaying.set()
            print("[kd.] Stream:  successfully open play stream")

    def run(self) -> None:
        self.isReceiving.set()
        while self.isReceiving.is_set():
            try:
                data = self.sk.recv(self.receive_buffer_size_)
                # check received data size
                cnt = 0
                while len(data) < self.receive_buffer_size_:
                    cnt += 1
                    # print(f'[kd.] Stream:  Receive again ({len(data)})')
                    data += self.sk.recv(self.receive_buffer_size_)
                    if cnt > self.break_count:
                        print("[kd.] Stream:  Auto Break by break_count !!!!!!!")
                        self.terminate()

                if len(data) != self.receive_buffer_size_:
                    print(f"[kd.] Stream:  Unexpected data ({len(data)})")
                    continue
                # print(f'[kd.] Stream:  Receive done ({len(data)})')
                self.audio_buffer.add(np.frombuffer(data, dtype=self.data_type))

                if self.isPlaying.is_set():
                    # print(f"play data shape: {len(data)}")
                    self.play_stream.write(data)
            except Exception as e:
                # print(f'[kd.] Stream:  {e}')
                pass
        else:
            print("[kd.] Stream:  Auto stop receiving")

    def terminate(self):
        if self.sk is not None and not self.sk._closed:
            self.sk.send('stop'.encode(encoding="utf-8"))
            print('[kd.] Stream:  Send stop cmd to server')
            self.sk.close()
            self.sk = None
            print('[kd.] Stream:  Close local socket')
        if self.is_alive() or self.isReceiving.is_set():
            self.isReceiving.clear()
            print('[kd.] Stream:  close receiving')
        if self.play_stream is not None and self.play_stream.is_active():
            self.isPlaying.clear()
            self.play_stream.stop_stream()
            self.play_stream.close()
            self.play_stream = None
            print('[kd.] Stream:  Stop playing stream')
        if self.p is not None:
            self.p.terminate()


class LocalStreamReader:
    """ 當地設備之串流類
    ------------

    使用方法 - 監聽
    ------------
    - 說明： 從本地端麥克風收音, 於本地端播放設備播放

    - 初始化
    >>> lsr = LocalStreamReader(channels=1, frame_size=2048, wav_format=8)

    - 檢查是否初始化成功, 成功則 rst=True
    >>> rst = lsr.get_status()

    - 初始化播放裝置
    >>> lsr.stream_start()

    - 初始化錄音設備, 並開始串流
    >>> lsr.stream_start()
    """

    def __init__(self,
                 device=None,
                 rate=None,
                 channels: int = 1,
                 frame_size: int = 2048,
                 wav_format: int = 8,
                 buffer=None):
        """
        :param device: 指定裝置, 預設為系統預設裝置
        :param rate: 指定取樣頻率, 預設為裝置預設值
        :param channels: 指定通道數量, 預設為 1
        :param frame_size: 框大小, 預設為 2048
        :param wav_format: 1 for 32-bit , 8 for 16-bit
        :param buffer: default None
        """

        self.audio_buffer = buffer
        self.device_ = None
        self.rate_ = None
        self.channels_ = None
        self.frame_size_ = None
        self.receive_buffer_size_ = None

        self.isInitial = threading.Event()
        self.isBroadcasting = threading.Event()
        self.isListening = threading.Event()
        self.play_stream = None
        self.rec_stream = None

        self.set_stream(device, rate, channels, frame_size, wav_format)

    def set_stream(self, device=None, rate=None,
                   channels: int = 1,
                   frame_size: int = 2048,
                   wav_format: int = 8):
        ## wav_format 1 for 32-bit , 8 for 16-bit
        self.p = pyaudio.PyAudio()
        ## check device
        with CheckDevice() as check:
            self.device_, self.rate_, self.channels_ = check.input_device(device, rate, channels)

        self.frame_size_ = frame_size
        self.receive_buffer_size_ = frame_size * 2 if wav_format == 8 else frame_size * 4
        if wav_format in [pyaudio.paFloat32, pyaudio.paInt16]:
            self.format = wav_format
            self.data_type = np.int16 if wav_format == pyaudio.paInt16 else np.float32
            self.isInitial.set()
            return True
        else:
            print("[kd.] Stream:  Open Failed")
            # raise Exception("[kd.] Stream:  data type Error")
            return False

    def get_status(self):
        return True if self.isInitial.is_set() else False

    def get_setup(self):
        return self.device_, self.rate_, self.channels_ if self.get_status() else None

    def play_audio(self):
        self.play_stream = self.p.open(
            format=self.format,
            channels=self.channels_,
            rate=self.rate_,
            output=True,
            frames_per_buffer=self.frame_size_
        )
        if self.play_stream.is_active():
            self.isBroadcasting.set()
            print("[kd.] Stream:  Broadcasting... Success")
        else:
            print("[kd.] Stream:  Broadcasting... Failed")

    def _callback(self, in_data, frame_count, time_info, status):
        if self.isListening.is_set():
            if self.isBroadcasting.is_set():
                self.play_stream.write(in_data)
            data = np.frombuffer(in_data, dtype=self.data_type)
            if self.audio_buffer is not None:
                self.audio_buffer.add(data)
            # print(f"{np.sum(data)}")
        return in_data, pyaudio.paContinue

    def stream_start(self):
        self.rec_stream = self.p.open(
            format=self.format,
            channels=self.channels_,
            input=True,
            # output=True,
            input_device_index=self.device_,
            rate=self.rate_,
            frames_per_buffer=self.frame_size_,
            stream_callback=self._callback)
        self.rec_stream.start_stream()
        self.isListening.set()

    def terminate(self):
        self.isInitial.clear()
        self.isBroadcasting.clear()
        if self.play_stream is not None and self.play_stream.is_active():
            self.play_stream.stop_stream()
            self.play_stream.close()
            self.play_stream = None
            print("[kd.] Stream:  Stop playing stream")
        if self.rec_stream is not None and self.isListening.is_set():
            self.isListening.clear()
            self.rec_stream.stop_stream()
            self.rec_stream.close()
            self.rec_stream = None
            print("[kd.] Stream:  Stop recording stream")
        if self.p is not None:
            self.p.terminate()


if __name__ == '__main__':
    ### check device
    with CheckDevice() as cd:
        audio_devices = cd.system_devices()
        device_, rate_, channels_ = cd.input_device(3, 192000)

    ### example: streaming with no buffer
    lsr = LocalStreamReader(
        # device=10,
        # rate=None,
        channels=1,
        frame_size=2048,
        wav_format=8)
    rst = lsr.get_status()
    if rst:
        lsr.play_audio()
        lsr.stream_start()

    ### example: streaming with buffer
    bf = AudioBuffer(3)
    lsr = LocalStreamReader(buffer=bf)
    rst = lsr.get_status()
    if rst:
        lsr.play_audio()
        lsr.stream_start()

    ### play audio
    file = "../data/train/clean/ok/impact01_nor_0.wav"
    play_audio(file)

    f = wave.open(file, "rb")
    play_audio(f)

    w, sr = librosa.load(file, None)
    play_audio(w, sr)

    sr, w = wavfile.read(file)
    play_audio(w, sr)

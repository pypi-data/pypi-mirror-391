import re
import shutil
import librosa
import numpy as np
from scipy.io import wavfile
from tqdm import trange, tqdm
from typing import Tuple, List, Union, Any
from pathlib import Path, PurePath
from multiprocessing import Pool
from functools import partial

__all__ = [
    'check_path',
    'check_file',
    'check_input',
    'save_wave',
    'file_load',
    'load_wave',
    'load_waves',
    'copy_waves',
    'LoadAudio',
]
__exp__ = '.wav'


def check_path(path, exist_ok=False, sep=''):
    # runs/exp --> runs/exp{sep}0, runs/exp{sep}1 etc.
    path = Path(path)
    if (path.exists() and exist_ok) or (not path.exists()):
        return str(path)
    else:
        dirs = list(path.rglob(f"{path}{sep}*"))
        matches = [re.search(rf"%s{sep}(\d+)" % path.stem, str(d)) for d in dirs]
        i = [int(m.groups()[0]) for m in matches if m]  # indices
        n = max(i) + 1 if i else 2  # increment number
        return f"{path}{sep}{n}"  # update PATH


def check_file(file_dir, rename=True, sep=''):
    check_path(file_dir)
    file_dir = Path(file_dir)
    if file_dir.is_dir():
        file_dir = file_dir / 'unknow'
    file_dir = file_dir.with_suffix(__exp__)
    if file_dir.is_file():
        print(f'[kd.] 檔案已經存在: {file_dir}')
        if rename:
            _files = list(file_dir.parent.rglob(f'{file_dir.stem}{sep}*'))
            matches = [re.search(f"{file_dir.stem}{sep}(\d+)", str(d)) for d in _files]
            i = [int(m.groups()[0]) for m in matches if m]
            n = max(i) + 1 if i else 2
            file_dir = (file_dir.parent / f"{file_dir.stem}{sep}{n}").with_suffix(__exp__)
            print(f'[kd.] 重新命名檔案: {file_dir}')
        else:
            print(f'[kd.] 已覆蓋原檔案: {file_dir}')
    file_dir.parent.mkdir(exist_ok=True, parents=True)
    return str(file_dir)


def check_input(input) -> Tuple[List[Path], List[Union[str, Any]]]:
    """
    檢查或尋找副檔名為 kudio.kudio_params.waveform.type 的檔案

    Parameters:
        input : anything. file path, list of file path, .txt file contains file path, list of .txt files, ...
    Returns:
        rightList, wrongList (rightList if file with suffix "kudio.kudio_params.waveform.type" else wrongList)

    """
    rightList = []
    wrongList = []
    if isinstance(input, (list, tuple)):
        for item in input:
            r, w = check_input(item)
            rightList.extend(r)
            wrongList.extend(w)
    elif input and isinstance(input, (str, PurePath)):
        input = Path(input)
        if input.is_file():
            if input.suffix == '.txt':
                with open(input, 'r') as f:
                    input = [x.strip() for x in f.read().strip().splitlines() if len(x.strip())]
                    for item in input:
                        r, w = check_input(item)
                        rightList.extend(r)
                        wrongList.extend(w)
            elif input.suffix == '.wav':
                rightList.append(input)
            else:
                wrongList.append(str(input))
        elif input.is_dir():
            rightList.extend(list(input.rglob("*.wav")))
        else:
            wrongList.append(str(input))
    else:
        wrongList.append(input)
    return rightList, wrongList


def file_load(wav_dir, sr=None, mono=True):
    """
    load .wav file.

    wav_name : str
        target .wav file
    mono : boolean
        When load a multi channels file and this param True, the returned data will be merged for mono data

    return : numpy.array( float )
    """
    try:
        return librosa.load(str(wav_dir), sr=sr, mono=mono)
    except:
        print(f"[kd.] File broken or Not exists! : {wav_dir}")


def load_wave(wave, num=None):
    info = wave if num is None else wave[num]
    if isinstance(info, (list, tuple)):
        # info = list(itertools.chain.from_iterable(convert_to_waveform(i) for i in info))
        info = [load_wave(w) for w in tqdm(info, desc="[kd.] Loading Audios:")]
    elif isinstance(info, (str, PurePath)) and \
            Path(info).is_file() and \
            Path(info).suffix in ['.wav']:
        info = file_load(info)
    else:
        raise Exception("[kd.] Found unexpected file", info)
    return info


def load_waves(wave, use_pool: bool = False, std_len: bool = False, core_: int = 8):
    """
    將所有.wav 轉換為數值 (wave, sr)(type=float32, sample rate=N)

    Parameters:
        wave: str, list, list tree, tuple(include .txt files)
        use_pool: To use multi-processing pool


    Returns:
        A list (np.ndarray, int) containing all audio files converted into waveform.[shape(length) is the same as input]

    result = load_waves(synWavesList, is_pool=True, cpu_croes=8)
    print(len(result))
    :param std_len: if std_len=True, return 3 elements [ys, sr, mlen]

    """
    waves, w = check_input(wave)
    if use_pool and len(waves) > 300:
        fcn = partial(load_wave, waves)
        with Pool(core_) as pool:
            result = pool.map(fcn, trange(len(waves), desc="[kd.load_waves] Pooling..."))
    else:
        # result = load_wave(waves[0]) if len(waves) == 1 else load_wave(waves)
        result = load_wave(waves)

    if std_len:
        w2d = []
        lens = []
        srs = []
        for y, sr in result:
            w2d.append(y)
            lens.append(len(y))
            srs.append(sr)
        assert set(srs).__len__() == 1, '[kd.load_waves] Different audio sampling frequencies'

        min_len = min(lens)
        for i, w_ in enumerate(tqdm(w2d, desc="[kd.load_waves] std_len ing...")):
            w2d[i] = w_[:min_len]
        return w2d, srs[0], min_len

    return result


def save_wave(path, wave: np.ndarray, sr: int, d_sample: int = None) -> None:
    """
    To write a WAV file (numPy array)

    :param path: 儲存路徑 str
    :param wave: 音頻 np.ndarray
    :param sr: 取樣頻率 int
    :param d_sample: resample int
    """
    Path(path).parent.mkdir(exist_ok=True, parents=True)
    wave_type = wave.dtype

    if d_sample is not None:
        # 重采样, 注意一定要对数据做astype(np.float32)，否则会出现下采样无效。
        wave = librosa.resample(wave.astype(np.float32), sr, d_sample)
        wave = wave.astype(wave_type)
        sr = d_sample

    if wave_type == np.float32:
        # wave = (wave * 32768).astype('int16')
        wave = (wave * np.iinfo(np.int16).max).astype('int16')

    wave = np.clip(wave, -32768, 32767)
    wavfile.write(path, sr, wave.astype('int16'))
    # librosa.output.write_wav(str(file_dir), wave.astype(np.float32), sr, norm=False)


def copy_waves(path, wave_):
    path = Path(path)
    if path.suffix:
        print(f'[kd.] 輸入並非路徑➡{path}')
        return
    path.mkdir(exist_ok=True, parents=True)

    if isinstance(wave_, list):
        for w in tqdm(wave_, desc=f'[kd.] 複製音檔至路徑➡{path.resolve()}\n\tCopying '):
            copy_waves(path, w)
    else:
        w = Path(wave_)
        shutil.copy(str(w), path / w.name)


class LoadAudio(object):

    def __init__(self, waves_dirs):
        self.sr_pth = Path(waves_dirs)
        assert self.sr_pth.is_dir(), f"[kd.io] Folder: {self.sr_pth.absolute()}, not found."

        self.files = list(self.sr_pth.rglob('*.wav'))
        self.nf = len(self.files)

    def __iter__(self):
        self.count = 0
        return self

    def __next__(self):
        if self.count == self.nf:
            raise StopIteration
        self.count += 1
        return self.count

    def __len__(self):
        return self.nf  # number of files

    @staticmethod
    def check_input(*args):
        return check_input(*args)

    @staticmethod
    def file_load(*args, **kwargs):
        return file_load(*args, **kwargs)

    @staticmethod
    def load_wave(*args, **kwargs):
        return load_wave(*args, **kwargs)

    @staticmethod
    def load_waves(*args, **kwargs):
        return load_waves(*args, **kwargs)

    @staticmethod
    def copy_waves(*args, **kwargs):
        return copy_waves(*args, **kwargs)

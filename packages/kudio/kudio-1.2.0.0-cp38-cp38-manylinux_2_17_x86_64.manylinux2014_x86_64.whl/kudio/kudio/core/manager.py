from copy import deepcopy
from pathlib import Path
from kudio.core.io import load_waves, save_wave
from kudio.core.feature import wave_separate
from kudio.core.stream import play_audio
from kudio.util.colors import warn

__all__ = [
    'AudioDataManager'
]


class AudioDataManager:
    def __init__(self):
        self.suffix = '.wav'
        self.rate_ = None
        self.ch_ = 1
        self.default_dict = {"dir": None, "wave": [], "sr": None, "ch": self.ch_}
        self.reset_defaults()

    def reset_defaults(self):
        self.audios_ = dict()

    reset = reset_defaults

    def set_params(self, sr: int, ch: int):
        assert sr > 0, "sr setting error"
        self.ch_ = ch if 3 > ch > 0 else 1
        self.rate_ = sr
        self.default_dict = {"dir": None, "wave": [] * self.ch_, "sr": sr, "ch": self.ch_}

    def __call__(self, wave_name):
        return self.get_item(wave_name)

    def __getitem__(self, wave_name):
        if isinstance(wave_name, str):
            return self.get_item(wave_name)
        elif isinstance(wave_name, int):
            return self.get_item(list(self.get_names())[wave_name])

    def get_item(self, name):
        try:
            return self.audios_[name]
        except Exception as e:
            print(f"[kd.] Manager -  {e}")
            return None

    def __len__(self):
        return len(self.audios_)

    def get_wave(self, name):
        item = self.__getitem__(name)
        if item is not None:
            return item['wave']
        else:
            return None

    def get_sample(self, name):
        item = self.__getitem__(name)
        if item is not None:
            return item['sr']
        else:
            return None

    def add_local_file(self, dir, name: str = None):
        dir = Path(dir)
        assert dir.is_file(), f'[AudioManager] (add_local_file) File not exists ->{dir}'
        name = dir.stem if name is None else name
        if name in self.get_names():
            warn("[kd.] Manager - (add_local_file) Name exist")
            return None
        self.audios_[name] = deepcopy(self.default_dict)
        self.audios_[name]["dir"] = str(dir)
        wave_, rate_ = load_waves(dir)[0]
        self.audios_[name]["wave"].append(wave_)
        self.audios_[name]["sr"] = rate_
        self.audios_[name]["ch"] = 1
        # return wave_, rate_

    def add_new_file(self, name: str = None, dir=None, wave=None, sr: int = None, ch: int = None, override=False):
        if name is None:
            if dir is None:
                return warn('[AudioManager] (add_new_file) Please set a name or dir')
            else:
                name = Path(dir).stem
        if name in self.get_names() and not override:
            warn("Name exist")
        else:
            sr = self.rate_ if sr is None else sr
            ch = self.ch_ if ch is None else ch
            self.audios_[name] = deepcopy(self.default_dict)
            if dir is not None:
                self.audios_[name]["dir"] = str(dir)
            if wave is not None:
                if len(wave) == 1 and ch > 0:
                    wave = wave_separate(wave[0], ch)
                    for i in range(ch):
                        self.audios_[name]["wave"].append(wave[i])
                else:
                    self.del_element(name)
                    return warn('[AudioManager] (add_new_file) Unexpected wave or ch')
            self.audios_[name]["sr"] = sr
            self.audios_[name]["ch"] = ch

    def add_name(self, name: str):
        self.audios_[name] = self.default_dict.copy()

    def add_dir(self, name: str, dir: str):
        self.audios_[name]["dir"] = dir

    def add_wave(self, name: str, wave):
        self.audios_[name]["wave"].append(wave)

    def add_sr(self, name, sr):
        self.audios_[name]["sr"] = sr

    def add_ch(self, name, ch):
        self.audios_[name]["ch"] = ch

    def del_element(self, name):
        try:
            del self.audios_[name]
        except Exception as e:
            print(e)

    def del_from_path(self, pth, key: str = None):
        pth = Path(pth)
        files = list(pth.glob(key) if key else pth.glob('.wav'))
        for f in files:
            if f.is_file():
                f.unlink(missing_ok=True)

    def get_names(self):
        return self.audios_.keys()

    def get_values(self):
        return self.audios_.values()

    def save_(self, name, dst_path=None, down_sample=None):
        if self.__len__() > 0:
            item = self.get_item(name)
            if item is None:
                print("[kd.] Manager - (save_) Data not found!")
                return
            else:
                dir_ = item['dir'] if dst_path is None else (Path(dst_path) / name).with_suffix(self.suffix)
                if self.ch_ > 1:
                    pth = Path(dir_).parent
                    for i, w in enumerate(item['wave']):
                        d = (pth / f"{name}_ch{i}").with_suffix(self.suffix)
                        save_wave(d, w, item['sr'], d_sample=down_sample)
                else:
                    save_wave(dir_, item['wave'][0], item['sr'], d_sample=down_sample)
        else:
            print("[kd.] Manager - (save_) Data empty!")

    def save_all(self, dst_path=None, down_sample=None):
        if self.__len__() > 0:
            for n in self.get_names():
                item = self.get_item(n)
                if item is None:
                    print("[kd.] Manager - (save_all) Data not found!")
                    return False
                else:
                    dir_ = item['dir'] if dst_path is None else (Path(dst_path) / n).with_suffix(self.suffix)
                    if self.ch_ is not None and self.ch_ > 1:
                        pth = Path(dir_).parent
                        for i, w in enumerate(item['wave']):
                            d = (pth / f"{n}_ch{i}").with_suffix(self.suffix)
                            save_wave(d, w, item['sr'], d_sample=down_sample)
                    else:
                        save_wave(dir_, item['wave'][0], item['sr'], d_sample=down_sample)
            print("[kd.] Manager - Save all wave success")
            return True
        else:
            print("[kd.] Manager - save_all) Data empty!")
            return False

    def play_audio(self, name, volume: float):
        item = self.__getitem__(name)
        if item is not None:
            w = item['wave'][0]
            dtype_ = w.dtype
            play_audio(wav=(w * volume).astype(dtype_), rate=item['sr'])
        else:
            print(f"[kd.] Manager - Play audio error, wave:{name}")

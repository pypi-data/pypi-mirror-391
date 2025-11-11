# -*- coding: utf-8 -*-
import shutil
import librosa
import numpy as np
from pathlib import Path
from scipy.io import wavfile
from multiprocessing import Pool
from functools import partial
from tqdm import tqdm, trange
from kudio.core.io import check_input, load_waves
from kudio.util.colors import warn

__all__ = ['Synthesizer']


class Synthesizer:
    """ Synthesizer 音頻混合器
    ------------

    ------------

    使用方法
    ------------
    # >>> syx = Synthesizer(clean, noise, out_path='', snr_ratio=(-5, 0, 5))
         :clean, noise: 為音頻資料, 型態可以是:
              clean = 'data/clean' # str
              clean = ['data/clean', 'data/clean2'] # list
              clean = 'wave.txt' # .txt file
              clean = ['wave.txt', 'data/clean2'] # list
        :out_path: 資料輸出路徑
        :snr_ratio: SNR值, 型態為列表, 整數, 一個或多個
              snr_ratio = [10]
              snr_ratio = [-5, 0, 5]
        :return: synWavesList 混合後的音頻列表 [[noy, cln, noise, snr], ...]

    # >>> syx.syn(mode='regular', add_clean=False, rdn_choice=None)
        - mode: 混音方法
              mode = 'regular' 或 'increment'
                  mode: 'reg' or 'regular'
                      -> noiseWaves 按照 snrRatio & noise順序，循環加入cleanWaves(產生音檔數量與cleanWaves數量一樣)
                  mode: 'inc' or 'increment'
                      -> 產生音檔數量為 cleanWaves * noiseWaves * snrRatio
        - add_clean: 是否將原始音檔輸出
        - rdn_choice: 是否從輸入資料clean中隨機選取資料做為新的輸入資料clean

    # >>> syx.syn_extra_mode(background_path="<path>", background_snr=(5,))
        - 將 noise 與 background_path的音檔 按照 background_snr 混合, 再按照 snr_ratio 混入clean
        - 產生音檔數量為: clean*((1+noise)*(1+backgroundnoise)-1)*snr*(1+20%(silence))
        - background_path: 輸入資料
        - background_snr: 混音 SNR 值, 可以是任何整數值, 一個或多個
              snr_ratio = [10]
              snr_ratio = [-5, 0, 5]
        - add_clean: 是否將原始音檔輸出
        - rdn_choice: 是否從輸入資料clean中隨機選取資料做為新的輸入資料clean

    ------------

    # >>> Synthesizer.syn_waves(synWavesList, isSilence: bool, num=None)
        - staticmethod
        - synWavesList = [[save_dir, clean_file, noise_file, snr], ... ]
    """

    def __init__(self, clean, noise, out_path='', snr_ratio=(-5, 0, 5)):
        # super(Synthesizer, self).__init__()
        # self.cleanPath, self.noisePath = Path(clean), Path(noise)
        assert all([Path(clean).is_dir(), Path(noise).is_dir()]), "input path error"
        self.cleanWaves, w = check_input(clean)
        self.noiseWaves, w = check_input(noise)
        assert self.cleanWaves, f"Error input {clean}, found {len(self.cleanWaves)} files."
        assert self.noiseWaves, f"Error input {noise}, found {len(self.noiseWaves)} files."

        self.noisyDir = Path('mixed' if out_path == '' else out_path)

        assert not isinstance(snr_ratio, str), f"type error: snr_ratio can't be str"
        self.snrRatio = snr_ratio if hasattr(snr_ratio, '__iter__') else [snr_ratio]

        self.synWavesList = None  # for syn processing
        self.clean_dir_ = clean

    def wave_input(self):
        return self.cleanWaves, self.noiseWaves

    def wave_syn(self) -> list:
        return self.synWavesList

    def wave_syn_abs(self) -> list:

        return self.synWavesList

    def waveform(self, is_pool=False):
        fcn = partial(load_waves, is_pool=is_pool)
        return fcn(self.cleanWaves), fcn(self.noiseWaves)

    def syn(self, mode: str = 'regular',
            mkdir_parents: bool = True,
            is_add_clean: bool = False,
            rdn_choice_num: int = 0,
            overwrite: bool = True,
            is_pool: bool = True,
            is_silence: bool = False,
            p_silence=0.02):

        """
        Parameters
        ----------
        mode : str, optional, default: True
                    'reg', 'inc', 'max'
        mkdir_parents : bool, optional


        Returns
        -------
        out : list
            synthesized_wav_list

        """
        print("[kd.] ==== Audio Synthesizing ====")
        # 檢查是否目的資料夾是否存在
        if self.noisyDir.is_dir() and list(self.noisyDir.glob('*')):
            if overwrite:
                warn(f"[kd.] syn:  路徑已存在，將覆蓋資料夾 -> {self.noisyDir}")
                shutil.rmtree(self.noisyDir)
            else:
                warn(f"[kd.] syn:  路徑已存在 -> {self.noisyDir}，終止程序")
                return
        self.noisyDir.mkdir(parents=True, exist_ok=True)

        # 從隨機clean隨機挑選N個資料作為clean(N不大於原本資料長度)
        clnWaves = [
            np.random.choice(self.cleanWaves) for _ in range(rdn_choice_num)
        ] if len(self.cleanWaves) >= rdn_choice_num > 0 else self.cleanWaves

        # 是否將乾淨資料加入noy中，輸出至RAW_DATA資料夾
        if is_add_clean:
            dir_ = self.noisyDir.joinpath("RAW_DATA")
            dir_.mkdir(parents=True, exist_ok=True)
            for cln in clnWaves:
                shutil.copy(cln, dir_.joinpath(cln.stem + '_raw').with_suffix('.wav'))

        clnLen = clnWaves.__len__()
        nosLen = self.noiseWaves.__len__()
        snrLen = self.snrRatio.__len__()
        print(f"Clean: {clnLen}, Noise: {nosLen}, SNR: {self.snrRatio[0]} ~ {self.snrRatio[-1]}")

        if mode in ['reg', 'regular']:
            print(f"{len(self.snrRatio)} SNRs * {nosLen} noises, generate {clnLen} noisy.")
            nosWaves = np.tile(self.noiseWaves, clnLen // nosLen + 1)[:clnLen]
            snrSeqs = np.tile(self.snrRatio, clnLen // snrLen + 1)[:clnLen]
        elif mode in ['inc', 'increment']:
            print(f"{clnLen * nosLen * snrLen} noisy files "
                  f"generated by {snrLen} kinds of SNR and {nosLen} noise files ")
            clnWaves = np.repeat(clnWaves, nosLen * snrLen)
            nosWaves = np.tile(np.repeat(self.noiseWaves, snrLen), clnLen)
            snrSeqs = np.tile(self.snrRatio, clnLen * nosLen)
        elif mode in ['max', 'extra']:
            return "Please use class function 'syn_extra_mode' to run extra mode."
        else:
            return "select the right mode"

        # output path
        outWaves = []
        for cln, nos, snr in zip(clnWaves, nosWaves, snrSeqs):
            snr = f'n{abs(snr)}' if snr < 0 else f"{snr}dB"

            outDir = self.noisyDir.joinpath(
                cln.relative_to(self.clean_dir_).parent) if mkdir_parents else self.noisyDir

            outWaves.append(
                (outDir.joinpath('_'.join([cln.stem, nos.stem, snr]))).with_suffix('.wav'))

        self.synWavesList = list(zip(outWaves, clnWaves, nosWaves, snrSeqs))

        self.__syn_pool(is_pool=is_pool, is_silence=is_silence, p_silence=p_silence)
        return self.synWavesList

    def syn_extra_mode(self, background_path='../data/backgroundnoise', background_snr=(5,)):
        # sync using background_noise
        assert not isinstance(background_snr, str), f"type error: snr_ratio can't be str"
        bgSNR = background_snr if hasattr(background_snr, '__iter__') else [background_snr]
        bgNoiseWaves, w = check_input(background_path)
        assert bgNoiseWaves, f"Error input {background_path}"
        if self.noisyDir.is_dir() and list(self.noisyDir.glob('*')):
            shutil.rmtree(self.noisyDir)
        self.noisyDir.mkdir(parents=True, exist_ok=True)
        cleanWaves = self.cleanWaves
        for cln in cleanWaves:
            shutil.copy(cln, (self.noisyDir / (cln.stem + '_n0')).with_suffix(cln.suffix))

        # 建立暫存路徑, 存放第一次混音後的檔案 + pure noise + pure back ground noise
        temporaryPath = Path('tmp_mixed')
        if temporaryPath.is_dir():
            shutil.rmtree(temporaryPath)
        temporaryPath.mkdir()

        fullCleanWaves = np.repeat(self.noiseWaves, len(bgNoiseWaves) * len(bgSNR))
        fullNoiseWaves = np.tile(np.repeat(bgNoiseWaves, len(bgSNR)), len(self.noiseWaves))
        fullSnrSequence = np.tile(bgSNR, len(self.noiseWaves) * len(bgNoiseWaves))

        fullOutPaths = [
            (temporaryPath / '_'.join(
                [cln.stem, nos.stem, f"{f'n{abs(snr)}' if snr < 0 else snr}dB"])).with_suffix(".wav") for
            cln, nos, snr in zip(fullCleanWaves, fullNoiseWaves, fullSnrSequence)]
        self.synWavesList = list(zip(fullOutPaths, fullCleanWaves, fullNoiseWaves, fullSnrSequence))
        self.__syn_pool(is_pool=False, is_silence=False)

        # increment mixed
        noiseWaves = fullOutPaths + self.noiseWaves + bgNoiseWaves
        fullCleanWaves = np.repeat(self.cleanWaves, len(noiseWaves) * len(self.snrRatio))
        fullNoiseWaves = np.tile(np.repeat(noiseWaves, len(self.snrRatio)), len(cleanWaves))
        fullSnrSequence = np.tile(self.snrRatio, len(cleanWaves) * len(noiseWaves))
        fullOutPaths = [
            (self.noisyDir / '_'.join(
                [cln.stem, nos.stem, f"{f'n{abs(snr)}' if snr < 0 else snr}dB"])).with_suffix(".wav") for
            cln, nos, snr in zip(fullCleanWaves, fullNoiseWaves, fullSnrSequence)]
        self.synWavesList = list(zip(fullOutPaths, fullCleanWaves, fullNoiseWaves, fullSnrSequence))

        self.__syn_pool(is_pool=True, is_silence=True, p_silence=0.02)
        shutil.rmtree(temporaryPath)
        return self.synWavesList

    def __syn_pool(self, is_pool: bool, is_silence: bool, p_silence=0.02):
        if is_silence and 1 > p_silence > 0:  # 將 p_silence 的noisy靜音後，只輸出 noise，作新類別 silence
            out0, cln0, nos0, snr0 = zip(*self.synWavesList)
            index = np.random.choice(range(len(self.synWavesList)), size=round(len(self.synWavesList) * p_silence))
            out, cln, nos, snr = zip(*[self.synWavesList[i] for i in index])
            snr = tuple(np.where(np.array(snr) != 0, 0, 0))
            out = tuple([o.parent / (c.stem + n.stem + '_n00.wav') for o, c, n in zip(out, cln, nos)])
            self.synWavesList = list(zip(out0 + out, cln0 + cln, nos0 + nos, snr0 + snr))

        if is_pool and len(self.synWavesList) > 200:
            fcn = partial(Synthesizer.syn_waves, self.synWavesList, is_silence)
            with Pool(8) as pool:
                pool.map(fcn, trange(len(self.synWavesList), desc="Audio synthesis"))
        else:
            [Synthesizer.syn_waves(wave, is_silence) for wave in tqdm(self.synWavesList, desc="Audio synthesis")]

    @staticmethod
    def syn_waves(synWavesList, isSilence: bool, num=None):
        """
        synWavesList = [[save_dir, clean_file, noise_file, snr], ... ]
        """
        sr_clean = sr_noise = 16000 if 16000 else None
        save_dir, clean_file, noise_file, snr = synWavesList if num is None else synWavesList[num]
        y_clean, sr_clean = librosa.load(clean_file, sr_clean)
        y_noise, sr_noise = librosa.load(noise_file, sr_noise)

        clean_pwr = sum(abs(y_clean) ** 2) / len(y_clean)
        if len(y_noise) < len(y_clean):
            tmp = (len(y_clean) // len(y_noise)) + 1
            y_noise = np.array([x for j in [y_noise] * tmp for x in j])
            y_noise = y_noise[:len(y_clean)]
        else:
            ind = np.random.randint(1, len(y_noise) - len(y_clean) + 1)  # random select
            y_noise = y_noise[ind:ind + len(y_clean)]

        y_noise = y_noise - np.mean(y_noise)
        noise_variance = clean_pwr / (10 ** (snr / 10))
        noise = np.sqrt(noise_variance) * y_noise / np.std(y_noise)

        y_noisy = noise if isSilence else y_clean + noise
        Path(save_dir).parent.mkdir(exist_ok=True, parents=True)
        wavfile.write(save_dir, sr_clean, (y_noisy * np.iinfo(np.int16).max).astype('int16'))
        # wavfile.write(save_dir, sr_clean, y_noisy.astype(np.float32))
        # librosa.output.write_wav(save_dir, y_noisy.astype(np.float32), sr_clean, norm=False)

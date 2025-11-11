import os
import matplotlib.pyplot as plt
import librosa.display
import numpy as np
from pathlib import Path
from matplotlib import cm
from scipy import signal
from kudio.core.io import copy_waves, file_load

__all__ = [
    'Common',
    'WaveVisualizer',
    'history_plot'
]


def history_plot(history, metrics='loss', save_fig: str = None):
    # plt.figure()
    for_legend = []
    color = ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'b--', 'r:', 'c:', 'm:', 'k:', 'g--', 'y--']
    his_list = list(history.history.keys())
    for index, h_list in enumerate(his_list):
        if h_list.find(metrics) > -1:
            valid = history.history.get(h_list)
            plt.plot(valid, color[index], label='h_list')
            for_legend.append(h_list)
    plt.legend(for_legend, loc='upper left', fontsize='small')
    plt.title(metrics)
    plt.xlabel('Epoch')
    plt.ylabel(metrics)
    plt.grid(True)
    if save_fig is not None:
        if not os.path.isdir(os.path.basename(save_fig)):
            os.makedirs(os.path.basename(save_fig))
        if save_fig.endswith('.png'):
            plt.savefig("{}_{}".format(metrics, save_fig), dpi=150)
        else:
            plt.savefig("{}_{}.png".format(metrics, save_fig), dpi=150)
    plt.show()
    plt.close()


def hist_plt(hist, fig_dir=None, show:bool=False):
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.plot(hist.history['accuracy'])
    plt.plot(hist.history['val_accuracy'])
    plt.title('Model Accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper left')

    # Plot training & validation loss values
    plt.subplot(1, 2, 2)
    plt.plot(hist.history['loss'])
    plt.plot(hist.history['val_loss'])
    plt.title('Model Loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper left')

    plt.tight_layout()
    if fig_dir is not None:
        plt.savefig(str(fig_dir), dpi=150)
    if show:
        plt.show()
        plt.close()


class Common(object):
    def __init__(self, fig_dir: str = 'kd_figs', is_save=False):
        self.is_save = is_save
        if self.is_save:
            fig_dir = Path(fig_dir).absolute()
            fig_dir.mkdir(parents=True, exist_ok=True)

        self.plt = plt
        self.fig = self.plt.figure(figsize=(7, 5))
        self.plt.subplots_adjust(wspace=0.3, hspace=0.3)

    def loss_plot(self, loss, val_loss):
        """
        Plot loss curve.

        loss : list [ float ]
            training loss time series.
        val_loss : list [ float ]
            validation loss time series.

        return   : None
        """
        ax = self.fig.add_subplot(1, 1, 1)
        ax.cla()
        ax.plot(loss)
        ax.plot(val_loss)
        ax.set_title("Model loss")
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Loss")
        ax.legend(["Train", "Validation"], loc="upper right")

    def show(self):
        self.fig.show()

    def save(self, dir):
        if self.is_save:
            self.plt.savefig(dir)

    def close(self):
        self.plt.close()

    @staticmethod
    def plot_stft_w_2mfe(f, n_mels=40, sub_mfe_fq: int = 48000):
        f = Path(f)
        y, sr = librosa.load(str(f), sr=None, mono=True)

        fg = plt.figure(figsize=(12, 10), dpi=200)

        plt.subplot(311)
        plt.title(f.stem)
        librosa.display.waveplot(y, sr=sr)

        plt.subplot(312)
        plt.title(f'Mel Spectrogram {sr}KHz n:{n_mels}')
        # mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
        # librosa.display.specshow(log_mel_spectrogram, sr=sr, x_axis='time', y_axis='mel')
        mel_spect = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels)
        mel_spect2 = librosa.power_to_db(mel_spect, ref=np.max)
        librosa.display.specshow(mel_spect2, sr=sr, x_axis='time', y_axis='mel', fmax=sr // 2)

        plt.subplot(313)
        plt.title(f'Mel Spectrogram {sub_mfe_fq}KHz n:{n_mels}')
        mel_spect = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels, fmax=sub_mfe_fq)
        mel_spect2 = librosa.power_to_db(mel_spect, ref=np.max)
        librosa.display.specshow(mel_spect2, sr=sr, x_axis='time', y_axis='mel', fmax=sub_mfe_fq)

        plt.tight_layout()
        # plt.savefig(str(cls.fig_dir.joinpath(f'{f.stem}_n{n_mels}').with_suffix('.png')))
        plt.show()
        plt.close()


class WaveVisualizer(Common):
    def __init__(self, fig_size=(7, 5), dpi=200, subplots: int = None):
        super().__init__()
        self.plt = plt
        self.row_len = None
        if subplots is not None:
            self.row_len = subplots
            self.fig, self.ax = plt.subplots(self.row_len, 2, figsize=(11, 8))
        else:
            self.fig = self.plt.figure(figsize=fig_size, dpi=dpi)
        self.plt.subplots_adjust(wspace=0.3, hspace=0.3)

    def plot(self, wave_list, title=None):
        self.wave_length = len(wave_list)
        print(f'[kd.] plot {self.wave_length} wave(s)')
        if title is None or not len(title) == self.wave_length:
            title = [Path(w).stem for w in wave_list]

        for ind, (w, t) in enumerate(zip(wave_list, title)):
            self.ax[ind][0].set_title(str(t))
            y, sr = file_load(w)
            librosa.display.waveplot(y,
                                     sr=sr,
                                     ax=self.ax[ind][0])

            self.ax[ind][1].set_title(str(t))
            DA = librosa.amplitude_to_db(
                np.abs(librosa.stft(
                    y, n_fft=512, hop_length=256, win_length=512, window='hamming')), ref=np.max)
            librosa.display.specshow(DA,
                                     sr=sr,
                                     hop_length=256,
                                     x_axis='time',
                                     y_axis='linear',
                                     cmap=cm.get_cmap('jet'),
                                     ax=self.ax[ind][1])
        self.multi_hide_xlabel()
        self.fig.tight_layout()

    def multi_hide_xlabel(self):
        id = 0
        while id < self.wave_length - 1:
            self.ax[id, 0].set_xlabel("")
            self.ax[id, 1].set_xlabel("")
            id += 1

    def save(self, path):
        path = Path(path)
        if path.exists():
            print('[kd.] 檔案或路徑已存在')
            return
        self.plt.savefig(path)

    def copy_wave(self, path, wave_list):
        copy_waves(path, wave_list)


def basic_analyze(file, show: bool = False, save_dir=None):
    # 畫 波形圖, STFT, ZCR
    x, sr = file_load(file)

    plt.figure(figsize=(10, 8), dpi=200)
    plt.subplot(311)
    plt.title(Path(file).stem)
    librosa.display.waveplot(x, sr=sr)

    # display Spectrogram
    X = librosa.stft(x)
    Xdb = librosa.amplitude_to_db(abs(X))
    plt.subplot(312)
    plt.title('STFT')
    librosa.display.specshow(Xdb, sr=sr, x_axis='time', y_axis='hz', cmap=cm.get_cmap('jet'))
    # librosa.display.specshow(Xdb, sr=sr, x_axis='time', y_axis='log')
    # plt.colorbar()

    # Zero-crossing-rate
    plt.subplot(313)
    plt.title('ZCR')
    zcrs = librosa.feature.zero_crossing_rate(x + 0.0001)
    time2 = np.linspace(0, int((len(x) / sr)), len(zcrs[0]))
    plt.plot(time2, zcrs[0])
    plt.axis([0, int(len(x) / sr), 0, max(zcrs[0])])

    plt.tight_layout()

    if save_dir is not None:
        # save_dir = Path(save_dir)
        plt.savefig(str(save_dir))
    if show:
        plt.show()
    plt.close()


def plot_4_features(file, show: bool = False, save_dir=None, dpi=200):
    """
    Plot Waveform / Spectral Centroid / Spectral Rolloff / ZCR /Power Spectral Density
    """
    x, sr = file_load(file)

    ### Normalising the spectral centroid for visualisation

    fig, ax = plt.subplots(2, 1, figsize=(10, 10), dpi=dpi)

    # Plotting the Spectral Centroid along the waveform
    librosa.display.waveplot(x, sr=sr, alpha=0.4, ax=ax[0], label='waveform')
    plot_spectral_centroid(ax[0], x, sr, color='r', label='spectral_centroid')

    # Spectral Rolloff
    # librosa.display.waveplot(x, sr=sr, alpha=0.4, ax=ax[1])
    plot_spectral_rolloff(ax[0], x, sr, color='b', label='spectral_rolloff')

    plot_zcr(ax[0], x, sr, color='g', label='zcr')

    plot_power_spectral_density(ax[1], x, sr)

    ax[0].set_xlim(0, int(len(x) / sr))
    ax[0].grid(which='major', axis='both')
    ax[0].set_title('spectral centroid & spectral rolloff & zcr')
    # ax[0].set_aspect('auto')
    # ax[0].minorticks_on()

    plt.tight_layout()
    if save_dir is not None:
        plt.savefig(save_dir)
    if show is not None:
        plt.show()
    plt.close()


def plot_3_features(file, show: bool = False, save_dir=None, dpi=200):
    """
    Plot Waveform / Spectral Centroid / Spectral Rolloff / ZCR
    """
    x, sr = file_load(file)

    ### Normalising the spectral centroid for visualisation

    fig, ax = plt.subplots(figsize=(7, 5), dpi=dpi)

    # Plotting the Spectral Centroid along the waveform
    librosa.display.waveplot(x, sr=sr, alpha=0.4, ax=ax, label='waveform')
    plot_spectral_centroid(ax, x, sr, color='r', label='spectral_centroid')

    # Spectral Rolloff
    # librosa.display.waveplot(x, sr=sr, alpha=0.4, ax=ax[1])
    plot_spectral_rolloff(ax, x, sr, color='b', label='spectral_rolloff')

    plot_zcr(ax, x, sr, color='g', label='zcr')

    # plot_power_spectral_density(ax[1], x, sr)

    ax.set_xlim(0, int(len(x) / sr))
    ax.grid(which='major', axis='both')
    ax.set_title('spectral centroid & spectral rolloff & zcr')

    plt.tight_layout()
    if save_dir is not None:
        plt.savefig(save_dir)
    if show is not None:
        plt.show()
    plt.close()


def plot_PSD(file, show: bool = False, save_dir=None, dpi=200):
    """
    Plot Power Spectral Density
    """
    x, sr = file_load(file)

    fig, ax = plt.subplots(figsize=(7, 5), dpi=dpi)

    plot_power_spectral_density(ax, x, sr)

    plt.tight_layout()
    if save_dir is not None:
        plt.savefig(save_dir)
    if show is not None:
        plt.show()
    plt.close()


def normalize(x, axis=0):
    import sklearn.preprocessing as skp
    return skp.minmax_scale(x, axis=axis)
    # try:
    #     import sklearn
    #     return sklearn.preprocessing.minmax_scale(x, axis=axis)
    # except Exception as e:
    #     print(e)
    #     _mean = np.mean(spectral_centroids)
    #     _std = np.std(spectral_centroids) + 1e-12
    #     return (spectral_centroids - _mean) / _std


def plot_spectral_centroid(ax, y, sr, color='r', label=None):
    ### spectral centroid -- centre of mass -- weighted mean of the frequencies present in the sound
    spectral_centroids = librosa.feature.spectral_centroid(y, sr=sr)[0]

    ### Computing the time variable for visualization
    # frames = range(len(spectral_centroids))
    # t = librosa.frames_to_time(frames, sr=sr)
    t = np.linspace(0, int((len(y) / sr)), len(spectral_centroids))

    ax.plot(t, normalize(spectral_centroids), color=color, label=label)
    ax.set_title('Spectral Centroid')
    # ax.axis([0, int(len(y) / sr), 0, max(spectral_centroids)])
    if label is not None: ax.legend()


def plot_spectral_rolloff(ax, y, sr, color='r', label=None):
    # Spectral Rolloff
    spectral_rolloff = librosa.feature.spectral_rolloff(y, sr=sr)[0]

    # frames = range(len(spectral_rolloff))
    # t = librosa.frames_to_time(frames, sr=sr)
    t = np.linspace(0, int((len(y) / sr)), len(spectral_rolloff))

    ax.plot(t, normalize(spectral_rolloff), color=color, label=label)
    # ax.axis([0, int(len(y) / sr), 0, max(spectral_rolloff)])
    ax.set_title('Spectral Rolloff')
    if label is not None: ax.legend()


def plot_power_spectral_density(ax, y, sr, color='b', label=None):
    # Compute and plot the power spectral density.
    freqs, psd = signal.welch(y, sr, nfft=1024)
    ax.semilogx(freqs, psd, color=color, label=label)
    ax.set_title('Power Spectral Density')
    ax.set_xlabel('Frequency[Hz]')
    ax.set_ylabel('PSD [V**2/Hz]')
    ax.grid(which='major', axis='both')
    if label is not None: ax.legend()


def plot_zcr(ax, y, sr, color='r', label=None):
    ax.set_title('ZCR')
    zcrs = librosa.feature.zero_crossing_rate(y + 0.0001)
    time2 = np.linspace(0, int((len(y) / sr)), len(zcrs[0]))
    ax.plot(time2, zcrs[0], color=color, label=label)
    # ax.axis([0, int(len(y) / sr), 0, max(zcrs[0])])
    if label is not None: ax.legend()

# -*- coding: utf-8 -*-
import sys
import librosa
import numpy as np
import scipy.signal
from scipy.io import wavfile
from pathlib import Path
from tqdm import tqdm
from kudio.core.io import file_load

__all__ = [
    'wave_separate',
    'concat_mfcc_',
    'concat_mfcc',
    'concat_logspec',
    'concat_logspec_',
    'contextual_LogSpectrogram',
    'wav2spec',
    'spec2wav',
    'wavform2spec',
    'spec2wavform',
    'w2mfcc',
    'wav2mfcc',
    'w2s',
    's2w',
    'denoise_wav2spec',
    'denoise_spec2wav',
    'wave_slicing',
    'features2matrix',
    'wav2mel',
]


def wave_separate(wave: np.ndarray, channels: int) -> list:
    """
    For Respeaker Mic Array

    Separate inputs by number of channels

    :param wave: 原始音頻
    :param channels: 欲分割通道數量
    :return: list
    """
    # if channels == 1:
    #     return wave
    # elif channels > 1:
    #     print("[kd.] separate - input shape:", wave.shape)
    #     w_list = [wave[c::channels] for c in range(channels)]
    #     w_list[0] = w_list[0][:len(w_list[1])]  ## Make sure each list is the same length
    #     w_array = np.vstack(w_list)
    #     print("[kd.] separate - output shape:", w_array.shape)
    #     return w_array
    # else:
    #     raise Exception("[kd.] separate - error")
    return [wave[c::channels] for c in range(channels)]


def concat_mfcc(wav_list, n_mfcc=40, desired_samples=None, desired_length=None):
    """
    將音檔轉為梅爾倒頻譜

    Look at:
        librosa.feature.mfcc

    Parameters:
        wav_list : list
            wave list

        desired_samples:
            specified length

    Returns:
        y_out : np.ndarray
    """
    mfcc_list = []
    for wav_dir in tqdm(wav_list):
        y, sr = file_load(wav_dir)
        if desired_length:
            y = y[:sr * desired_length]
        if desired_samples and desired_samples < len(y):
            y = y[:desired_samples]
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc).T
        mfcc = mfcc.reshape(1, mfcc.shape[0], -1)
        mfcc_list.append(mfcc)
    return np.vstack(mfcc_list)


concat_mfcc_ = concat_mfcc


def contextual_LogSpectrogram(wav_list,
                              sequence,
                              forward_backward,
                              norm,
                              hop_length=256,
                              n_fft=512,
                              win_length=512,
                              desired_samples=None):
    """
    將音檔轉為對數頻譜並堆疊

    Look at:
        wavform2spec, librosa.stft

    Examples:
        >>> ret = contextual_LogSpectrogram(wave_list,False,0,False)

        >>> ret = contextual_LogSpectrogram(wave_list,True,0,True,desired_samples)

    Parameters:
        wav_list : list

        sequence: bool
            convert to time serial

        forward_backward: int >=0
            contexture spectrogram

        norm: bool
            normalize

        desired_samples:
            specified length

    Returns:
        y_out : np.ndarray
    """
    return np.vstack(
        [wav2spec(
            file=file,
            sequence=sequence,
            forward_backward=forward_backward,
            norm=norm,
            hop_length=hop_length,
            n_fft=n_fft,
            win_length=win_length,
            desired_length=desired_samples,
            resample_rate=None) for file in tqdm(wav_list, desc='[kd.] Concatenate spectrograms')
        ])


concat_logspec = contextual_LogSpectrogram
concat_logspec_ = contextual_LogSpectrogram


def f2s(file,
        sequence=False,
        forward_backward=False,
        norm=False,
        hop_length=256,
        n_fft=512,
        win_length=512,
        desired_length=None,
        resample_rate=None) -> np.ndarray:
    y, rate = file_load(file, sr=resample_rate, mono=True)

    return wavform2spec(
        y, sequence, forward_backward, norm, hop_length, n_fft, win_length,
        desired_length=desired_length)


def s2w(wave_out_dir, noisy_file, enhanced_spec,
        squeeze=False, hop_length=256, n_fft=512, win_length=512, window='hamming'):
    """
    waveform to spectrogram

    -> librosa.stft

    -> kudio.spec2wavform

    Parameters:
        wave_out_dir : str
            wave path

        noisy_file : str
            wave path
    """
    y, rate = librosa.load(noisy_file, sr=16000)

    y_out = spec2wavform(y, enhanced_spec, squeeze, hop_length,
                         n_fft, win_length, window)

    Path(wave_out_dir).parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(wave_out_dir, rate, (y_out * np.iinfo(np.int16).max).astype('int16'))
    # librosa.output.write_wav(str(wave_out_dir), y_out.astype(np.float32), rate, norm=False)


wav2spec = f2s
spec2wav = s2w


def w2s(y,
        sequence=False,
        forward_backward=0,
        norm=False,
        hop_length=256,
        n_fft=512,
        win_length=512,
        window='hamming',
        desired_length=None) -> np.ndarray:
    """
    waveform to spectrogram

    -> librosa.stft

    Parameters:
        y : np.ndarray [shape=(n,)], real-valued
            the input signal (audio time series)

        n_fft : int > 0 [scalar]
            FFT window size

        hop_length : int > 0 [scalar]
            number audio of frames between STFT columns.
            If unspecified, defaults `win_length / 4`.

        win_length  : int <= n_fft [scalar]
            Each frame of audio is windowed by `window()`.
            The window will be of length `win_length` and then padded
            with zeros to match `n_fft`.

            If unspecified, defaults to ``win_length = n_fft``.

        window : string, tuple, number, function, or np.ndarray [shape=(n_fft,)]
            - a window specification (string, tuple, or number);
              see `scipy.signal.get_window`
            - a window function, such as `scipy.signal.hanning`
            - a vector or array of length `n_fft`

            .. see also:: `filters.get_window`

        sequence: bool
            convert to time serial

        forward_backward: int >=0
            contexture spectrogram

        norm: bool
            normalize

        desired_length:
            specified length

    Returns:
        y_out : np.ndarray
    """
    if desired_length and desired_length < len(y):
        y = y[:desired_length]
    D = librosa.stft(y,
                     n_fft=n_fft,
                     hop_length=hop_length,
                     win_length=win_length,
                     window=window)
    epsilon = np.finfo(float).eps
    D = D + epsilon
    Sxx = np.log10(np.abs(D) ** 2)

    if norm:
        Sxx_mean = np.mean(Sxx, axis=1).reshape(Sxx.shape[0], 1)
        # Sxx_var = np.var(Sxx, axis=1).reshape(257, 1)
        Sxx_std = np.std(Sxx, axis=1).reshape((Sxx.shape[0], 1)) + 1e-12
        Sxx_r = (Sxx - Sxx_mean) / Sxx_std  # de Std
    else:
        Sxx_r = np.array(Sxx)

    idx = 0
    # set data into 3 dim and muti-frame(frame, sample, num_frame)
    if forward_backward:
        Sxx_r = Sxx_r.T
        return_data = np.empty(
            (Sxx_r.shape[0] + 50, int(forward_backward * 2) + 1,
             int(n_fft / 2) + 1), dtype=np.float32)
        # return_data = np.empty(
        #     (Sxx_r.shape[0] + 50, np.int32(forward_backward * 2) + 1,
        #      np.int32(n_fft / 2) + 1))
        frames, dim = Sxx_r.shape
        for num, data in enumerate(Sxx_r):
            idx_start = idx - forward_backward
            idx_end = idx + forward_backward
            if idx_start < 0:
                null = np.zeros((-idx_start, dim))
                tmp = np.concatenate((null, Sxx_r[0:idx_end + 1]), axis=0)
            elif idx_end > frames - 1:
                null = np.zeros((idx_end - frames + 1, dim))
                tmp = np.concatenate((Sxx_r[idx_start:], null), axis=0)
            else:
                tmp = Sxx_r[idx_start:idx_end + 1]
            return_data[idx] = tmp
            idx += 1
        shape = return_data.shape

        if sequence:
            # return return_data[:idx]
            return return_data.reshape(1, shape[0], shape[1] * shape[2])[:, :idx]  # (1,time_step,dim)
        else:
            return return_data.reshape(shape[0], shape[1] * shape[2])[:idx]
    else:
        Sxx_r = np.array(Sxx_r).T
        shape = Sxx_r.shape
        if sequence:
            return Sxx_r.reshape(1, shape[0], shape[1])
            # return Sxx_r.reshape(shape[0], 1, shape[1])
        else:
            return Sxx_r


wavform2spec = w2s


def spec2wavform(y, enhanced_spec, sequence=False, hop_length=256,
                 n_fft=512, win_length=512, window='hamming') -> np.ndarray:
    """
    spectrogram to waveform

    -> librosa.stft

    Parameters:
        y : np.ndarray [shape=(n,)], real-valued
            the input signal (audio time series)

        enhanced_spec: np.ndarray
            input spectrogram

        n_fft : int > 0 [scalar]
            FFT window size

        hop_length : int > 0 [scalar]
            number audio of frames between STFT columns.
            If unspecified, defaults `win_length / 4`.

        win_length  : int <= n_fft [scalar]
            Each frame of audio is windowed by `window()`.
            The window will be of length `win_length` and then padded
            with zeros to match `n_fft`.

            If unspecified, defaults to ``win_length = n_fft``.

        window : string, tuple, number, function, or np.ndarray [shape=(n_fft,)]
            - a window specification (string, tuple, or number);
              see `scipy.signal.get_window`
            - a window function, such as `scipy.signal.hanning`
            - a vector or array of length `n_fft`

            .. see also:: `filters.get_window`

        center      : boolean
            - If `True`, the signal `y` is padded so that frame
              `D[:, t]` is centered at `y[t * hop_length]`.
            - If `False`, then `D[:, t]` begins at `y[t * hop_length]`

        dtype       : numeric type
            Complex numeric type for `D`.  Default is 64-bit complex.

        pad_mode : string
            If `center=True`, the padding mode to use at the edges of the signal.
            By default, STFT uses reflection padding.


    Returns:
        y_out : np.ndarray
    """
    if sequence:
        enhanced_spec = enhanced_spec.squeeze()
    D = librosa.stft(y.astype('float32'),
                     hop_length=hop_length,
                     n_fft=n_fft,
                     win_length=win_length,
                     window=window)
    epsilon = np.finfo(float).eps
    D = D + epsilon
    phase = np.exp(1j * np.angle(D))
    Sxx_r_tmp = np.array(enhanced_spec)  # enhanced log power magnitude: spec_test
    Sxx_r_tmp = np.sqrt(10 ** Sxx_r_tmp)
    Sxx_r = Sxx_r_tmp.T
    reverse = np.multiply(Sxx_r, phase)
    result = librosa.istft(reverse, hop_length=hop_length, win_length=win_length, window='hamming')
    y_out = librosa.util.fix_length(result, len(y), mode='edge')
    # y_out = y_out/np.max(np.abs(y_out))
    return y_out


def w2mfcc(y, sr, n_mfcc=40):
    return librosa.feature.mfcc(y, sr, n_mfcc=n_mfcc).T.reshape(1, -1, n_mfcc)


wav2mfcc = w2mfcc


def denoise_wav2spec(waveform):
    D = librosa.stft(waveform / np.max(abs(waveform)),
                     n_fft=512,
                     hop_length=256,
                     win_length=512,
                     window=scipy.signal.hanning)

    D += np.finfo(float).eps
    Sxx = np.abs(D)
    phase = np.angle(D)

    Sxx_mean = np.mean(Sxx, axis=1).reshape((257, 1))
    Sxx_std = np.std(Sxx, axis=1).reshape((257, 1)) + 1e-12
    Sxx_r = (Sxx - Sxx_mean) / Sxx_std
    return np.reshape(Sxx_r.T, (1, Sxx_r.shape[1], 257)), phase


def denoise_spec2wav(spec, phase):
    spec = np.squeeze(spec).T

    pred_wav = librosa.istft(np.multiply(spec, np.exp(1j * phase)),
                             hop_length=256,
                             win_length=512,
                             window=scipy.signal.hanning)
    return pred_wav / np.max(abs(pred_wav))


def wave_slicing(y: np.ndarray,
                 frame_length=2048,
                 hop_length=512,
                 is_reshape=True) -> np.ndarray:
    """
    Slice a time series waveform into overlapping frames

    :param y: np.ndarray [shape=(n,)]
        Time series to frame. Must be one-dimensional and contiguous
        in memory.
    :param frame_length: int > 0 [scalar]
        Length of the frame in samples
    :param hop_length: int > 0 [scalar]
        Number of samples to hop between frames
    :param is_reshape: bool
        Reshape to one dimension
    :return: np.ndarray
    """
    frame_stack = librosa.util.frame(
        y, frame_length=frame_length, hop_length=hop_length)
    if is_reshape:
        frame_stack = frame_stack.T.reshape(-1)
    return frame_stack


def features2matrix(features):
    """
    features_to_matrix(features)

    This function takes a list of feature matrices as argument and returns
    a single concatenated feature matrix and the respective class labels.

    ARGUMENTS:
        - features:        a list of feature matrices

    RETURNS:
        - feature_matrix:    a concatenated matrix of features
        - labels:            a vector of class indices
    """

    labels = np.array([])
    feature_matrix = np.array([])
    for i, f in enumerate(features):
        if i == 0:
            feature_matrix = f
            labels = i * np.ones((len(f), 1))
        else:
            feature_matrix = np.vstack((feature_matrix, f))
            labels = np.append(labels, i * np.ones((len(f), 1)))
    return feature_matrix, labels


def wav2mel(file_name,
            n_mels=64,
            n_frames=5,
            n_fft=1024,
            hop_length=512,
            power=2.0):
    # calculate the number of dimensions
    dims = n_mels * n_frames
    # generate melspectrogram using librosa
    y, sr = file_load(file_name, mono=True)
    mel_spectrogram = librosa.feature.melspectrogram(y=y,
                                                     sr=sr,
                                                     n_fft=n_fft,
                                                     hop_length=hop_length,
                                                     n_mels=n_mels,
                                                     power=power)
    # convert melspectrogram to log mel energies
    log_mel_spectrogram = 20.0 / power * np.log10(np.maximum(mel_spectrogram, sys.float_info.epsilon))

    # calculate total vector size
    n_vectors = len(log_mel_spectrogram[0, :]) - n_frames + 1

    # skip too short clips
    if n_vectors < 1:
        return np.empty((0, dims))

    # generate feature vectors by concatenating multiframes
    vectors = np.zeros((n_vectors, dims))
    for t in range(n_frames):
        vectors[:, n_mels * t: n_mels * (t + 1)] = log_mel_spectrogram[:, t: t + n_vectors].T

    return vectors

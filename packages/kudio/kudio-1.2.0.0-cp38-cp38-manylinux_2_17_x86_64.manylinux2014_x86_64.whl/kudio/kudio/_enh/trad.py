import numpy as np
import pywt

__all__ = ['trad_enhance']


def wavelet_low_pass_filter(y, thres=0.8, wavelet='db2'):
    coeff = pywt.wavedec(y, wavelet, mode='per')
    coeff[1:] = (pywt.threshold(i, value=thres * np.nanmax(y), mode='soft') for i in coeff[1:])
    return pywt.waverec(coeff, wavelet, mode='per')


def trad_enhance(y, sr):
    # noise estimation with wiener filter
    # calculation parameters
    len_ = 512  # 20 * sr // 1000  # frame size in samples
    PERC = 50  # window overlop in percent of frame
    len1 = len_ * PERC // 100  # overlop'length
    len2 = len_ - len1  # window'length - overlop'length
    # setting default parameters
    Expnt = 2.0
    beta = 0.002
    win = np.hamming(len_)  # hamming window
    winGain = len2 / sum(win)
    nFFT = 2 * 2 ** 8
    # initialize various variables
    k = 1
    img = 1j
    x_old = np.zeros(len1)
    Nframes = len(y) // len2 - 1
    xfinal = np.zeros((Nframes + 1) * len2)

    para = []
    for n in range(0, Nframes):
        # Windowing
        insign = win * y[k - 1: k + len_ - 1]

        # compute fourier transform of a frame
        spec = np.fft.fft(insign, nFFT)

        # compute the magnitude
        sig = abs(spec)

        # noisy speech power spec
        ns_ps = sig ** 2

        # save the noisy phase information
        theta = np.angle(spec)

        # Noise Estimation
        # Init_Weight、ConMinTrack、MCRA、MCRA2
        if n == 0:
            para = INIT(ns_ps, sr).mcra()
        else:
            para = EST(ns_ps, para).mcra()
        noise_ps = para['noise_ps']
        noise_mu = np.sqrt(noise_ps)

        # Posterior SNR
        SNRpos = 10 * np.log10(np.linalg.norm(sig, 2) ** 2 / np.linalg.norm(noise_mu, 2) ** 2)

        # --- wiener filtering --- #
        # setting SNR & alpha
        if Expnt == 1.0:  # magnitude spectrum
            if SNRpos < -5.0:
                alpha = 4
            elif SNRpos > 20:
                alpha = 1
            else:
                alpha = 3 - SNRpos * 2 / 20
        else:  # power spectrum
            if SNRpos < -5.0:
                alpha = 5
            elif SNRpos > 20:
                alpha = 1
            else:
                alpha = 4 - SNRpos * 3 / 20

        # 1 over subtraction
        sub_speech = sig ** Expnt - alpha * noise_mu ** Expnt

        # the pure signal is less than the noise signal power
        diffw = sub_speech - beta * noise_mu ** Expnt

        # beta negative components
        # find_index
        index_list = []
        for i in range(len(diffw)):
            if diffw[i] < 0:
                index_list.append(i)

        if len(index_list) > 0:
            # The lower bound is represented by the estimated noise signal
            for i in range(len(index_list)):
                sub_speech[index_list[i]] = beta * noise_mu[index_list[i]] ** Expnt

        # Priori SNR
        SNRpri = 10 * np.log10(np.linalg.norm(sub_speech ** (1 / Expnt), 2) ** 2 / np.linalg.norm(noise_mu, 2) ** 2)

        # parameter to deal mel
        mel_max = 10
        mel_0 = (1 + 4 * mel_max) / 5
        s = 25 / (mel_max - 1)

        # # setting mel
        if SNRpri < -5.0:
            mel = mel_max
        elif SNRpri > 20:
            mel = 1
        else:
            mel = mel_0 - SNRpri / s

        # 2 gain function Gk
        g_k = sub_speech / (sub_speech + mel * noise_mu ** Expnt)
        wf_speech = g_k * sig

        # add phase
        # wf_speech[nFFT // 2 + 1:nFFT] = np.flipud(wf_speech[1:nFFT // 2])
        x_phase = wf_speech * np.exp(img * theta)

        # take the IFFT
        xi = np.fft.ifft(x_phase).real

        # --- Overlap and add --- #
        xfinal[k - 1: k + len2 - 1] = x_old + xi[0: len1]
        x_old = xi[0 + len1: len_]
        k = k + len2

    return winGain * xfinal


class INIT:

    def __init__(self, ns_ps, fs):
        self.ns_ps = ns_ps
        self.fs = fs

    # Weighted spectral average
    def weight(self):
        parameters = {'ass': 0.85, 'beta': 1.5, 'noise_ps': self.ns_ps, 'P': self.ns_ps}
        return parameters

    # Continuous minimal tracking
    def com_min_track(self):
        len_val = len(self.ns_ps)
        parameters = {'n': 2, 'leng': len_val, 'alpha': 0.7, 'beta': 0.96, 'gamma': 0.998, 'noise_ps': self.ns_ps,
                      'pxk_old': self.ns_ps, 'pxk': self.ns_ps, 'pnk_old': self.ns_ps,
                      'pnk': self.ns_ps}
        return parameters

    # MCRA algorithm
    def mcra(self):
        len_val = len(self.ns_ps)
        parameters = {'n': 2, 'ad': 0.95, 'ass': 0.8, 'L': 1000 * 2 // 20, 'delta': 5, 'ap': 0.2, 'leng': len_val,
                      'P': self.ns_ps, 'Pmin': self.ns_ps, 'Ptmp': self.ns_ps, 'pk': np.zeros(len_val),
                      'noise_ps': self.ns_ps}
        return parameters

    # MCRA2 algorithm
    def mcra2(self):
        len_val = len(self.ns_ps)
        freq_res = self.fs / len_val
        k_1khz = int(1000 // freq_res)
        k_3khz = int(3000 // freq_res)

        # [9.60] delta
        low_1 = 2 * np.ones(k_1khz, dtype=np.int),
        low_2 = 2 * np.ones(k_3khz - k_1khz, dtype=np.int),
        high = 5 * np.ones(len_val // 2 - k_3khz, dtype=np.int),
        delta_val = np.append(np.append(np.append(np.append(np.append(low_1, low_2), high), high), low_2), low_1)

        parameters = {'n': 2, 'leng': len_val, 'ad': 0.95, 'ass': 0.8, 'ap': 0.2, 'beta': 0.8, 'beta1': 0.98,
                      'gamma': 0.998, 'alpha': 0.7, 'delta': delta_val, 'pk': np.zeros(len_val), 'noise_ps': self.ns_ps,
                      'pxk_old': self.ns_ps, 'pxk': self.ns_ps, 'pnk_old': self.ns_ps, 'pnk': self.ns_ps}
        return parameters


class EST:

    def __init__(self, ns_ps, para):
        self.ns_ps = ns_ps
        self.para = para

    # Weighted spectral average
    def weight(self):

        # input para
        ass = self.para['ass']
        beta = self.para['beta']
        noise_ps = self.para['noise_ps']
        P = self.para['P']
        P = ass * P + (1 - ass) * self.ns_ps

        # noise estiamtion
        # [9.30] in the power-spectrum domain
        for i in range(len(noise_ps)):
            if P[i] < beta * noise_ps[i]:
                noise_ps[i] = ass * noise_ps[i] + (1 - ass) * P[i]

        # output para
        self.para['P'] = P
        self.para['noise_ps'] = noise_ps
        return self.para

    # Continuous minimal tracking
    def com_min_track(self):
        # input para
        n = self.para['n']
        leng = self.para['leng']
        alpha = self.para['alpha']
        beta = self.para['beta']
        gamma = self.para['gamma']
        noise_ps = self.para['noise_ps']
        pxk_old = self.para['pxk_old']
        pxk = self.para['pxk']
        pnk_old = self.para['pnk_old']
        pnk = self.para['pnk']

        # noise estimation
        # [9.24]
        pxk = alpha * pxk_old + (1 - alpha) * self.ns_ps
        # [9.25]
        for t in range(leng):
            if pnk_old[t] <= pxk[t]:
                pnk[t] = (gamma * pnk_old[t]) + (((1 - gamma) / (1 - beta)) * (pxk[t] - beta * pxk_old[t]))
            else:
                pnk[t] = pxk[t]
        pxk_old = pxk
        pnk_old = pnk
        noise_ps = pnk

        # output
        self.para['n'] = n + 1
        self.para['noise_ps'] = noise_ps
        self.para['pnk'] = pnk
        self.para['pnk_old'] = pnk_old
        self.para['pxk'] = pxk
        self.para['pxk_old'] = pxk_old
        return self.para

    # MCRA algorithm
    def mcra(self):
        # input para
        ass = self.para['ass']
        ad = self.para['ad']
        ap = self.para['ap']
        pk = self.para['pk']
        delta = self.para['delta']
        L = self.para['L']
        n = self.para['n']
        leng = self.para['leng']
        noise_ps = self.para['noise_ps']
        P = self.para['P']
        Pmin = self.para['Pmin']
        Ptmp = self.para['Ptmp']

        # noise estimation
        # [9.55]
        P = ass * P + (1 - ass) * self.ns_ps
        # [9.23]
        if n % L == 0:
            Pmin = np.minimum(Ptmp, P)
            Ptmp = P
        else:
            Pmin = np.minimum(Pmin, P)
            Ptmp = np.minimum(Ptmp, P)
        # [9.58]
        Srk = P / Pmin
        Ikl = np.zeros(leng)
        for i in range(len(Ikl)):
            if Srk[i] > delta:
                Ikl[i] = 1
        # [9.59]
        pk = ap * pk + (1 - ap) * Ikl
        # [9.54]
        adk = ad + (1 - ad) * pk
        # [9.53]
        noise_ps = adk * noise_ps + (1 - adk) * self.ns_ps

        # output para
        self.para['pk'] = pk
        self.para['n'] = n + 1
        self.para['noise_ps'] = noise_ps
        self.para['P'] = P
        self.para['Pmin'] = Pmin
        self.para['Ptmp'] = Ptmp
        return self.para

    # MCRA2 algorithm
    def mcra2(self):
        # input para
        n = self.para['n']
        leng = self.para['leng']
        ad = self.para['ad']
        ass = self.para['ass']
        ap = self.para['ap']
        beta = self.para['beta']
        gamma = self.para['gamma']
        alpha = self.para['alpha']
        pk = self.para['pk']
        delta = self.para['delta']
        noise_ps = self.para['noise_ps']
        pxk = self.para['pxk']
        pnk = self.para['pnk']
        pxk_old = self.para['pxk_old']
        pnk_old = self.para['pnk_old']

        # noise estimation
        # [9.61]
        pxk = alpha * pxk_old + (1 - alpha) * self.ns_ps
        # [9.25]
        for i in range(len(pnk)):
            if pnk_old[i] < pxk[i]:
                pnk[i] = (gamma * pnk_old[i]) + (((1 - gamma) / (1 - beta)) * (pxk[i] - beta * pxk_old[i]))
        pxk_old = pxk
        pnk_old = pnk
        # [9.57]
        Srk = np.zeros(leng)
        Srk = pxk / pnk
        # [9.58]
        Ikl = np.zeros(leng)
        for i in range(len(Ikl)):
            if Srk[i] > delta[i]:
                Ikl[i] = 1
        # [9.59]
        pk = ap * pk + (1 - ap) * Ikl
        # [9.54]
        adk = ad + (1 - ad) * pk
        # [9.53]
        noise_ps = adk * noise_ps + (1 - adk) * pxk
        # output para
        self.para['n'] = n + 1
        self.para['pk'] = pk
        self.para['noise_ps'] = noise_ps
        self.para['pnk'] = pnk
        self.para['pnk_old'] = pnk_old
        self.para['pxk'] = pxk
        self.para['pxk_old'] = pxk_old
        return self.para

import os
import re
import numpy as np
import pandas as pd
from scipy.io import wavfile
from tqdm import tqdm
from kudio.util import warn, pur, cya, blu

__all__ = ['AudioEvaluate', 'eval_metrics']


def check_metrics_install():
    # SDR
    try:
        import mir_eval

        SDR_OK = True
    except ModuleNotFoundError:
        warn("No module named 'mir_eval' !!")
        os.system("pip install mir_eval")
        try:
            import mir_eval

            SDR_OK = True
        except:
            SDR_OK = False
    except:
        SDR_OK = False

    # STOI
    try:
        from pystoi import stoi

        STOI_OK = True
    except ModuleNotFoundError:
        warn("No mself.odule named 'pystoi' !!")
        os.system("pip install pystoi")
        try:
            from pystoi import stoi

            STOI_OK = True
        except:
            STOI_OK = False
    except:
        STOI_OK = False

    # PESQ

    """
    https://github.com/schmiph2/pysepm
    """
    try:
        import pysepm

        PESQ_OK = True
    except ModuleNotFoundError:
        warn("No mself.odule named 'pypesq' !!")
        os.system("pip3 install https://github.com/schmiph2/pysepm/archive/master.zip")
        try:
            import pysepm

            PESQ_OK = True
        except:
            PESQ_OK = False
    except:
        PESQ_OK = False
    return PESQ_OK, STOI_OK, SDR_OK


class AudioEvaluate(object):
    """ AudioEvaluate 音頻評估
    ------------
    評估指標： PESQ, STOI, SDR
    ------------

    ------------------------------------------------------------

    使用方法
    ------------
    >>> audio_eval = AudioEvaluate(clean_list, noisy_list)
        :clean_list: 為乾淨(無噪聲)音頻列表
        :noisy_list: 為原始(帶噪聲)音頻列表

    >>> audio_eval.eval(enhance_method, enhanced_list)
        :enhance_method: 可自定任何文字, 方便辨別
        :enhanced_list: 為處理後(目標)音頻列表, 與clean_list, noisy_list同時評估

    >>> df = audio_eval.get_df()
        :return df: 返回評估結果, 型態為pandas.Dataframe
    """

    def __init__(self, clean_list, noisy_list):
        self.enhanced_list = None
        self.clean_list = clean_list
        self.noisy_list = noisy_list

        self.pesq_status, self.stoi_status, self.sdr_status = check_metrics_install()

        self.score_dict = {"Enh_method": []}
        if self.pesq_status: self.score_dict["PESQ"] = []
        if self.stoi_status: self.score_dict["STOI"] = []
        if self.sdr_status: self.score_dict["SDR"] = []

    def eval(self, enhance_method, enhanced_list):
        # sort enh. list by noisy list
        enh_names = [i.stem for i in enhanced_list]
        # for n in self.noisy_list:
        #     if n.stem == enh_names[0]:
        #         print(True)
        assert len(self.noisy_list) == len(enh_names), 'Check number of files'
        index = [enh_names.index(n.stem) for n in self.noisy_list]
        if len(self.noisy_list) != len(index):
            raise Exception("Noisy list is not the same as Enhancement list.")
        self.enhanced_list = np.array(enhanced_list)[index]

        self.base_pesq, self.base_stoi, self.base_sdr = [], [], []
        self.score_dict['Enh_method'].append(enhance_method)
        if self.pesq_status:
            self.base_pesq, pesq = self.__pesq_score()
            self.score_dict['PESQ'].append(np.around(pesq, 4))
        if self.stoi_status:
            self.base_stoi, stoi = self.__stoi_score()
            self.score_dict['STOI'].append(np.around(stoi, 4))
        if self.sdr_status:
            self.base_sdr, sdr = self.__sdr_score()
            self.score_dict['SDR'].append(np.around(sdr, 4))

    def get_df(self):
        if self.base_pesq or self.base_stoi or self.base_sdr:
            self.score_dict['Enh_method'].append('Baseline')
            if self.base_pesq:  self.score_dict['PESQ'].append(np.around(self.base_pesq, 4))
            if self.base_stoi: self.score_dict['STOI'].append(np.around(self.base_stoi, 4))
            if self.base_sdr: self.score_dict['SDR'].append(np.around(self.base_sdr, 4))
            return pd.DataFrame.from_dict(self.score_dict, orient='columns')
        else:
            return []

    def __sdr_score(self):
        import mir_eval
        pur("==== Evaluate SDR ====")
        df = pd.DataFrame(columns=['wave', 'Baseline-SDR', 'Enhance-SDR'])
        for cln, noy, enh in tqdm(zip(self.clean_list, self.noisy_list, self.enhanced_list)):
            sr, cln_wave = wavfile.read(cln)
            _, noy_wave = wavfile.read(noy)
            _, enh_wave = wavfile.read(enh)
            cln_wave = cln_wave.reshape(1, -1)
            noy_wave = noy_wave.reshape(1, -1)
            enh_wave = enh_wave.reshape(1, -1)
            mir_eval.separation.validate(cln_wave, noy_wave)
            mir_eval.separation.validate(cln_wave, enh_wave)
            sdr_base, sir, sar, perm = mir_eval.separation.bss_eval_sources(cln_wave, noy_wave)
            sdr_enh, sir, sar, perm = mir_eval.separation.bss_eval_sources(cln_wave, enh_wave)
            df = df.append({'wave': os.path.basename(cln),
                            'Baseline-SDR': float(sdr_base),
                            'Enhance-SDR': float(sdr_enh)
                            }, ignore_index=True)
        sdr_mean = df.dropna().mean()
        cya('sdr_mean:\n{}'.format(sdr_mean))
        return sdr_mean

    def __stoi_score(self):
        from pystoi import stoi
        pur("==== Evaluate STOI ====")
        df = pd.DataFrame(columns=['wave', 'Baseline-STOI', 'Enhance-STOI'])
        for cln, noy, enh in tqdm(zip(self.clean_list, self.noisy_list, self.enhanced_list)):
            sr, cln_wave = wavfile.read(cln)
            _, noy_wave = wavfile.read(noy)
            _, enh_wave = wavfile.read(enh)
            stoi_base = stoi(cln_wave, noy_wave, sr, extended=False)
            stoi_enh = stoi(cln_wave, enh_wave, sr, extended=False)
            df = df.append({'wave': os.path.basename(cln),
                            'Baseline-STOI': float(stoi_base),
                            'Enhance-STOI': float(stoi_enh)
                            }, ignore_index=True)
        stoi_mean = df.dropna().mean()
        cya('stoi_mean:\n{}'.format(stoi_mean))
        return stoi_mean

    def __pesq_score(self):
        pur("==== Evaluate PESQ ====")
        df = pd.DataFrame(columns=['wave', 'Baseline-PESQ', 'Enhance-PESQ'])
        for cln, noy, enh in tqdm(zip(self.clean_list, self.noisy_list, self.enhanced_list)):
            cln = str(cln)
            noy = str(noy)
            enh = str(enh)
            pesq_base = os.popen('pesq.exe +16000 ' + cln + ' ' + noy).readlines()[-1]
            pesq_enh = os.popen('pesq.exe +16000 ' + cln + ' ' + enh).readlines()[-1]
            # print('Base={}Enh={}'.format(pesq_base, pesq_enh))
            try:
                df = df.append({'wave': os.path.basename(cln),
                                'Baseline-PESQ': float(re.sub(r'^.*= ', '', pesq_base.strip('\n'))),
                                'Enhance-PESQ': float(re.sub(r'^.*= ', '', pesq_enh.strip('\n')))
                                }, ignore_index=True)
            except ValueError:
                df = df.append({'wave': os.path.basename(cln),
                                'Baseline-PESQ': np.NaN,
                                'Enhance-PESQ': np.NaN
                                }, ignore_index=True)
        pesq_mean = df.dropna().mean()
        cya('pesq_mean:\n{}'.format(pesq_mean))
        return pesq_mean

    def __pesq_score_v2(self):
        # For linux system
        from pypesq import pesq
        df = pd.DataFrame(columns=['wave', 'Baseline-PESQ', 'Enhance-PESQ'])
        for cln, noy, enh in tqdm(zip(self.clean_list, self.noisy_list, self.enhanced_list)):
            sr, cln_wave = wavfile.read(cln)
            _, noy_wave = wavfile.read(noy)
            _, enh_wave = wavfile.read(enh)
            # y, rate = librosa.load(cln,sr=16000)
            # pesq_base = pesq(y, y, rate, 'wb')
            pesq_base = pesq(cln_wave, noy_wave, sr, 'wb')
            pesq_enh = pesq(cln_wave, enh_wave, sr, 'wb')
            df = df.append({'wave': os.path.basename(cln),
                            'Baseline-PESQ': pesq_base,
                            'Enhance-PESQ': pesq_enh
                            }, ignore_index=True)
        pesq_mean = df.dropna().mean()
        blu('pesq_mean:\n{}'.format(pesq_mean))
        return pesq_mean


def eval_metrics(rate, ref, deg):
    pesq_status, stoi_status, sdr_status = check_metrics_install()
    csv_lines = []
    pesq_base, stoi_base, sdr_base = None, None, None

    # The shape of estimated sources and the true sources should match
    if len(ref) > len(deg):
        ref = ref[:len(deg)]
    else:
        deg = deg[:len(ref)]

    if pesq_status:
        import pysepm
        pesq_base = pysepm.pesq(ref, deg, rate)[1]
        csv_lines.append(['PESQ', f'{pesq_base:.3f}'])

    if stoi_status:
        from pystoi import stoi
        stoi_base = stoi(ref, deg, rate, extended=False)
        csv_lines.append(['STOI', f'{stoi_base:.3f}'])

    if sdr_status:
        import mir_eval
        ref_rsp = ref.reshape(1, -1)
        deg_rsp = deg.reshape(1, -1)
        mir_eval.separation.validate(ref_rsp, deg_rsp)
        sdr_base, sir, sar, perm = mir_eval.separation.bss_eval_sources(ref_rsp, deg_rsp)
        csv_lines.append(['SDR', f'{sdr_base[0]:.3f}'])

    # with open('metrics.csv', "w", newline="") as f:
    #     writer = csv.writer(f, lineterminator='\n')
    #     writer.writerows(csv_lines)
    return pesq_base, stoi_base, sdr_base[0]


AudioEvaluate.eval_metrics = eval_metrics

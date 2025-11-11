# -*- coding: utf-8 -*-
import os
import copy
from os import PathLike
from typing import Optional

import yaml
from pathlib import Path
from kudio.util import red, gre

try:
    from dotenv import load_dotenv, find_dotenv

    ret = load_dotenv(find_dotenv(), override=True)
    if not ret:
        print(".env not found")
except Exception as e:
    # print(e)
    pass

__all__ = ['KudioConfig', 'KC']


class Dict(dict):

    def __init__(__self, *args, **kwargs):
        object.__setattr__(__self, '__parent', kwargs.pop('__parent', None))
        object.__setattr__(__self, '__key', kwargs.pop('__key', None))
        object.__setattr__(__self, '__frozen', False)
        for arg in args:
            if not arg:
                continue
            elif isinstance(arg, dict):
                for key, val in arg.items():
                    __self[key] = __self._hook(val)
            elif isinstance(arg, tuple) and (not isinstance(arg[0], tuple)):
                __self[arg[0]] = __self._hook(arg[1])
            else:
                for key, val in iter(arg):
                    __self[key] = __self._hook(val)

        for key, val in kwargs.items():
            __self[key] = __self._hook(val)

    def __setattr__(self, name, value):
        if hasattr(self.__class__, name):
            raise AttributeError("'Dict' object attribute "
                                 "'{0}' is read-only".format(name))
        else:
            self[name] = value

    def __setitem__(self, name, value):
        isFrozen = (hasattr(self, '__frozen') and
                    object.__getattribute__(self, '__frozen'))
        if isFrozen and name not in super(Dict, self).keys():
            raise KeyError(name)
        super(Dict, self).__setitem__(name, value)
        try:
            p = object.__getattribute__(self, '__parent')
            key = object.__getattribute__(self, '__key')
        except AttributeError:
            p = None
            key = None
        if p is not None:
            p[key] = self
            object.__delattr__(self, '__parent')
            object.__delattr__(self, '__key')

    def __add__(self, other):
        if not self.keys():
            return other
        else:
            self_type = type(self).__name__
            other_type = type(other).__name__
            msg = "unsupported operand type(s) for +: '{}' and '{}'"
            raise TypeError(msg.format(self_type, other_type))

    @classmethod
    def _hook(cls, item):
        if isinstance(item, dict):
            return cls(item)
        elif isinstance(item, (list, tuple)):
            return type(item)(cls._hook(elem) for elem in item)
        return item

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __missing__(self, name):
        if object.__getattribute__(self, '__frozen'):
            raise KeyError(name)
        return self.__class__(__parent=self, __key=name)

    def __delattr__(self, name):
        del self[name]

    def to_dict(self):
        base = {}
        for key, value in self.items():
            if isinstance(value, type(self)):
                base[key] = value.to_dict()
            elif isinstance(value, (list, tuple)):
                base[key] = type(value)(
                    item.to_dict() if isinstance(item, type(self)) else
                    item for item in value)
            else:
                base[key] = value
        return base

    def copy(self):
        return copy.copy(self)

    def deepcopy(self):
        return copy.deepcopy(self)

    def __deepcopy__(self, memo):
        other = self.__class__()
        memo[id(self)] = other
        for key, value in self.items():
            other[copy.deepcopy(key, memo)] = copy.deepcopy(value, memo)
        return other

    def update(self, *args, **kwargs):
        other = {}
        if args:
            if len(args) > 1:
                raise TypeError()
            other.update(args[0])
        other.update(kwargs)
        for k, v in other.items():
            if ((k not in self) or
                    (not isinstance(self[k], dict)) or
                    (not isinstance(v, dict))):
                self[k] = v
            else:
                self[k].update(v)

    def __getnewargs__(self):
        return tuple(self.items())

    def __getstate__(self):
        return self

    def __setstate__(self, state):
        self.update(state)

    def __or__(self, other):
        if not isinstance(other, (Dict, dict)):
            return NotImplemented
        new = Dict(self)
        new.update(other)
        return new

    def __ror__(self, other):
        if not isinstance(other, (Dict, dict)):
            return NotImplemented
        new = Dict(other)
        new.update(self)
        return new

    def __ior__(self, other):
        self.update(other)
        return self

    def setdefault(self, key, default=None):
        if key in self:
            return self[key]
        else:
            self[key] = default
            return default

    def freeze(self, shouldFreeze=True):
        object.__setattr__(self, '__frozen', shouldFreeze)
        for key, val in self.items():
            if isinstance(val, Dict):
                val.freeze(shouldFreeze)

    def unfreeze(self):
        self.freeze(False)


class KudioConfig(Dict):

    def write_config(self, file: str = 'cfg.yaml', exist_ok: bool = False) -> bool:
        def __write():
            with open(str(file), 'w') as f:
                yaml.dump(self.to_dict(), f)
            print(f'[kd._config] Config is written to {file}')

        return (not Path(file).exists() or exist_ok) and (__write() or True)

    @classmethod
    def load_config(cls, cfg_dir: str = '', type='default') -> Optional['KudioConfig']:
        def __load(f_: Path):
            print(f"[kd._config] Load → {f_.absolute()}")
            with open(str(f_.absolute()), encoding="utf-8") as f:
                c_ = yaml.load(f, Loader=yaml.UnsafeLoader)
            return c_

        _file = Path(cfg_dir)
        if _file.is_file():
            return cls(__load(_file))
        elif _file.is_dir():
            f = list(_file.rglob("cfg.yaml"))
            if len(f) == 1:
                return cls(__load(f[-1]))
            else:
                print(f"[kd._config] (f.zo.or.multi.f)")
                return cls(**cls.__default_config(type_=type))

    @staticmethod
    def __default_config(type_='default'):
        print("[kd._config] def cfg")
        cfg_ = {
            "config": {'cfg.yaml'},
            "connections": {
                "base": {
                    'engine': 'tortoise.backends.mysql',
                    "credentials": {
                        'host': os.getenv('BASE_HOST', '127.0.0.1'),
                        'user': os.getenv('BASE_USER', 'root'),
                        'password': os.getenv('BASE_PASSWORD', '123456'),
                        'port': int(os.getenv('BASE_PORT', 3306)),
                        'database': os.getenv('BASE_DB', 'base'),
                    }
                },
            },
            "apps": {
                "base": {"models": ["models.base"], "default_connection": "base"},
                # "db2": {"models": ["models.db2"], "default_connection": "db2"},
                # "db3": {"models": ["models.db3"], "default_connection": "db3"}
            },
            'use_tz': False,
            'timezone': 'Asia/Taipei',

            'waveform': {
                'type': '.wav',
                'default_rate': 16000,
                'common_rate': [192000, 96000, 88200, 64000, 48000, 44100,
                                32000, 22050, 16000, 11025, 8000, 6000],
                'resample_rate': 16000,
                'channels': 'mono',
                'format': '16bit'},
            'device': {
                'pool_max': 200, 'cpu_cores': 12},
            'train': {
                'overwrite': True,
                'clean': 'data/train/clean'},
            'test': {
                'noisy': 'data/test/noisy'},
            'syn': {
                'overwrite': False,
                'noise': 'data/train/noise',
                'snr_range': [-5, 0, 5],
                'method': 'regular',
                'bkg_noise': 'data/backgroundnoise',
                'snr_bkg': [5]},
            'f_mfe': {
                'n_mels': 40,
                'bank': 1,
                'f0': 0,
                'f1': 48000},
            'denoise': {
                'overwrite': True,
                'train': True,
                'eval': False,
                'method': ['ddae', 'lstm', 'acap']},
            'model': {
                'path': 'models',
                'dnn_size': [512, 512, 512],
                'NOEFE_ENH': [150, 200],
                'DNN_ENH': 10,
                'LSTM_ENH': 10,
                'ACAPELLA_ENH': 10,
                'DNN_CLA': 200,
                'CNN_CLA': 100,
                'sVGG_CLA': 150,
                'LSTM_CLA': 150},
            'base': {
                'job_name': 'kudio',
                'train': True,
                'test': True,
                'overwrite': True,
                'feature': ['mfcc', 'logspec'],
                'classify': ['DNN', 'CNN', 'sVGG', 'LSTM'],
                'desired_samples': 32000,
                'advanced': False,
                'wanted_score': 93},
            'default': {
                'runs_path': 'runs',
                'denoise': ['none', 'trad', 'ddae', 'lstm', 'acap', 'wavelet', 'tradwavelet', 'noefe'],
                'feature': ['mfcc', 'logspec'],
                'classify': ['DNN', 'CNN', 'sVGG', 'LSTM', 'CNN1', 'CNN2']}
        }

        wj_cfg = {
            'apps': {'base': {'default_connection': 'base', 'models': ['models.base']}},
            'config': {'cfg.yaml'},
            'connections': {'base': {
                'credentials': {'database': 'base', 'host': '127.0.0.1', 'password': '123456', 'port': 3306,
                                'user': 'root'}, 'engine': 'tortoise.backends.mysql'}},
            'default': {'classify': ['DNN', 'CNN', 'sVGG', 'LSTM', 'CNN1', 'CNN2'],
                        'denoise': ['none', 'trad', 'ddae', 'lstm', 'acap', 'wavelet', 'tradwavelet', 'noefe'],
                        'feature': ['mfcc', 'logspec'], 'runs_path': 'runs'},
            'denoise': {'eval': False, 'method': ['ddae', 'lstm', 'acap'], 'overwrite': True, 'train': True},
            'device': {'cpu_cores': 12, 'pool_max': 200},
            'f_mfe': {'bank': 1, 'f0': 0, 'f1': 48000, 'n_mels': 40},
            'base': {'advanced': False, 'classify': ['sVGG'], 'desired_samples': 32000, 'feature': ['mfcc'],
                     'job_name': 'KudioClassify', 'overwrite': True, 'test': True, 'train': True, 'wanted_score': 93},
            'model': {'ACAPELLA_ENH': 10, 'CNN_CLA': 100, 'DNN_CLA': 200, 'DNN_ENH': 10, 'LSTM_CLA': 150,
                      'LSTM_ENH': 10,
                      'NOEFE_ENH': [150, 200], 'dnn_size': [512, 512, 512], 'path': 'models', 'sVGG_CLA': 150},
            'syn': {'bkg_noise': 'data/backgroundnoise', 'method': 'regular', 'noise': 'data/train/noise',
                    'overwrite': False, 'snr_bkg': [5], 'snr_range': [-5, 0, 5]},
            'test': {'noisy': 'data/test/noisy'},
            'timezone': 'Asia/Taipei',
            'train': {'clean': 'path/to/data', 'overwrite': True},
            'use_tz': False,
            'waveform': {'channels': 'mono',
                         'common_rate': [192000, 96000, 88200, 64000, 48000, 44100, 32000, 22050,
                                         16000, 11025, 8000, 6000], 'default_rate': 16000, 'format': '16bit',
                         'resample_rate': 16000, 'type': '.wav'}
        }

        return wj_cfg if 'wj' in type_ else cfg_

    def show(self, key: str = None) -> None:
        if key is None:
            for key, value in self.items():
                gre(f"[kd._config] {key}: {value}")
        else:
            if key in self:
                gre(f"[kd._config] {key}: {self.get(key)}")
            else:
                red(f"[kd._config] Unknown key: {key}")


KC = KudioConfig

# if __name__ == '__main__':
#     cfg_ = KC.load_config()
#     rt = cfg_.write_config(exist_ok=True)
#     cfg_.show('global')

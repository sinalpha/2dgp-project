"""효과음 모음. 파일이 없거나 로드에 실패해도 게임은 조용히 계속된다."""
import os
from pico2d import load_wav, Mix_PlayChannel, Mix_Playing

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sound')
_cache = {}


def _load(name, volume):
    try:
        w = load_wav(os.path.join(DIR, name + '.ogg'))
        w.set_volume(volume)
        return w
    except Exception as ex:          # 파일 없음 / 디코더 없음
        print('sound load failed:', name, ex)
        return None


def play(name):
    """name: shoot / fail / metal / glass / matte. 재생 채널 번호(실패 시 -1)를 반환"""
    if name not in _cache:
        _cache[name] = _load(name, 80)
    if not _cache[name]:
        return -1
    return Mix_PlayChannel(-1, _cache[name].wav, 0)


def is_playing(channel):
    return channel >= 0 and Mix_Playing(channel) != 0

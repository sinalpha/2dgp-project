"""공용 그리기 도구: 색상, 굵은 선, 한글 폰트"""
import math
import os
from pico2d import *

AMBER = (255, 182, 39)
CYAN = (77, 208, 225)
BLOCK_COLOR = (255, 107, 107)
KIND_COLOR = {'metal': (170, 180, 196), 'glass': (77, 208, 225), 'matte': (124, 140, 248)}

_fonts = {}


def thick_line(x1, y1, x2, y2, width, color, alpha=255):
    length = math.hypot(x2 - x1, y2 - y1) or 1
    nx, ny = -(y2 - y1) / length, (x2 - x1) / length
    for i in range(width):
        o = i - (width - 1) / 2
        draw_line(x1 + nx * o, y1 + ny * o, x2 + nx * o, y2 + ny * o, color[0], color[1], color[2], alpha)


FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
PIXEL = 12            # Mona12 는 12px 도트 폰트: 12의 배수 크기에서 가장 또렷하다


def _font_path(bold):
    mona = os.path.join(FONT_DIR, 'Mona12-Bold.ttf' if bold else 'Mona12.ttf')
    for p in (mona, 'C:/Windows/Fonts/malgun.ttf', 'C:/Windows/Fonts/gulim.ttc'):
        if os.path.exists(p):
            return p
    raise IOError('한글 폰트를 찾을 수 없습니다')


def font(size):
    """캔버스를 연 뒤에 호출해야 한다. 같은 크기는 한 번만 로딩.
    도트 폰트라 크기를 12의 배수로 맞춘다 (20 이하 -> 12, 30 -> 24, 48, 60 ...).
    32 이상의 큰 글자는 굵은 글꼴을 쓴다."""
    snapped = max(PIXEL, int(size / PIXEL + 0.35) * PIXEL)
    if size not in _fonts:
        _fonts[size] = load_font(_font_path(size >= 30), snapped)
    return _fonts[size]

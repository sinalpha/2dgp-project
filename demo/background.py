import raylogic as rl
from pico2d import *
from gfx import BLOCK_COLOR

NO_PLACE_R = 40      # 광원/목표 주변 배치 금지 반경
NO_PLACE_TOP = 70    # 상단 표시줄 배치 금지 높이


def blocked(stage, x, y):
    """배치 금지 구역: 광원/목표 주변, 상단 표시줄"""
    return (any((x - cx) ** 2 + (y - cy) ** 2 < NO_PLACE_R ** 2 for cx, cy in _spots(stage))
            or y > rl.H - NO_PLACE_TOP)


def _spots(stage):
    """광원과 모든 목적지의 위치"""
    return [(sx, sy) for sx, sy, _ in rl.get_sources(stage)] + list(rl.get_targets(stage))


class Background:
    """배경 격자와 배치 금지 구역 표시"""

    def __init__(self, stage):
        self.stage = stage

    def update(self):
        pass

    def draw(self):
        W, H = rl.W, rl.H
        draw_rectangle(0, 0, W - 1, H - 1, 14, 20, 36, 255, True)
        for gx in range(0, W, 40):
            draw_line(gx, 0, gx, H, 255, 255, 255, 10)
        for gy in range(0, H, 40):
            draw_line(0, gy, W, gy, 255, 255, 255, 10)

        draw_rectangle(0, H - NO_PLACE_TOP, W - 1, H - 1, *BLOCK_COLOR, 38, True)
        draw_line(0, H - NO_PLACE_TOP, W, H - NO_PLACE_TOP, *BLOCK_COLOR, 110)
        for cx, cy in _spots(self.stage):
            draw_circle(cx, cy, NO_PLACE_R, *BLOCK_COLOR, 38, True)
            draw_circle(cx, cy, NO_PLACE_R, *BLOCK_COLOR, 110)

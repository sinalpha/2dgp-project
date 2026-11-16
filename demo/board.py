import raylogic as rl
from pico2d import *
from gfx import AMBER, CYAN, thick_line
from piece import Piece


class Board:
    """스테이지 고정물: 벽, 광원, 목표, (스테이지에 미리 놓인 오브젝트)"""

    def __init__(self, stage):
        self.stage = stage
        self.reached = set()  # 빛이 도달한 목적지 번호 (발사가 끝난 뒤에 채워진다)
        self.fixed = [Piece(*o) for o in stage.get('fixed', [])]

    def update(self):
        pass

    def draw(self):
        st = self.stage
        for w in st['walls']:
            thick_line(w[0], w[1], w[2], w[3], 8, (58, 69, 104))
        for p in self.fixed:
            p.draw()

        for sx, sy, _ in rl.get_sources(st):
            draw_circle(sx, sy, 12, *AMBER, 255, True)
            draw_circle(sx, sy, 18, *AMBER, 90)

        for i, (tx, ty) in enumerate(rl.get_targets(st)):
            tc = AMBER if i in self.reached else CYAN      # 빛이 닿은 목적지는 호박색
            draw_circle(tx, ty, rl.TARGET_R, *tc, 255)
            draw_circle(tx, ty, rl.TARGET_R - 1, *tc, 255)
            draw_circle(tx, ty, 8, *tc, 255, True)

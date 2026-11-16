import math
import game_framework
import sound
from pico2d import *
from gfx import AMBER, BLOCK_COLOR, thick_line, font

BEAM_SPEED_PPS = 800.0   # 빛이 나아가는 속도 (pixel / sec)
STEP_LEN = 40            # 그라데이션 토막 길이 (pixel)
STEPS_MAX = 12           # 줄기 하나를 나누는 최대 토막 수 (그리기 비용 제한)
MIN_ALPHA = 0.18         # 에너지가 거의 없어도 빛이 보이도록 하는 최소 알파 비율


def alpha_scale(energy):
    """에너지(0~100) -> 알파 비율. 에너지가 클수록 진하고 작을수록 투명해진다"""
    return max(MIN_ALPHA, min(1.0, energy / 100.0))


class Beam:
    """발사된 빛. 프레임 시간(frame_time)에 비례해 앞으로 나아간다."""

    def __init__(self, result):
        self.result = result
        self.dist = 0.0
        self.hit_idx = 0           # 다음에 소리 낼 재질 충돌
        self.fail_played = False

    @property
    def done(self):
        return self.dist >= self.result['total']

    @property
    def energy(self):
        """지금 빛 끝(앞쪽)의 에너지. 재질을 지날 때마다 줄어든다 (갈라지면 가장 센 줄기)"""
        if self.done:
            return self.result['best'] if self.result['success'] else 0
        cur = 0
        for x1, y1, x2, y2, e, d0, e_end in self.result['paths']:
            length = math.hypot(x2 - x1, y2 - y1)
            if d0 <= self.dist <= d0 + length:
                u = (self.dist - d0) / length if length > 1e-6 else 0.0
                cur = max(cur, e + (e_end - e) * u)      # 줄기를 따라 서서히 줄어든다
        return cur

    @property
    def success(self):
        return self.done and self.result['success']

    def update(self):
        if not self.done:
            self.dist += BEAM_SPEED_PPS * game_framework.frame_time
        # 빛이 재질에 닿은 순간 해당 재질 소리 (같은 프레임의 같은 재질은 한 번만)
        hits, played = self.result['hits'], set()
        while self.hit_idx < len(hits) and hits[self.hit_idx][0] <= self.dist:
            kind = hits[self.hit_idx][1]
            if kind not in played:
                sound.play(kind)
                played.add(kind)
            self.hit_idx += 1
        if self.done and not self.result['success'] and not self.fail_played:
            self.fail_played = True
            sound.play('fail')

    def draw(self):
        D = self.dist
        for x1, y1, x2, y2, e, d0, e_end in self.result['paths']:
            length = math.hypot(x2 - x1, y2 - y1)
            if D <= d0 or length < 1e-6:
                continue
            f = min(1.0, (D - d0) / length)
            # 줄기를 토막으로 나눠, 토막마다 에너지(= 알파값)를 줄기 위치에 맞게 보간한다
            n = max(1, min(STEPS_MAX, int(length * f / STEP_LEN) + 1))
            for i in range(n):
                u0, u1 = f * i / n, f * (i + 1) / n
                k = alpha_scale(e + (e_end - e) * (u0 + u1) / 2)      # 0..1
                ax, ay = x1 + (x2 - x1) * u0, y1 + (y2 - y1) * u0
                bx, by = x1 + (x2 - x1) * u1, y1 + (y2 - y1) * u1
                thick_line(ax, ay, bx, by, 9, AMBER, int(28 * k))
                thick_line(ax, ay, bx, by, 5, AMBER, int(70 * k))
                thick_line(ax, ay, bx, by, 2, (255, 240, 200), int(255 * k))
        if self.done:
            for x, y, why in self.result['ends']:
                if why == 'dead':
                    draw_circle(x, y, 7, *BLOCK_COLOR, 255, True)
                    font(14).draw(x + 10, y + 12, '0', BLOCK_COLOR)
                elif why == 'target':
                    draw_circle(x, y, 5, 255, 255, 255, 255, True)

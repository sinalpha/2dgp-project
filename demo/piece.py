import raylogic as rl
from pico2d import *
from gfx import KIND_COLOR, thick_line, font


class Piece:
    """플레이어가 배치하는 오브젝트 (금속 판 / 유리 프리즘 / 매트 블록)"""

    def __init__(self, kind, x, y, angle, ghost=False):
        self.kind, self.x, self.y, self.angle = kind, x, y, angle
        self.ghost = ghost    # True 면 배치 미리보기(반투명)

    def as_tuple(self):
        return (self.kind, self.x, self.y, self.angle)

    def hit(self, mx, my, radius):
        return (self.x - mx) ** 2 + (self.y - my) ** 2 < radius ** 2

    def update(self):
        pass

    def draw(self):
        a, b = rl.seg_points(self.as_tuple())
        col = KIND_COLOR[self.kind]
        alpha = 110 if self.ghost else 255
        if self.kind == 'metal':
            thick_line(a[0], a[1], b[0], b[1], 6, col, alpha)
        elif self.kind == 'glass':
            thick_line(a[0], a[1], b[0], b[1], 10, col, 90 if self.ghost else 150)
            thick_line(a[0], a[1], b[0], b[1], 2, (220, 250, 255), alpha)
        else:
            thick_line(a[0], a[1], b[0], b[1], 12, col, alpha)
            for t in (0.25, 0.5, 0.75):
                px, py = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                draw_circle(px, py, 2, 14, 20, 36, alpha, True)
        font(14).draw(self.x + 8, self.y + 18, '-%d' % rl.MATERIALS[self.kind]['cost'], (200, 208, 224))

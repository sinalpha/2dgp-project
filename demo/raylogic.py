"""RAY TRACER - 빛 경로 계산 (화면과 무관한 순수 로직)"""
import math

W, H = 1000, 640
START_ENERGY = 100
OBJ_LEN = 90          # 플레이어 오브젝트 길이
TARGET_R = 22

# 재질별 에너지 감소 / 특성
MATERIALS = {
    'metal': {'name': '금속 판', 'cost': 5},                  # 정반사
    'glass': {'name': '유리 프리즘', 'cost': 10, 'bend': 25},  # 고정 각도로 꺾임
    'matte': {'name': '매트 블록', 'cost': 20, 'spread': 60},  # 사방 3갈래
}

MAX_RAYS = 120
MAX_DEPTH = 14


def seg_points(obj):
    """obj = (kind, x, y, angle_deg) -> 선분 끝점 두 개"""
    kind, x, y, ang = obj
    a = math.radians(ang)
    dx, dy = math.cos(a) * OBJ_LEN / 2, math.sin(a) * OBJ_LEN / 2
    return (x - dx, y - dy), (x + dx, y + dy)


def _hit_segment(p, d, a, b):
    """반직선 p + t*d 와 선분 ab 의 교차. t 반환(없으면 None)"""
    ex, ey = b[0] - a[0], b[1] - a[1]
    den = d[0] * ey - d[1] * ex
    if abs(den) < 1e-9:
        return None
    wx, wy = a[0] - p[0], a[1] - p[1]
    t = (wx * ey - wy * ex) / den
    u = (wx * d[1] - wy * d[0]) / den
    if t > 1e-4 and -1e-9 <= u <= 1 + 1e-9:
        return t
    return None


def _hit_circle(p, d, c, r):
    fx, fy = p[0] - c[0], p[1] - c[1]
    b = fx * d[0] + fy * d[1]
    cc = fx * fx + fy * fy - r * r
    disc = b * b - cc
    if disc < 0:
        return None
    t = -b - math.sqrt(disc)
    if t > 1e-4:
        return t
    return None


def _hit_bounds(p, d):
    best = 1e9
    if d[0] > 1e-9:
        best = min(best, (W - p[0]) / d[0])
    elif d[0] < -1e-9:
        best = min(best, (0 - p[0]) / d[0])
    if d[1] > 1e-9:
        best = min(best, (H - p[1]) / d[1])
    elif d[1] < -1e-9:
        best = min(best, (0 - p[1]) / d[1])
    return best


def _rot(d, deg):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return (d[0] * c - d[1] * s, d[0] * s + d[1] * c)


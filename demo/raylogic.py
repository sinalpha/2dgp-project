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


def get_targets(stage):
    """목적지 목록. 스테이지는 'target'(1개) 또는 'targets'(여러 개)로 지정한다"""
    return stage.get('targets') or [stage['target']]


def get_sources(stage):
    """광원 목록 [(x, y, angle)]. 'source'+'source_angle'(1개) 또는 'sources'(여러 개)"""
    return stage.get('sources') or [(stage['source'][0], stage['source'][1], stage['source_angle'])]


def trace(stage, placed):
    """
    반환: dict
      paths  : [(x1, y1, x2, y2, energy, dist0, energy_end)]  그려야 할 빛줄기
               (energy -> energy_end 로 줄기를 따라 서서히 줄어든다)
      ends   : [(x, y, reason)]                   빛이 끝난 지점 (dead/wall/out/target)
      hits   : [(경로상 거리, 재질)]  빛이 재질에 닿는 지점 (효과음용, 거리순)
      success: 모든 목적지에 도달했는가
      reached: 도달한 목적지 번호 목록
      best   : 성공 시 가장 약하게 도착한 목적지의 에너지 (실패 시 도달한 것 중 최대)
      total  : 가장 긴 경로 길이
    """
    solids = []  # (kind, a, b)
    for w in stage['walls']:
        solids.append(('wall', (w[0], w[1]), (w[2], w[3])))
    for o in stage.get('fixed', []) + placed:
        a, b = seg_points(o)
        solids.append((o[0], a, b))

    targets = get_targets(stage)
    rays = []
    for sx, sy, sa in get_sources(stage):
        a = math.radians(sa)
        rays.append(((sx, sy), (math.cos(a), math.sin(a)), START_ENERGY, 0, 0.0))
    paths, ends, hits = [], [], []
    tbest = {}                     # 목적지 번호 -> 도착한 최대 에너지
    total, count = 0.0, 0

    while rays and count < MAX_RAYS:
        p, d, e, depth, dist0 = rays.pop()
        count += 1

        t_hit, hit = _hit_bounds(p, d), ('out', None, None)
        for kind, a, b in solids:
            t = _hit_segment(p, d, a, b)
            if t is not None and t < t_hit:
                t_hit, hit = t, (kind, a, b)
        for ti, tpos in enumerate(targets):
            tt = _hit_circle(p, d, tpos, TARGET_R)
            if tt is not None and tt < t_hit:
                t_hit, hit = tt, ('target', ti, None)

        q = (p[0] + d[0] * t_hit, p[1] + d[1] * t_hit)
        kind, a, b = hit
        # 줄기 끝에서의 에너지: 재질에 닿으면 그 재질의 감소량만큼 줄어든 값 (그라데이션용)
        e_end = e if kind in ('out', 'wall', 'target') else max(0, e - MATERIALS[kind]['cost'])
        paths.append((p[0], p[1], q[0], q[1], e, dist0, e_end))
        total = max(total, dist0 + t_hit)

        if kind in ('out', 'wall'):
            ends.append((q[0], q[1], kind))
            continue
        if kind == 'target':
            tbest[a] = max(tbest.get(a, 0), e)      # a = 목적지 번호
            ends.append((q[0], q[1], 'target'))
            continue

        m = MATERIALS[kind]
        hits.append((dist0 + t_hit, kind))
        e -= m['cost']
        if e <= 0 or depth >= MAX_DEPTH:
            ends.append((q[0], q[1], 'dead'))
            continue

        ex, ey = b[0] - a[0], b[1] - a[1]
        el = math.hypot(ex, ey)
        s = (ex / el, ey / el)
        dist1 = dist0 + t_hit
        if kind == 'metal':
            n = (-s[1], s[0])
            dn = d[0] * n[0] + d[1] * n[1]
            nd = (d[0] - 2 * dn * n[0], d[1] - 2 * dn * n[1])
            rays.append((q, nd, e, depth + 1, dist1))
        elif kind == 'glass':
            sign = 1 if (d[0] * s[1] - d[1] * s[0]) > 0 else -1
            rays.append((q, _rot(d, sign * m['bend']), e, depth + 1, dist1))
        elif kind == 'matte':
            n = (-s[1], s[0])
            if n[0] * d[0] + n[1] * d[1] > 0:
                n = (-n[0], -n[1])
            share = e / 3
            for off in (-m['spread'], 0, m['spread']):
                rays.append((q, _rot(n, off), share, depth + 1, dist1))

    hits.sort()
    success = len(tbest) == len(targets)
    best = min(tbest.values()) if success else max(tbest.values(), default=0)
    return {'paths': paths, 'ends': ends, 'hits': hits, 'success': success,
            'reached': sorted(tbest), 'best': best, 'total': total}


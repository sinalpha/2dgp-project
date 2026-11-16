"""상단 표시줄 / 에너지 게이지 / 결과 배너. play_mode 의 상태를 읽어서 그린다."""
import raylogic as rl
from pico2d import *
from gfx import AMBER, BLOCK_COLOR, CYAN, KIND_COLOR, font

KIND_KEYS = [(SDLK_1, 'metal'), (SDLK_2, 'glass'), (SDLK_3, 'matte')]
SKIP_BTN = (rl.W - 134, 50, rl.W - 24, 82)    # x1, y1, x2, y2 (스테이지 스킵 버튼)


def on_skip_button(x, y):
    return SKIP_BTN[0] <= x <= SKIP_BTN[2] and SKIP_BTN[1] <= y <= SKIP_BTN[3]


def banner(title, sub, col):
    W = rl.W
    draw_rectangle(W // 2 - 260, 38, W // 2 + 260, 138, 14, 20, 36, 230, True)
    draw_rectangle(W // 2 - 260, 38, W // 2 + 260, 138, col[0], col[1], col[2], 255)
    font(30).draw(W // 2 - 220, 102, title, col)
    font(14).draw(W // 2 - 220, 62, sub, (200, 208, 224))


def draw(g):
    """g : play_mode 모듈"""
    H, W = rl.H, rl.W
    f18, f14 = font(18), font(14)
    st = g.stage()
    beam = g.beam

    f18.draw(24, H - 28, st['name'], (255, 255, 255))
    for i in range(len(rl.STAGES)):
        draw_circle(30 + i * 16, H - 62, 4, *(AMBER if i == g.stage_idx else (58, 69, 104)), 255, True)
    f14.draw(24, H - 52, st['hint'], (138, 147, 168))

    x = 340
    for i, (key, kind) in enumerate(KIND_KEYS):
        if kind not in st['inventory']:
            continue
        m = rl.MATERIALS[kind]
        n = g.remaining(kind)
        col = KIND_COLOR[kind]
        if kind == g.sel:
            draw_rectangle(x - 8, H - 62, x + 168, H - 6, 255, 255, 255, 40, True)
        draw_circle(x + 8, H - 24, 7, col[0], col[1], col[2], 255, True)
        f18.draw(x + 24, H - 24, '%s ×%d' % (m['name'], n), (255, 255, 255) if n else (110, 118, 140))
        f14.draw(x + 24, H - 46, '[%d]  에너지 -%d' % (i + 1, m['cost']), (138, 147, 168))
        x += 190

    # 에너지 게이지
    energy = beam.energy if beam else rl.START_ENERGY      # 발사 중에는 실시간으로 줄어든다
    gx, gw = W - 210, 180
    draw_rectangle(gx, H - 30, gx + gw, H - 20, 42, 51, 80, 255, True)
    fw = int(gw * energy / rl.START_ENERGY)
    if fw > 0:
        draw_rectangle(gx, H - 30, gx + fw, H - 20, *AMBER, 255, True)
    f14.draw(gx, H - 46, 'ENERGY %d' % energy, CYAN)
    f14.draw(gx + 100, H - 46, '시도 %d회' % g.attempts, (138, 147, 168))

    f14.draw(24, 18, '클릭 배치/집기 · R/휠 회전 · 우클릭 제거 · Space 발사 · Z 되돌리기 · Y 다시하기 · X 재시작 · 1/2/3 선택 · P 일시정지',
             (110, 118, 140))

    x1, y1, x2, y2 = SKIP_BTN
    hot = on_skip_button(*g.mouse)
    draw_rectangle(x1, y1, x2, y2, 255, 255, 255, 60 if hot else 25, True)
    draw_rectangle(x1, y1, x2, y2, *AMBER, 255)
    f14.draw(x1 + 14, y1 + 16, '스킵 [K]', AMBER)

    if beam and beam.done:
        if beam.result['success']:
            last = g.stage_idx + 1 >= len(rl.STAGES)
            banner('성공!  남은 에너지 %d' % beam.result['best'],
                   '시도 %d회  ·  N: %s' % (g.attempts, '결과 보기' if last else '다음 스테이지'), AMBER)
        else:
            dead = any(w == 'dead' for _, _, w in beam.result['ends'])
            n, m = len(beam.result['reached']), len(rl.get_targets(st))
            if m > 1:
                title = '실패 - 목적지 %d/%d 도달' % (n, m)
            else:
                title = '실패 - 에너지 소진' if dead else '실패 - 목표에 닿지 못함'
            banner(title, '배치를 고쳐 다시 Space', BLOCK_COLOR)

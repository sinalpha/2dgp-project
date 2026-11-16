"""기록 화면: 타이틀에서 T 로 열고, 지난 플레이의 스테이지별 시도 횟수를 보여준다"""
from pico2d import *

import game_framework
import raylogic as rl
import records
from gfx import AMBER, thick_line, font

data = {}


def init():
    global data
    data = records.load()


def finish():
    pass


def pause():
    pass


def resume():
    pass


def handle_events():
    for e in get_events():
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN or e.type == SDL_MOUSEBUTTONDOWN:
            import title_mode
            game_framework.change_mode(title_mode)


def update():
    pass


def draw():
    clear_canvas()
    draw_rectangle(0, 0, rl.W - 1, rl.H - 1, 14, 20, 36, 255, True)
    font(48).draw(90, 570, '시도 기록', AMBER)
    thick_line(90, 535, 560, 535, 2, AMBER, 120)

    last, best = data.get('last'), data.get('best')
    if not last:
        font(18).draw(100, 440, '아직 기록이 없습니다. 모든 스테이지를 클리어해 보세요.', (202, 220, 252))
    else:
        font(14).draw(440, 505, '지난 플레이', (138, 147, 168))
        font(14).draw(560, 505, '최고 기록', (138, 147, 168))
        y = 475
        step = min(40, 340 // len(rl.STAGES))     # 스테이지가 많아도 화면에 들어오게
        for i, s in enumerate(rl.STAGES):
            font(18).draw(100, y, s['name'], (202, 220, 252))
            font(18).draw(440, y, '%d회' % last[i] if i < len(last) else '-', (255, 255, 255))
            font(18).draw(560, y, '%d회' % best[i] if best and i < len(best) else '-', AMBER)
            y -= step
        thick_line(90, y + 15, 680, y + 15, 1, (138, 147, 168), 120)
        font(24).draw(100, y - 25, '총 시도', (255, 255, 255))
        font(24).draw(440, y - 25, '%d회' % sum(last), (255, 255, 255))
        font(24).draw(560, y - 25, '%d회' % data.get('best_total', sum(last)), AMBER)
    font(14).draw(100, 50, '아무 키나 눌러 타이틀로', (138, 147, 168))
    update_canvas()

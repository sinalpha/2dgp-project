"""모든 스테이지를 클리어한 뒤의 결과 화면 (스테이지별 시도 횟수)"""
from pico2d import *

import game_framework
import play_mode
import raylogic as rl
import records
from gfx import AMBER, thick_line, font

total = 0
rows = []


def init():
    global total, rows
    total = play_mode.total_attempts
    rows = [(s['name'], n) for s, n in zip(rl.STAGES, play_mode.stage_attempts)]
    records.save(play_mode.stage_attempts)


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
        elif e.type == SDL_KEYDOWN:
            if e.key == SDLK_ESCAPE:
                game_framework.quit()
            elif e.key in (SDLK_RETURN, SDLK_SPACE, SDLK_n):
                import title_mode
                game_framework.change_mode(title_mode)


def update():
    pass


def draw():
    clear_canvas()
    draw_rectangle(0, 0, rl.W - 1, rl.H - 1, 14, 20, 36, 255, True)
    font(48).draw(90, 580, '모든 스테이지 클리어!', AMBER)
    thick_line(90, 545, 560, 545, 2, AMBER, 120)

    best = min((n for _, n in rows), default=0)
    y = 515
    step = min(44, 360 // max(1, len(rows)))     # 스테이지가 많아도 화면에 들어오게
    for name, n in rows:
        font(18).draw(100, y, name, (202, 220, 252))
        font(18).draw(440, y, '%d회' % n, AMBER if n == best else (255, 255, 255))
        y -= step

    thick_line(90, y + 8, 560, y + 8, 1, (138, 147, 168), 120)
    font(24).draw(100, y - 28, '총 시도', (255, 255, 255))
    font(24).draw(440, y - 28, '%d회' % total, AMBER)
    font(14).draw(100, 70, 'Enter: 타이틀로   ESC: 종료', (138, 147, 168))
    update_canvas()

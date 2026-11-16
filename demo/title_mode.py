"""타이틀 화면"""
from pico2d import *

import game_framework
import raylogic as rl
import records
from gfx import AMBER, thick_line, font


def init():
    pass


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
        elif e.type == SDL_KEYDOWN and e.key == SDLK_ESCAPE:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN and e.key == SDLK_t:
            import records_mode
            game_framework.change_mode(records_mode)
        elif e.type in (SDL_KEYDOWN, SDL_MOUSEBUTTONDOWN):
            import play_mode
            game_framework.change_mode(play_mode)


def update():
    pass


def draw():
    clear_canvas()
    draw_rectangle(0, 0, rl.W - 1, rl.H - 1, 14, 20, 36, 255, True)
    thick_line(0, 330, 560, 330, 9, AMBER, 28)
    thick_line(0, 330, 560, 330, 2, (255, 240, 200), 255)
    thick_line(540, 310, 580, 350, 5, (170, 180, 196))
    thick_line(560, 330, 560, 520, 9, AMBER, 28)
    thick_line(560, 330, 560, 520, 2, (255, 240, 200), 255)
    draw_circle(560, 540, 22, 77, 208, 225)
    draw_circle(560, 540, 8, 77, 208, 225, 255, True)
    font(60).draw(90, 440, 'RAY TRACER', (255, 255, 255))
    font(18).draw(94, 392, '빛이 꺼지기 전에 목표에 도달시켜라', (202, 220, 252))
    font(14).draw(94, 250, '아무 키나 눌러 시작', AMBER)
    best = records.load().get('best_total')
    font(14).draw(94, 280, 'T: 시도 기록 보기' + ('   (최고 기록 %d회)' % best if best else ''), (202, 220, 252))
    font(14).draw(94, 220, '배치 → 발사 → 실패하면 고쳐서 다시', (138, 147, 168))
    font(14).draw(94, 100, '이경한 · 2023180027', (138, 147, 168))
    update_canvas()

"""일시정지: play_mode 위에 push_mode 로 쌓이는 모드 (P 또는 ESC 로 복귀)"""
from pico2d import *

import game_framework
import play_mode
import raylogic as rl
from gfx import AMBER, font


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
        elif e.type == SDL_KEYDOWN and e.key in (SDLK_p, SDLK_ESCAPE):
            game_framework.pop_mode()


def update():
    pass


def draw():
    clear_canvas()
    play_mode.game_world.render()          # 아래 모드의 화면을 그대로 두고
    draw_rectangle(0, 0, rl.W - 1, rl.H - 1, 14, 20, 36, 170, True)   # 어둡게 덮는다
    font(60).draw(rl.W // 2 - 130, rl.H // 2 + 20, 'PAUSE', AMBER)
    font(18).draw(rl.W // 2 - 110, rl.H // 2 - 30, 'P 또는 ESC: 계속하기', (200, 208, 224))
    update_canvas()

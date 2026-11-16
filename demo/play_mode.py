"""플레이 모드: 배치 -> 발사 -> 결과"""
import math
import os
import sys
from pico2d import *

import game_framework
import game_world
import hud
import raylogic as rl
import sound
from background import Background, blocked
from beam import Beam
from board import Board
from gfx import BLOCK_COLOR, thick_line
from piece import Piece

H = rl.H
SMOKE_DIR = os.environ.get('RT_SMOKE')   # 자동 검증용 (README 참고)
SMOKE_SOLUTIONS = [
    [('metal', 200, 120, 45)],
    [('metal', 250, 320, 45), ('metal', 250, 500, 45), ('metal', 880, 500, 135)],
    [('glass', 150, 100, 90), ('glass', 260, 151, 90), ('glass', 330, 234, 90), ('metal', 417, 560, 30)],
    [('matte', 490, 320, 90)],
    [('metal', 200, 100, 45), ('metal', 200, 500, 45), ('metal', 500, 500, 135), ('metal', 500, 100, 135)],
    [('glass', 200, 100, 90), ('glass', 330, 160, 90)],
    [('metal', 200, 320, 45), ('matte', 200, 540, 30), ('metal', 800, 540, 135)],
    [('matte', 500, 320, 90)],
    [('matte', 500, 320, 45)],
    [('metal', 250, 100, 45), ('matte', 250, 420, 0)],
    [('metal', 500, 150, 45), ('metal', 880, 490, 135)],
    [('matte', 400, 320, 45), ('matte', 420, 380, 90)],
    [('matte', 480, 320, 90), ('metal', 380, 493, 60), ('metal', 380, 147, 120)],
    [('glass', 200, 100, 90), ('glass', 330, 160, 90), ('glass', 800, 100, 90), ('glass', 670, 160, 90)],
    [('matte', 400, 200, 45), ('matte', 400, 440, 135)],
    [('metal', 200, 100, 45), ('glass', 200, 220, 0), ('glass', 260, 340, 0), ('metal', 500, 550, 165)],
]

stage_idx = 0
sel = 'metal'
angle = 45
mouse = (rl.W // 2, H // 2)
beam = None            # 발사된 빛 (없으면 None)
board = None
attempts = 0
total_attempts = 0
redo_stack = []        # Z 로 되돌린 오브젝트들 (Y 로 다시 놓는다)
shoot_ch = None        # 발사음 재생 채널 (None 이면 발사 준비 중 아님)
stage_attempts = []    # 스테이지별 누적 시도 횟수 (결과 화면용)
_smoke = {'step': 0, 't': 0.0}


# ---------------------------------------------------------------- 상태 도우미
def stage():
    return rl.STAGES[stage_idx]


def pieces():
    return game_world.objects(game_world.PIECES)


def remaining(kind):
    used = sum(1 for p in pieces() if p.kind == kind)
    return stage()['inventory'].get(kind, 0) - used


def load_stage(idx):
    global stage_idx, sel, beam, board, attempts, shoot_ch
    stage_idx = idx
    shoot_ch = None
    redo_stack.clear()
    game_world.clear()
    beam = None
    attempts = 0
    sel = next(iter(stage()['inventory']))
    board = Board(stage())
    game_world.add_object(Background(stage()), game_world.BACK)
    game_world.add_object(board, game_world.STAGE)


def edited():
    """배치가 바뀌면 이전 발사 결과는 무효 (발사 준비 중이면 취소)"""
    global beam, shoot_ch
    shoot_ch = None
    if beam:
        game_world.remove_object(beam)
        beam = None
    board.reached = set()


def fire():
    """발사음을 먼저 재생하고, 소리가 끝나면 launch() 로 실제 빛을 쏜다"""
    global shoot_ch
    if shoot_ch is not None:      # 이미 발사 준비 중
        return
    edited()
    shoot_ch = sound.play('shoot')


def launch():
    global beam, attempts, total_attempts
    result = rl.trace(stage(), [p.as_tuple() for p in pieces()])
    beam = Beam(result)
    game_world.add_object(beam, game_world.BEAM)
    attempts += 1
    total_attempts += 1
    stage_attempts[stage_idx] += 1


def next_stage():
    if stage_idx + 1 < len(rl.STAGES):
        load_stage(stage_idx + 1)
    else:
        import ending_mode
        game_framework.change_mode(ending_mode)


# ---------------------------------------------------------------- 입력
def place(x, y):
    global sel, angle
    # 놓인 오브젝트를 클릭하면 집어 올린다 (옮겨 놓기)
    for p in reversed(pieces()):
        if p.hit(x, y, 35):
            sel, angle = p.kind, p.angle
            game_world.remove_object(p)
            redo_stack.clear()
            edited()
            return
    if remaining(sel) <= 0 or blocked(stage(), x, y):
        return
    game_world.add_object(Piece(sel, round(x / 10) * 10, round(y / 10) * 10, angle), game_world.PIECES)
    redo_stack.clear()
    edited()


def remove_near(x, y):
    best, bd = None, 45
    for p in pieces():
        d = math.hypot(p.x - x, p.y - y)
        if d < bd:
            best, bd = p, d
    if best:
        game_world.remove_object(best)
        redo_stack.clear()
        edited()


def handle_events():
    global mouse, angle, sel
    for e in get_events():
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_MOUSEMOTION:
            mouse = (e.x, H - 1 - e.y)
        elif e.type == SDL_MOUSEWHEEL:
            angle = (angle + 15 * (1 if e.y > 0 else -1)) % 180
        elif e.type == SDL_MOUSEBUTTONDOWN:
            mouse = (e.x, H - 1 - e.y)
            if e.button == SDL_BUTTON_LEFT:
                if hud.on_skip_button(*mouse):
                    next_stage()
                else:
                    place(*mouse)
            elif e.button == SDL_BUTTON_RIGHT:
                remove_near(*mouse)
        elif e.type == SDL_KEYDOWN:
            k = e.key
            if k == SDLK_ESCAPE:
                game_framework.quit()
            elif k == SDLK_p:
                import pause_mode
                game_framework.push_mode(pause_mode)
            elif k == SDLK_k:
                next_stage()
            elif k == SDLK_r:
                angle = (angle + 15) % 180
            elif k == SDLK_SPACE:
                fire()
            elif k == SDLK_z and pieces():
                undone = pieces()[-1]
                game_world.remove_object(undone)
                redo_stack.append(undone)
                edited()
            elif k == SDLK_y and redo_stack:
                game_world.add_object(redo_stack.pop(), game_world.PIECES)
                edited()
            elif k == SDLK_x:
                game_world.clear_layer(game_world.PIECES)
                redo_stack.clear()
                edited()
            elif k in (SDLK_n, SDLK_RETURN):
                if beam and beam.success:
                    next_stage()
            else:
                for key, kind in hud.KIND_KEYS:
                    if k == key and kind in stage()['inventory']:
                        sel = kind


# ---------------------------------------------------------------- 모드 인터페이스
def init():
    global total_attempts, stage_attempts
    total_attempts = 0
    stage_attempts = [0] * len(rl.STAGES)
    load_stage(0)
    _smoke['step'], _smoke['t'] = 0, get_time()


def finish():
    game_world.clear()


def pause():
    pass


def resume():
    pass


def update():
    global shoot_ch
    if shoot_ch is not None and not sound.is_playing(shoot_ch):
        shoot_ch = None
        launch()
    game_world.update()
    board.reached = set(beam.result['reached']) if beam and beam.done else set()
    if SMOKE_DIR:
        smoke_test()


def draw():
    clear_canvas()
    game_world.render()
    draw_ghost()
    hud.draw(sys.modules[__name__])
    update_canvas()


def draw_ghost():
    """마우스 위치에 놓일 오브젝트 미리보기"""
    if remaining(sel) <= 0:
        return
    mx, my = mouse
    if blocked(stage(), mx, my):
        draw_circle(mx, my, 10, *BLOCK_COLOR, 200)
        thick_line(mx - 7, my - 7, mx + 7, my + 7, 2, BLOCK_COLOR)
        thick_line(mx - 7, my + 7, mx + 7, my - 7, 2, BLOCK_COLOR)
    else:
        Piece(sel, round(mx / 10) * 10, round(my / 10) * 10, angle, ghost=True).draw()


# ---------------------------------------------------------------- 자동 검증
def screenshot(path):
    mod = sys.modules['pico2d.pico2d']
    surf = SDL_CreateRGBSurface(0, rl.W, H, 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000)
    SDL_RenderReadPixels(mod.renderer, None, SDL_PIXELFORMAT_ARGB8888, surf.contents.pixels, surf.contents.pitch)
    SDL_SaveBMP(surf, path.encode())
    SDL_FreeSurface(surf)


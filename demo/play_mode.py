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

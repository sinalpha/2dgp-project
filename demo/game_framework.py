"""모드 스택 기반 게임 프레임웍 (LEC15) + 프레임 시간 (LEC16)"""
import time

running = True
stack = []
frame_time = 0.0
MAX_FRAME_TIME = 0.05   # 창을 끌거나 멈췄을 때 한 프레임에 너무 크게 움직이는 것을 방지


def change_mode(mode):
    """현재 모드를 끝내고 새 모드로 교체"""
    global stack
    if len(stack) > 0:
        stack[-1].finish()
        stack.pop()
    stack.append(mode)
    mode.init()


def push_mode(mode):
    """현재 모드를 pause 하고 새 모드를 위에 쌓는다"""
    global stack
    if len(stack) > 0:
        stack[-1].pause()
    stack.append(mode)
    mode.init()


def pop_mode():
    """현재 모드를 끝내고 아래에 있던 모드를 resume"""
    global stack
    if len(stack) > 0:
        stack[-1].finish()
        stack.pop()
    if len(stack) > 0:
        stack[-1].resume()


def quit():
    global running
    running = False


def run(start_mode):
    global running, stack, frame_time
    running = True
    stack = [start_mode]
    start_mode.init()

    frame_time = 0.0
    current_time = time.time()
    while running:
        stack[-1].handle_events()
        stack[-1].update()
        stack[-1].draw()
        frame_time = min(time.time() - current_time, MAX_FRAME_TIME)
        current_time = time.time()

    while len(stack) > 0:
        stack[-1].finish()
        stack.pop()

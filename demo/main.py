"""RAY TRACER 데모 - Python + pico2d
실행: python main.py
"""
import os
import sys
import pico2d

import game_framework
import raylogic as rl

pico2d.open_canvas(rl.W, rl.H)
# 반투명 선/도형을 그리기 위한 알파 블렌딩
pico2d.SDL_SetRenderDrawBlendMode(sys.modules['pico2d.pico2d'].renderer, pico2d.SDL_BLENDMODE_BLEND)

if os.environ.get('RT_SMOKE'):      # 자동 검증은 타이틀을 건너뛴다
    import play_mode as start_mode
else:
    import title_mode as start_mode

game_framework.run(start_mode)
pico2d.close_canvas()
 
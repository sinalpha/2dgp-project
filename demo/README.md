# RAY TRACER 데모

Python + pico2d 로 만든 1차 발표용 플레이 가능한 데모입니다. 스테이지 4개.

## 실행
```
python main.py
```
pico2d 가 설치된 Python 에서 실행합니다. 이 PC 에서는 기본 `python` (D:\python, 3.14.0) 의 ctypes 가 깨져 있어
`C:\Users\hanhd\AppData\Local\Python\bin\python.exe main.py` 로 실행해야 합니다.

## 조작
| 입력 | 동작 |
|---|---|
| 마우스 클릭 | 선택한 오브젝트 배치 (10픽셀 격자). 이미 놓은 오브젝트를 클릭하면 집어 올려 다시 놓을 수 있음 |
| R / 마우스 휠 | 오브젝트 회전 (15도 단위) |
| 우클릭 | 가까운 오브젝트 제거 |
| 1 / 2 / 3 | 금속 판 / 유리 프리즘 / 매트 블록 선택 |
| Space | 빛 발사 |
| Z / X | 되돌리기 / 전체 재시작 |
| N | 성공 후 다음 스테이지 |
| ESC | 종료 |

## 규칙
빛은 오브젝트에 닿을 때마다 에너지를 잃고(시작 100), 0이 되면 그 지점에서 꺼집니다.
- 금속 판: 정반사, 에너지 -5
- 유리 프리즘: 통과하며 25도 꺾임, 에너지 -10
- 매트 블록: 3갈래로 퍼짐, 에너지 -20 후 나눠 가짐
- 벽: 전부 흡수

| P | 일시정지 (P / ESC 로 복귀) |

## 구조 (수업 슬라이드 방식)
- `main.py` 캔버스를 열고 `game_framework.run(시작 모드)` 만 호출
- `game_framework.py` 모드 스택 (`change_mode / push_mode / pop_mode / quit`) + 프레임 시간 `frame_time`
- `game_world.py` 레이어별 객체 관리 (배경 / 스테이지 / 오브젝트 / 빛)
- 모드: `title_mode` → `play_mode` (→ `pause_mode` push) → `ending_mode`
  각 모드는 `init / finish / handle_events / update / draw / pause / resume` 을 가짐
- 게임 객체 (클래스 1개 = 파일 1개): `background.py`, `board.py`, `piece.py`, `beam.py`
- `hud.py` 표시줄 / 에너지 게이지 / 결과 배너, `gfx.py` 색상 · 굵은 선 · 폰트
- `raylogic.py` 빛 경로 계산과 스테이지 데이터 (화면 무관)
- 빛의 이동은 `거리 += 속도 × frame_time` 으로 계산 (컴퓨터 성능과 무관한 속도)

## 자동 검증
환경변수 `RT_SMOKE=<폴더>` 를 주고 실행하면 스테이지별 해법을 자동 배치/발사하고 화면을 BMP 로 저장합니다.

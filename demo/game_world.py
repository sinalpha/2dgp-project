"""게임 월드: 레이어별 게임 객체 관리 (LEC14)"""

BACK, STAGE, PIECES, BEAM = 0, 1, 2, 3   # 그리는 순서 (뒤 -> 앞)

world = [[], [], [], []]


def add_object(o, depth=0):
    world[depth].append(o)


def add_objects(ol, depth=0):
    world[depth] += ol


def remove_object(o):
    for layer in world:
        if o in layer:
            layer.remove(o)
            return
    raise ValueError('Cannot delete non existing object')


def objects(depth):
    return world[depth]


def clear_layer(depth):
    world[depth].clear()


def clear():
    for layer in world:
        layer.clear()


def update():
    for layer in world:
        for o in layer:
            o.update()


def render():
    for layer in world:
        for o in layer:
            o.draw()

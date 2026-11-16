"""시도 횟수 기록 저장/불러오기 (records.json)"""
import json
import os

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'records.json')


def load():
    """{'last': [스테이지별 횟수], 'best_total': 최소 총 시도} 또는 {}"""
    try:
        with open(PATH, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save(stage_attempts):
    data = load()
    total = sum(stage_attempts)
    data['last'] = list(stage_attempts)
    if 'best_total' not in data or total < data['best_total']:
        data['best_total'] = total
        data['best'] = list(stage_attempts)
    try:
        with open(PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f)
    except OSError:
        pass

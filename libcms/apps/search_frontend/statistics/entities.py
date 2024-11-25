from typing import List, Dict


class Metric:
    def __init__(self, uid: int, title: str, value: int):
        self.id = uid
        self.title = title
        self.value = value

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'value': self.value,
        }


class StatisticsResponse:
    def __init__(self, metrics: List[Metric]):
        self.metrics = metrics

    def to_json(self):
        return {
            'metrics': [m.to_json() for m in self.metrics]
        }

    @staticmethod
    def from_metric_list(metric_list: List[Dict]):
        metrics: List[Metric] = []
        for metric in metric_list:
            metrics.append(Metric(uid=metric['id'], title=metric['title'], value=metric['value']))
        return StatisticsResponse(metrics=metrics)

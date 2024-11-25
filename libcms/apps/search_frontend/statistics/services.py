from ssearch import models as search_models
from .entities import StatisticsResponse


def get_record_statistics(record_id: str):
    statistics = search_models.get_statistics_for_detail(record_id=record_id)
    return StatisticsResponse.from_metric_list(statistics)


def log_record_detail(record_id: str, user, session_id):
    search_models.log_detail(
        record_id=record_id,
        user=user,
        action=search_models.DETAIL_ACTIONS['VIEW_DETAIL'],
        session_id=session_id,
        # from_subscribe=from_subscribe,
    )
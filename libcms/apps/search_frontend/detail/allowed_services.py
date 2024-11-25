from abc import ABC
from functools import lru_cache
from typing import List

from django.contrib.auth.models import User

# from ..order_document import services as order_document_services
from ..record_services import BibRecord, get_bib_record, get_bib_record_by_local_number




class AllowedServiceResolver(ABC):
    def resolve(self, bib_record: BibRecord, user: User) -> List[str]:
        raise NotImplemented


ORDER_DOCUMENT_SERVICE = 'order_document'
ORDER_COPY_SERVICE = 'order_copy'
SUBSCRIBE_TO_ISSUE_SERVICE = 'subscribe_to_issue'
SHOW_STATISTICS = 'show_statistics'
SHOW_MARC_DUMP = 'show_marc_dump'
SHOW_MLT = 'show_mlt'
SHOW_LINKED_RECORDS = 'show_linked_records'
SHOW_RELATED_ISSUES = 'show_related_issues'

class SbAllowedServiceResolver(AllowedServiceResolver):
    def resolve(self, bib_record: BibRecord, user: User):
        services: List[str] = []

        if self.__allow_order_document(bib_record, user):
            services.append(ORDER_DOCUMENT_SERVICE)

        if self.__allow_order_copy(bib_record):
            services.append(ORDER_COPY_SERVICE)

        if self.__allow_subscribe_to_issue(bib_record):
            services.append(SUBSCRIBE_TO_ISSUE_SERVICE)

        if self.__allow_show_statistics(user):
            services.append(SHOW_STATISTICS)

        if self.__allow_show_marc_dump(user):
            services.append(SHOW_MARC_DUMP)

        if self.__allow_show_mlt(bib_record):
            services.append(SHOW_MLT)

        if self.__allow_show_linked_records(bib_record):
            services.append(SHOW_LINKED_RECORDS)

        if self.__allow_show_related_issues(bib_record):
            services.append(SHOW_RELATED_ISSUES)

        return services

    def __allow_order_document(self, bib_record: BibRecord, user: User):

        if bib_record.metadata.media_references.full_text.url:
            return False

        # order_params = order_document_services.prepare_order(
        #     record_id=bib_record.record_id,
        #     username=user.username
        # )
        # return order_params.allow_order
        return False

    def __allow_order_copy(self, bib_record: BibRecord):
        marc_query = bib_record.template.mq

        leader_7 = (marc_query.leader_data()[7:8] or [''])[0]
        leader_8 = (marc_query.leader_data()[8:9] or [''])[0]

        if leader_7 == 's' and leader_8 == '1':
            return False

        for sfq in marc_query.get_field('850').get_subfield('b').list():
            if sfq.get_data() == 'BD':
                return True

        return False

    def __allow_subscribe_to_issue(self, bib_record: BibRecord):
        marc_query = bib_record.template.mq
        leader_7 = marc_query.leader_data()[7:8]

        allow_subscribe = False
        if 'SIC' in bib_record.metadata.record_catalogs:
            allow_subscribe = False
        elif leader_7 == 's':
            allow_subscribe = True
        else:
            parent_record_local_number = marc_query.f('461').f('001').d()
            parent_record = get_bib_record_by_local_number(local_number=parent_record_local_number)

            if parent_record is not None:
                leader_7 = (parent_record.template.mq.leader_data()[7:8] or [''])[0]
                if leader_7 == 's':
                    allow_subscribe = True

        return allow_subscribe

    def __allow_show_statistics(self, user: User):
        return user.is_superuser or user.is_staff

    def __allow_show_marc_dump(self, user: User):
        return user.is_superuser or user.is_staff

    def __allow_show_mlt(self, bib_record: BibRecord):
        return False

    def __allow_show_linked_records(self, bib_record: BibRecord):
        return True

    def __allow_show_related_issues(self, bib_record: BibRecord):
        marc_query = bib_record.template.mq

        local_numbers: List[str] = []
        for f451 in marc_query.f('451').list():
            local_number = f451.f('001').d()
            if not local_number:
                continue
            local_numbers.append(local_number)
        return bool(local_numbers)


class ChelAllowedServiceResolver(AllowedServiceResolver):
    def resolve(self, bib_record: BibRecord, user: User):
        return []



@lru_cache
def get_resolver() -> AllowedServiceResolver:
    return ChelAllowedServiceResolver()
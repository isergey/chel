from typing import List, Dict

from ..cover_resolver import resolve_for_search
from dataclasses import dataclass
from ..record_metadata.holders import Holders
from ..record_services import BibRecord


@dataclass
class Attribute:
    title: str
    values: List[str]

    def to_json(self):
        return {
            'title': self.title,
            'values': self.values
        }


@dataclass
class ValueTitle:
    value: str
    title: str

    def to_json(self):
        return {
            'value': self.value,
            'title': self.title
        }


@dataclass
class Media:
    media_type: str
    title: str
    url: str

    def to_json(self):
        return {
            'media_type': self.media_type,
            'title': self.title,
            'url': self.url
        }


@dataclass
class BibRecordDetail:
    record_id: str
    local_number: str
    title: str
    primary_responsibility: str
    publication_date: str
    libcard: str
    subjects: List[str]
    keywords: List[str]
    annotation: str
    attributes: List[Attribute]
    cover_url: str
    media: List[Media]
    holders: Holders
    allowed_services: List[str]
    source_documents: List[ValueTitle]

    def to_json(self):
        return {
            'record_id': self.record_id,
            'local_number': self.local_number,
            'title': self.title,
            'primary_responsibility': self.primary_responsibility,
            'publication_date': self.publication_date,
            'libcard': self.libcard,
            'subjects': [i for i in self.subjects],
            'keywords': [i for i in self.keywords],
            'annotation': self.annotation,
            'attributes': [i.to_json() for i in self.attributes],
            'cover_url': self.cover_url,
            'media': [i.to_json() for i in self.media],
            'holders': self.holders.to_json(),
            'allowed_services': self.allowed_services,
            'source_documents': [rd.to_json() for rd in self.source_documents],
        }

    @staticmethod
    def from_bib_record(bib_record: BibRecord, allowed_services: List[str]):
        source_documents: List[ValueTitle] = []

        for local_number, title in bib_record.template.source_documents:
            source_documents.append(ValueTitle(
                value=local_number,
                title=title
            ))

        cover_url = resolve_for_search(bib_record)

        return BibRecordDetail(
            record_id=bib_record.record_id,
            local_number=bib_record.template.local_number,
            title=bib_record.template.title,
            primary_responsibility=bib_record.template.primary_responsibility,
            publication_date=bib_record.template.publication_date,
            libcard=bib_record.libcard.as_html,
            subjects=bib_record.template.subject_heading,
            keywords=bib_record.template.subject_keywords,
            annotation=bib_record.template.annotation,
            attributes=get_attributes(bib_record),
            cover_url=cover_url,
            media=_get_media(bib_record),
            holders=bib_record.metadata.holders,
            allowed_services=allowed_services,
            source_documents=source_documents
        )


def get_attributes(bib_record: BibRecord):
    attributes: List[Attribute] = []
    template = bib_record.template

    if template.bbk:
        attributes.append(Attribute(
            title='ББК',
            values=template.bbk
        ))

    if template.udc:
        attributes.append(Attribute(
            title='УДК',
            values=template.udc
        ))
    return attributes


def _get_media(bib_record: BibRecord):
    media: List[Media] = []
    media_references = bib_record.metadata.media_references
    for media_reference in media_references.all:
        extension = media_reference.url.lower().split('.')[-1]
        media_type = 'content'
        if extension in ['pdf']:
            media_type = 'content'
        elif extension in ['mp3']:
            media_type = 'audio'

        elif extension in ['mp4']:
            media_type = 'video'

        elif extension in ['gif', 'jpg', 'jpeg', 'png']:
            continue

        media.append(Media(
            media_type=media_type,
            title=media_reference.title,
            url=media_reference.url
        ))

    return media


@dataclass
class LinkedRecord:
    id: str
    title: str
    part_title: str
    detail_url: str
    cover_url: str

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'part_title': self.part_title,
            'detail_url': self.detail_url,
            'cover_url': self.cover_url
        }

    @staticmethod
    def from_bib_record(bib_record: BibRecord):

        part_title = ''
        if bib_record.template.publication_date:
            part_title = 'Издание {publication_date}'.format(publication_date=str(bib_record.template.publication_date))

        return LinkedRecord(
            id=bib_record.record_id,
            title=bib_record.template.title,
            part_title=part_title,
            detail_url=bib_record.detail_url,
            cover_url=bib_record.metadata.media_references.cover.url
        )


@dataclass
class LinkedRecordsResponse:
    items: List[LinkedRecord]

    def to_json(self):
        return {
            'items': [item.to_json() for item in self.items]
        }


@dataclass
class StatItem:
    title: str
    value: str


@dataclass
class Statistics:
    items: List[StatItem]

    @staticmethod
    def from_stat(items_data: List[Dict]):
        items: List[StatItem] = []

        for item_data in items_data or []:
            items.append(StatItem(
                title=item_data['title'],
                value=item_data['value']
            ))

        return Statistics(
            items=items
        )


@dataclass
class RecordDump:
    marc_dump: str
    json: str

    def to_json(self):
        return {
            'marc_dump': self.marc_dump,
            'json': self.json
        }

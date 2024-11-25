from functools import lru_cache
from typing import List

from junimarc.marc_query import MarcQuery, FieldQuery
from junimarc.record import Record
from . import utils


class RusmarcTemplate:
    def __init__(self, marc_record: Record, marc_query: MarcQuery = None, show_200e=True):
        self.marc_record = marc_record
        self.mq = marc_query if marc_query is not None else MarcQuery(marc_record)
        self.show_200e = show_200e

    @property
    @lru_cache(maxsize=None)
    def local_number(self):
        return self.mq.get_field('001').get_data()

    @property
    @lru_cache(maxsize=None)
    def title(self):
        title = []
        title200 = self.__get_200_title(fq=self.mq.get_field('200'))
        title461 = self.__get_200_title(fq=self.mq.get_field('461').get_field('200'))
        title463 = self.__get_200_title(fq=self.mq.get_field('463').get_field('200'))

        bib_level = self.bib_level

        if title463 and bib_level == 'a':
            title.append(title200)
            if title461:
                title.append(' // ')
                title.append(title461)

            if title463:
                if not title461:
                    title.append(' // ')
                else:
                    utils.append_symbol('.', title)
                    title.append(' — ')
                title.append(title463)
        elif title461:
            title.append(title461)
            utils.append_symbol('.', title)
            title.append(' — ')
            title.append(title200)
        else:
            title.append(title200)

        return ''.join(title).strip()

    @property
    @lru_cache(maxsize=None)
    def primary_responsibility(self):
        parts = []
        for fq in self.mq.get_field('700').list():
            part = self.__get_personal_name(fq)
            if part:
                parts.append(part)

        if not parts:
            for fq in self.mq.get_field('710').list():
                part = fq.get_subfield('a').get_data().rstrip()
                if part:
                    parts.append(part)

        if not parts:
            for fq in self.mq.get_field('720').list():
                part = self.__get_personal_name(fq)
                if part:
                    parts.append(part)

        if not parts:
            for fq in self.mq.get_field('730').list():
                part = self.__get_personal_name(fq)
                if part:
                    parts.append(part)

        if not parts:
            for fq in self.mq.get_field('740').list():
                part = self.__get_personal_name(fq)
                if part:
                    parts.append(part)

        return ', '.join(parts).strip()

    @property
    @lru_cache(maxsize=None)
    def publication_date(self):
        result = ''

        date210 = self.mq.get_field('210').get_subfield('d').get_data().rstrip()
        date461_210 = self.mq.get_field('461').get_field('210').get_subfield('d').get_data().rstrip()
        date463_210 = self.mq.get_field('463').get_field('210').get_subfield('d').get_data().rstrip()

        if date463_210:
            result = date463_210
        elif date461_210:
            result = date461_210
        else:
            result = date210

        return result.strip()

    @property
    @lru_cache(maxsize=None)
    def source_documents(self):

        docs:List[List[str, str]] = []

        f461 = self.mq.f('461')

        local_number = f461.f('001').d()
        title = f461.f('200').s('a').d()

        if local_number:
            docs.append([local_number, title])

        f463 = self.mq.f('463')

        local_number = f463.f('001').d()
        title = f463.f('200').s('a').d()


        if local_number:
            docs.append([local_number, title])
        return docs

    @property
    @lru_cache(maxsize=None)
    def annotation(self):
        values: List[str] = []
        for fq in self.mq.get_field('330').list():
            utils.add_to_values(values, fq.get_subfield('a').get_data())
        return '\n'.join(values).strip()

    @property
    @lru_cache(maxsize=None)
    def bbk(self):
        values = []
        for fq in self.mq.get_field('689').list():
            utils.add_to_values(values, fq.get_subfield('a').get_data())

        for fq in self.mq.get_field('686').list():
            sfa = fq.get_subfield('a').get_data()
            sf2 = fq.get_subfield('2').get_data()
            if sf2 == 'rubbk':
                utils.add_to_values(values, sfa)
        return values

    @property
    @lru_cache(maxsize=None)
    def udc(self):
        values = []
        for fq in self.mq.get_field('686').list():
            sfa = fq.get_subfield('a').get_data()
            sf2 = fq.get_subfield('2').get_data()
            if sf2 == 'udc':
                utils.add_to_values(values, sfa)
        return values

    @property
    @lru_cache(maxsize=None)
    def material_type(self):
        return self.__get_material_type()

    @property
    @lru_cache(maxsize=None)
    def document_type(self):
        return self.__get_document_type()

    @property
    @lru_cache(maxsize=None)
    def bib_level(self):
        return self.mq.leader_data()[7:8]

    @property
    @lru_cache(maxsize=None)
    def record_type(self):
        return self.mq.leader_data()[6:7]

    @property
    @lru_cache(maxsize=None)
    def hierarchy_level(self):
        return self.mq.leader_data()[8:9]

    @property
    @lru_cache(maxsize=None)
    def subject_heading(self):
        values: List[str] = []
        for fq in self.mq.get_field('606').list():
            for sfq in fq.get_subfield('a').list():
                utils.add_to_values(values, sfq.get_data())

        for fq in utils.get_each_filed_query(self.mq, '4'):
            for inner_fq in fq.get_field('606').list():
                utils.add_to_values(values, inner_fq.get_subfield('a').get_data())

        return values

    @property
    @lru_cache(maxsize=None)
    def subject_keywords(self):
        values = []
        for fq in self.mq.get_field('610').list():
            for sfq in fq.get_subfield('a').list():
                utils.add_to_values(values, sfq.get_data())

        for fq in utils.get_each_filed_query(self.mq, '4'):
            for inner_fq in fq.get_field('610').list():
                utils.add_to_values(values, inner_fq.get_subfield('a').get_data())

        return values

    def __get_200_title(self, fq: FieldQuery, parent_v=''):
        title = []

        for sfa in fq.get_subfield('a').list():
            title_part = sfa.get_data().rstrip()

            if not title_part:
                continue

            utils.append_symbol(';', title)
            title.append(' ' + title_part)

        title_part = fq.get_subfield('b').get_data().rstrip()
        if title_part:
            title.append(''.join([' [', title_part, ']']))

        if self.show_200e:
            title_part = fq.get_subfield('e').get_data().rstrip()
            if title_part:
                utils.append_symbol(':', title)
                title.append(' ' + title_part)

        title_part = fq.get_subfield('h').get_data().rstrip()
        if title_part:
            utils.append_symbol('.', title)
            title.append(' ' + title_part)

        title_part = fq.get_subfield('i').get_data().rstrip()
        if title_part:
            utils.append_symbol('.', title)
            title.append(' ' + title_part)

        # title_part = fq.get_subfield('f').get_data().rstrip()
        # if title_part:
        #     title.append(' / ' + title_part)

        # title_part = fq.get_subfield('g').get_data().rstrip()
        # if title_part:
        #     append_symbol(':', title)
        #     title.append(' ' + title_part)



        title_part = fq.get_subfield('v').get_data().rstrip()

        if title_part:

            parent_200_a = self.mq.get_field('200').get_subfield('a').d()
            cleaned_parent_200_a = ''.join(parent_200_a.lower().split(' '))
            cleaned_title_part = ''.join(title_part.lower().split(' '))

            if cleaned_parent_200_a != cleaned_title_part:
                if self.mq.get_field('200').get_subfield('a').get_data().rstrip() != title_part:
                    utils.append_symbol('.', title)
                    title.append(' — ' + title_part)

        return ''.join(title).strip()

    def __get_personal_name(self, fq: FieldQuery):
        sa = fq.get_subfield('a').get_data()

        sb = fq.get_subfield('b').get_data()
        sg = fq.get_subfield('g').get_data()

        result = []

        if sg:
            result.append(sa)
            result.append(', ')
            result.append(sg)
        elif sb:
            result.append(sa)
            result.append(' ')
            result.append(sb)
        else:
            result.append(sa)

        return ''.join(result).strip()

    def __get_material_type(self):
        marc_query = self.mq
        record_type = self.record_type
        bib_level = self.bib_level
        hierarchy_level = self.hierarchy_level
        f105_a = marc_query.get_field('105').get_subfield('a').get_data() or ' ' * 9
        f105_a_pos_4 = f105_a[4:5]
        f105_a_pos_5 = f105_a[5:6]
        f105_a_pos_6 = f105_a[6:7]
        f105_a_pos_7 = f105_a[7:8]
        f105_a_pos_4_7 = [f105_a_pos_4, f105_a_pos_5, f105_a_pos_6, f105_a_pos_7]

        material_types = []

        if bib_level == 'm' and hierarchy_level == '0':
            material_types.append('monography')

        if bib_level == 's' and hierarchy_level == '1':
            material_types.append('journal_paper')

        if record_type == 'a' and bib_level == 'm' and hierarchy_level == '2':
            material_types.append('issues')

        if bib_level == 'a' or bib_level == 'b':
            material_types.append('articles_reports')

        if bib_level == 'c':
            material_types.append('collections')

        if bib_level == 'i':
            material_types.append('integrity')

        if record_type == 'c' or record_type == 'd':
            material_types.append('musical_scores')

        if record_type == 'e' or record_type == 'f':
            material_types.append('maps')

        if record_type == 'g':
            material_types.append('video')

        if record_type == 'i' or record_type == 'j':
            material_types.append('sound_records')

        if record_type == 'k':
            material_types.append('graphics')

        if ((marc_query.get_field('106').is_exist() or marc_query.get_field('135').is_exist())
                and (marc_query.get_field('856').get_subfield('u').is_exist()
                     or marc_query.get_field('330').get_subfield('u').is_exist())
        ):
            material_types.append('e_resources')

        if 'm' in f105_a_pos_4_7:
            material_types.append('dissertation_abstracts')

        if 'd' in f105_a_pos_4_7:
            material_types.append('referats')

        if 'j' in f105_a_pos_4_7:
            material_types.append('textbook')

        if bib_level == 'm' and 'k' in f105_a_pos_4_7:
            material_types.append('patents')

        if bib_level == 'm' and 'l' in f105_a_pos_4_7:
            material_types.append('standarts')

        if bib_level == 's' and 'l' in f105_a_pos_4_7:
            material_types.append('legislative_acts')

        if bib_level == 'm' and 'p' in f105_a_pos_4_7:
            material_types.append('technical_reports')

        if 'g' in f105_a_pos_4_7:
            material_types.append('references')

        if 'e' in f105_a_pos_4_7:
            material_types.append('dictionaries')

        if 'f' in f105_a_pos_4_7:
            material_types.append('encyclopedias')

        return material_types

    def __get_document_type(self):
        record_type = self.record_type
        bib_level = self.bib_level
        f105_a = self.mq.get_field('105').get_subfield('a').get_data()
        f105_a_4_7 = f105_a[4:8]
        f116_a = self.mq.get_field('116').get_subfield('a').get_data()
        f116_a_pos_0 = f116_a[0:1]

        values = []

        if 'e' in f105_a_4_7:
            values.append('dict')

        elif 'f' in f105_a_4_7:
            values.append('encyc')

        elif 'g' in f105_a_4_7:
            values.append('ref')

        elif 'j' in f105_a_4_7:
            values.append('textbook')

        elif 'p' in f105_a_4_7:
            values.append('tech_report')

        elif 'd' in f105_a_4_7 and 'm' in f105_a_4_7:
            values.append('author_abstract')

        elif 'm' in f105_a_4_7:
            values.append('disser')

        elif record_type == 'k' and bib_level == 'm' and f116_a_pos_0 == 'b':
            values.append('picture')

        return values

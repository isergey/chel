from .libcard import LibCard
from ..marc_query import MarcQuery
from ..record import Record
from .utils import repeat, join, wrap, suffix


class RusmarcLibCard(LibCard):
    def __init__(self, as_html=False):
        self.__as_html = as_html

    def template(self, mq: MarcQuery):
        primary_responsibility = self.__primary_responsibility(mq)

        if self.__as_html:
            primary_responsibility = wrap(
                '<span class="lc-record__primary-responsibility">',
                primary_responsibility,
                '</span>'
            )

        parts = [
            join([
                primary_responsibility,
                self.__title_section(mq)], ' ' if self.__as_html else '\n'),
            self.__publishers_imprint_section(mq),
            self.__issue_section(mq),
            self.__physics_section(mq),
            self.__series_section(mq),
            self.__note_section(mq),
            self.__ident_section(mq),
        ]

        return suffix(join(parts, '. – '), '.')

    def __title_section(self, mq: MarcQuery):
        level = mq.l(7)
        is_monograph = level == 'm'

        f461 = mq.f('461')
        f463 = mq.f('463')
        if f461.is_exist() and f463.is_exist():
            mq461 = MarcQuery(f461.get_element().get_record())
            mq463 = MarcQuery(f463.get_element().get_record())
            title_461 = self.__f200(mq461)
            title_mq463 = self.__f200(mq463)

            return join([
                self.__f200(mq),
                join([
                    title_461, repeat(mq463.f('210').s('d'), ' '),
                    title_mq463,
                ], '. – ')
            ], ' // ')
        elif f461.is_exist():

            mq461 = MarcQuery(f461.get_element().get_record())
            title_461 = self.__f200(mq461)

            f200a = repeat(mq.f('200').s('a'), ', ')
            volume = repeat(mq461.f('200').s('v'), ', ')

            monograph_title = self.__f200(mq) if is_monograph and f200a != volume else ''

            return join([
                join([title_461, self.__f210(mq461)], '. – '),
                join([
                    repeat(mq461.f('200').s('v'), ', '),
                    monograph_title
                ], ': ')
            ], '. ')



        return join([self.__f200(mq)], '. ')

    def __primary_responsibility(self, mq: MarcQuery):
        f461 = mq.f('461')
        if f461.is_exist():
            mq461 = MarcQuery(f461.get_element().get_record())
        else:
            mq461 = MarcQuery(Record())
        return suffix(self.__f700(mq) or self.__f710(mq) or self.__f700(mq461) or self.__f710(mq461), '.')

    def __publishers_imprint_section(self, mq: MarcQuery):
        return self.__f205(mq)

    def __issue_section(self, mq: MarcQuery):
        return self.__f210(mq)

    def __physics_section(self, mq: MarcQuery):
        return self.__f215(mq)

    def __series_section(self, mq: MarcQuery):
        return join([self.__f225(mq), self.__issued_with(mq), self.__translation(mq)], ' . ')

    @staticmethod
    def __note_section(mq: MarcQuery):
        return join([
            repeat(mq.f('010').s('9'), ', '),
            repeat(mq.f('320').s('a'), ', '),
        ], '. ')

    @staticmethod
    def __ident_section(mq: MarcQuery):
        f010 = mq.f('010')
        a = repeat(f010.s('a'), ', ')
        isbn = ''
        if a:
            isbn = 'ISBN: ' + a

        b = repeat(f010.s('b'), ', ')
        d = repeat(f010.s('d'), ', ')
        return join([isbn, wrap('(', b, ')'), d], ' : ')

    def __translation(self, mq: MarcQuery):
        f454 = mq.get_field('454')
        if not f454.is_exist():
            return ''
        emq = MarcQuery(f454.get_element().get_record())

        label = 'Перевод издания:'
        if self.__as_html:
            label = '<span class="lc-record__label">Перевод издания</span>:'

        return join(
            [label, self.__title_section(emq)],
            ' ')

    def __issued_with(self, mq: MarcQuery):

        mq423_titles = []

        for f423q in mq.f('423').list():
            mq423_titles.append(self.__f200(MarcQuery(f423q.get_element().get_record())))

        label = 'В одной обложке с:'
        if self.__as_html:
            label = '<span class="lc-record__label">В одной обложке с</span>:'

        return join(
            [label, join(mq423_titles, '., ')],
            ' ')

    def __f200(self, mq: MarcQuery):
        f200 = mq.f('200') 

        a = repeat(f200.s('a'), ' ; ')
        e = repeat(f200.s('e'), ' ; ')

        ae = join([a, e], ' : ')

        f = repeat(f200.s('f'), ' ; ')
        g = repeat(f200.s('g'), ' ; ')

        fg = join([f, g], ' ; ')

        if self.__as_html:
            ae = wrap('<span class="lc-record__title">', ae, '</span>')

        return join([ae, fg], ' / ')

    @staticmethod
    def __f205(mq: MarcQuery):
        f205 = mq.f('205')
        a = repeat(f205.s('a'), ' ; ')
        return a

    @staticmethod
    def __f210(mq: MarcQuery, without_d=False):
        f210 = mq.f('210')
        a = repeat(f210.s('a'), ' ; ')
        c = repeat(f210.s('c'), ' ; ')
        d = repeat(f210.s('d'), ' ; ')
        if without_d:
            d = ''
        ac = join([a, c], ' : ')
        return join([ac, d], ', ')

    @staticmethod
    def __f215(mq: MarcQuery):
        f215 = mq.f('215')
        a = repeat(f215.s('a'), ' ; ')
        c = repeat(f215.s('c'), ' ; ')
        ac = join([a, c], ' : ')
        d = repeat(f215.s('d'), ' ; ')

        return join([ac, d], ' ; ')

    @staticmethod
    def __f225(mq: MarcQuery):
        f225 = mq.f('225')

        a = repeat(f225.s('a'), ' ; ')
        f = repeat(f225.s('f'), ' ; ')
        g = repeat(f225.s('g'), ' ; ')
        i = repeat(f225.s('i'), ' ; ')

        fg = join([f, g], ' ; ')

        fgi = join([fg, i], '. ')

        res = join([a, fgi], ' / ')

        return wrap('(', res, ')')

    @staticmethod
    def __f700(mq: MarcQuery):
        f700 = mq.f('700')

        a = repeat(f700.s('a'), ' ; ')
        b = repeat(f700.s('b'), ' ; ')
        g = repeat(f700.s('g'), ' ; ')

        ab = join([a, b], ', ')
        ag = join([a, g], ', ')
        return ab if b else ag

    @staticmethod
    def __f710(mq: MarcQuery):
        f710 = mq.f('710')
        a = repeat(f710.s('a'), ' ; ')
        return a

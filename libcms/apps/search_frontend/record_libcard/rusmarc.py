from functools import lru_cache
from lxml import etree


from junimarc.ruslan_xml import record_to_xml
from junimarc.libcard import rusmarc
from junimarc.marc_query import MarcQuery
from junimarc.record import Record

from ..record_libcard.utils import beautify_libcard


class RecordLibCard:
    html_libcard = rusmarc.RusmarcLibCard(as_html=True)
    string_libcard = rusmarc.RusmarcLibCard(as_html=False)

    def __init__(self, mq: MarcQuery):
        self.__mq = mq

    @property
    @lru_cache(maxsize=None)
    def as_html(self):
        # return self.html_libcard.template(self.__mq)
        return RecordLibCardRenderer(marc_record=self.__mq.record, view='full').as_string

    @property
    @lru_cache(maxsize=None)
    def as_string(self):
        #return self.string_libcard.template(self.__mq)
        return RecordLibCardRenderer(marc_record=self.__mq.record, view='short').as_string


class RecordLibCardRenderer:
    libcard = rusmarc.RusmarcLibCard(as_html=True)

    def __init__(self, marc_record: Record, view='full'):
        self.__marc_record = marc_record
        self.__view = view
        self.__mq = MarcQuery(self.__marc_record)

    @property
    @lru_cache(maxsize=None)
    def as_string(self) -> str:
        #return self.libcard.template(self.__mq)
        libcard_xml_string = beautify_libcard(self.__transform().strip())
        return libcard_xml_string

    @lru_cache(maxsize=None)
    def __transform(self):
        record_tree = self.__record_to_xml_tree()
        if self.__view == 'full':
            transform = get_full_xslt_template()
        else:
            transform = get_short_xslt_template()
        libcard_tree = transform(record_tree)
        return etree.tostring(libcard_tree, pretty_print=True, encoding='utf-8').decode('utf-8')

    @lru_cache(maxsize=None)
    def __record_to_xml_tree(self):
        return record_to_xml(self.__marc_record)

@lru_cache(maxsize=None)
def get_full_xslt_template():
    xslt = etree.parse('transformers/full_document.xsl')
    return etree.XSLT(xslt)


@lru_cache(maxsize=None)
def get_short_xslt_template():
    xslt = etree.parse('transformers/short_document.xsl')
    return etree.XSLT(xslt)

from .record_services import BibRecord

BOOK_COVER = '/media/files/newportal/zag_book.gif'

ARTICLES_COVERS = [
    '/media/files/newportal/zag_st_yellow.gif',
    '/media/files/newportal/zag_st_purple.gif',
    '/media/files/newportal/zag_st_green.gif',
    '/media/files/newportal/zag_st.gif'
]


def resolve_for_search(bib_record: BibRecord):
    cover_url = bib_record.metadata.media_references.cover.url

    if not cover_url:
        if set(bib_record.metadata.record_catalogs) & {'BOOKS', 'DEP'}:
            cover_url = BOOK_COVER
        elif 'articles_reports' in bib_record.template.material_type:
            cover_url = __resolve_article_cover(bib_record)

    return cover_url


def resolve_for_income(income_group_code: str, bib_record: BibRecord):
    cover_url = bib_record.metadata.media_references.cover.url
    if not cover_url and income_group_code == 'articles':
        cover_url = __resolve_article_cover(bib_record)

    return cover_url



def __resolve_article_cover(bib_record: BibRecord):
    index = ord(bib_record.template.title[0:1] or '0') % len(ARTICLES_COVERS)
    cover_url = ARTICLES_COVERS[index]
    return cover_url

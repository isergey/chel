# coding=utf-8
INITIAL_RULE = """
\"\"\"
index_document - индексный документ
rq - junimarc.MarcQuery записи
jrecord - junimarc.Record
record - запись харвестра
record_content - контент записи харвестра
get_full_text(uri) - загрузка и извленение полного текста из pdf документа. Результат кешируется
urls = {} - словарь с URL документов
\"\"\"


FULL_TEXT_URL = 'http://scairbis.vip.cbr.ru'
GROUP_FIELDS_CACHE = {}
EACH_FIELD_QUERY_CACHE = {}


def _get_group_fields(prefix=''):
    value = GROUP_FIELDS_CACHE.get(prefix)

    if value is not None:
        return value

    group_fields = []
    GROUP_FIELDS_CACHE[prefix] = group_fields;

    for field in jrecord.get_fields():
        tag = field.get_tag()
        if tag.startswith(prefix):
            group_fields.append(tag)

    return group_fields;


def _get_each_filed_query(rq, prefix):
    value = EACH_FIELD_QUERY_CACHE.get(prefix)

    if value is not None:
        return value

    group_field_queries = []
    EACH_FIELD_QUERY_CACHE[prefix] = group_field_queries

    for tag in _get_group_fields(prefix):
        for fq in rq.get_field(tag).list():
            group_field_queries.append(fq)

    return group_field_queries

def _add_to_non_empty_values(values, data):
    if data and len(values) > 0:
        values.append(data)


def _add_to_values(values, data):
    if data:
        if type(data) in [list, set]:
            values.extend(data)
        else:
            values.append(data)
    return values


def _get_each_subfield_data(sfq):
    values = []
    for sf in sfq.list():
        _add_to_values(values, sf.get_gata())
    return ' '.join(values)


def _get_each_subfield_data(sfq):
    values = [];
    for sf in sfq.list():
        _add_to_values(values, sf.get_data())
    return ' '.join(values)


def _extract_700_field(fq):
    values = []
    _add_to_values(values, fq.get_subfield('a').get_data());
    _add_to_values(values, fq.get_subfield('b').get_data());
    _add_to_values(values, _get_each_subfield_data(fq.get_subfield('c')));
    _add_to_values(values, fq.get_subfield('d').get_data());
    _add_to_values(values, fq.get_subfield('g').get_data());
    _add_to_values(values, _get_each_subfield_data(fq.get_subfield('o')));
    return ' '.join(values);


def annotation(rq):
    values = []
    for fq in rq.get_field('330').list():
        _add_to_values(values, fq.get_subfield('a').get_data())
    return values


def author(rq):
    values = []
    for fq in rq.get_field('700').list():
        _add_to_values(values, _extract_700_field(fq))

    for fq in rq.get_field('701').list():
        _add_to_values(values, _extract_700_field(fq))

    for fq in rq.get_field('702').list():
        _add_to_values(values, _extract_700_field(fq))

    for fq in rq.get_field('703').list():
        _add_to_values(values, _extract_700_field(fq))

    return values;


def author_name_corporate(rq):
    fq_list = [
        rq.get_field('710'),
        rq.get_field('711'),
        rq.get_field('712'),
        rq.get_field('713'),
    ]
    values = []

    for fq_item in fq_list:
        for fq in fq_item.list():
            for sf in fq.get_subfields().list():
                _add_to_values(values, sf.get_data())

    return values

def bbk(rq):
    values = []
    for fq in rq.get_field('689').list():
        _add_to_values(values, fq.get_subfield('a').get_data())

    for fq in rq.get_field('686').list():
        sfa = fq.get_subfield('a').get_data()
        sf2 = fq.get_subfield('2').get_data()
        if sf2 == 'rubbk':
            _add_to_values(values, sfa)
    return values


def bib_level(rq):
    return rq.leader_data()[7:8] or '';


def code_language(rq):
    values = [];
    for fq in rq.get_field('101').list():
        for sfq in fq.get_subfield('a').list():
            _add_to_values(values, sfq.get_data());
    return values;

def content_text(eq):
    values = []
    # return []
    full_text_prefix = FULL_TEXT_URL
    for fq in rq.get_field('856').list():
        sfy_data = fq.get_subfield('y').get_data()
        sfz_data = fq.get_subfield('z').get_data()
        if sfz_data == 'Содержание' and sfy_data.startswith('/text'):
            content = get_full_text(full_text_prefix + sfy_data)
            _add_to_values(values, content)
    return values

def content_type(rq):
    values = [];
    sfa = rq.get_field('105').get_subfield('a').get_data()
    positions = [4, 5, 6, 7];
    for i in positions:
        data = (sfa[i:i+1] or '').strip()
        if data == '|':
            continue
        _add_to_values(values, data)
    return values


def content_notes(rq):
    values = []
    for fq in rq.get_field('327').list():
        for sfq in fq.get_subfield('a').list():
            _add_to_values(values, sfq.get_data());
    return values;


def date_of_publication(rq):
    f210d = rq.get_field('210').get_subfield('d').get_data()
    f461210d = rq.get_field('461').get_field('210').get_subfield('d').get_data()
    f463210d = rq.get_field('463').get_field('210').get_subfield('d').get_data()

    values = []
    _add_to_values(values, f210d)
    _add_to_values(values, f461210d)
    _add_to_values(values, f463210d)

    return values[0:1] or ''

def date_of_publication_of_original(rq):
    values = []
    for fq in _get_each_filed_query(rq, '455'):
        _add_to_values(values, fq.get_field('210').get_subfield('d').get_data())
    return values

def document_type(rq):
    leader06 = rq.leader_data()[6:7]
    leader07 = rq.leader_data()[7:8]
    leader08 = rq.leader_data()[8:9]
    f105_a = rq.get_field('105').get_subfield('a').get_data()
    f105_a_4_7 = f105_a[4:8]
    f110_a = rq.get_field('105').get_subfield('a').get_data()
    f110_a_pos_0 = f110_a[0:1]
    f115_a = rq.get_field('115').get_subfield('a').get_data()
    f115_a_pos_0 = f115_a[0:1]
    f116_a = rq.get_field('116').get_subfield('a').get_data()
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
        
    elif leader06 == 'k' and leader07 == 'm' and f116_a_pos_0 == 'b':
        values.append('picture')
    return values


def grnti(rq):
    values = []
    for fq in rq.get_field('689').list():
        _add_to_values(values, fq.get_subfield('a').get_data())

    for fq in rq.get_field('686').list():
        sfa = fq.get_subfield('a').get_data();
        sf2 = fq.get_subfield('2').get_data();
        if sf2 == 'rugasnti':
            _add_to_values(values, sfa);
    return values;


def isbn(rq):
    values = []
    _add_to_values(values, rq.get_field('010').get_subfield('a').get_data())
    for tag in _get_group_fields():
        _add_to_values(values, rq.get_field(tag).get_field('010').get_subfield('a').get_data())
    return values


def issn(rq):
    values = []
    _add_to_values(values, rq.get_field('011').get_subfield('a').get_data())
    _add_to_values(values, rq.get_field('225').get_subfield('x').get_data())
    for fq in _get_each_filed_query(rq, '4'):
        _add_to_values(values, fq.get_field('011').get_subfield('a').get_data())
    return values


def full_text(rq):
    values = []
    # return []
    full_text_prefix = FULL_TEXT_URL
    
    for fq in rq.get_field('856').list():
        sfy_data = fq.get_subfield('y').get_data()
        sfz_data = fq.get_subfield('z').get_data()
        if sfz_data == 'Полный текст' and sfy_data.startswith('/text'):
            content = get_full_text(full_text_prefix + sfy_data)
            _add_to_values(values, content)
    return values


def local_number(rq):
    return rq.get_field('001').get_data();


def notes(rq):
    values = []
    for fq in rq.get_field('330').list():
        for sfq in fq.get_subfield('a').list():
            _add_to_values(values, sfq.get_data())
    return values


def material_type(rq):
    leader6 = rq.leader_data()[6:7]
    leader7 = rq.leader_data()[7:8]
    leader8 = rq.leader_data()[8:9]
    f105_a = rq.get_field('105').get_subfield('a').get_data() or ' ' * 9
    f105_a_pos_4 = f105_a[4:5]
    f105_a_pos_5 = f105_a[5:6]
    f105_a_pos_6 = f105_a[6:7]
    f105_a_pos_7 = f105_a[7:8]
    f105_a_pos_4_7 = [f105_a_pos_4, f105_a_pos_5, f105_a_pos_6, f105_a_pos_7]

    values = []

    if leader7 == 'm' and leader8 == '0':
        _add_to_values(values, 'monography')

    if leader7 == 's' and leader8 == '1':
        _add_to_values(values, 'journal_paper')

    if leader6 == 'a' and leader7 == 'm' and leader8 == '2':
        _add_to_values(values, 'issues')

    if leader7 == 'a' or leader7 == 'b':
        _add_to_values(values, 'articles_reports')

    if leader7 == 'c':
        _add_to_values(values, 'collections')

    if leader7 == 'i':
        _add_to_values(values, 'integrity')

    if leader6 == 'c' or leader6 == 'd':
        _add_to_values(values, 'musical_scores')

    if leader6 == 'e' or leader6 == 'f':
        _add_to_values(values, 'maps')

    if leader6 == 'g':
        _add_to_values(values, 'video')

    if leader6 == 'i' or leader6 == 'j':
        _add_to_values(values, 'sound_records')

    if leader6 == 'k':
        _add_to_values(values, 'graphics')

    if ((rq.get_field('106').is_exist() or rq.get_field('135').is_exist())
            and (rq.get_field('856').get_subfield('u').is_exist()
                 or rq.get_field('330').get_subfield('u').is_exist())
    ):
        _add_to_values(values, 'e_resources')

    if 'm' in f105_a_pos_4_7:
        _add_to_values(values, 'dissertation_abstracts')

    if 'd' in f105_a_pos_4_7:
        _add_to_values(values, 'referats')

    if 'j' in f105_a_pos_4_7:
        _add_to_values(values, 'textbook')

    if leader7 == 'm' and 'k' in f105_a_pos_4_7:
        _add_to_values(values, 'patents')

    if leader7 == 'm' and 'l' in f105_a_pos_4_7:
        _add_to_values(values, 'standarts')

    if leader7 == 's' and 'l' in f105_a_pos_4_7:
        _add_to_values(values, 'legislative_acts')

    if leader7 == 'm' and 'p' in f105_a_pos_4_7:
        _add_to_values(values, 'technical_reports')

    if 'g' in f105_a_pos_4_7:
        _add_to_values(values, 'references')

    if 'e' in f105_a_pos_4_7:
        _add_to_values(values, 'dictionaries')

    if 'f' in f105_a_pos_4_7:
        _add_to_values(values, 'encyclopedias')

    return values

def owner(rq):
    values = []
    if record.source.code in ['ekbson', 'gpntb']:
        return values
    
    for fq in rq.get_field('850').list():
        for sfq in fq.get_subfield('a').list():
            _add_to_values(values, sfq.get_data())
    return values


def parent_record_number(rq):
    values = []
    for fq in _get_each_filed_query(rq, '4'):
        _add_to_values(values, fq.get_field('001').get_data())
    return values


def place_publication(rq):
    values = []
    for fq in rq.get_field('210').list():
        for sfq in fq.get_subfield('a').list():
            _add_to_values(values, sfq.get_data())

    for fq in rq.get_field('620').list():
        for sfq in fq.get_subfield('a').list():
            _add_to_values(values, sfq.get_data())

        for sfq in fq.get_subfield('b').list():
            _add_to_values(values, sfq.get_data())

        for sfq in fq.get_subfield('c').list():
            _add_to_values(values, sfq.get_data())

        for sfq in fq.get_subfield('d').list():
            _add_to_values(values, sfq.get_data())

    return values


def previose_local_number(rq):
    values = []
    for fq in rq.get_field('035').list():
        for sfq in fq.get_subfield('a').list():
            _add_to_values(values, sfq.get_data())
    return values


def publisher(rq):
    values = []
    for fq in rq.get_field('210').list():
        for sfq in fq.get_subfield('c').list():
            _add_to_values(values, sfq.get_data())
    
    for fq in _get_each_filed_query(rq, '4'):
         for ifq in fq.get_field('210').list():
            _add_to_values(values, ifq.get_subfield('c').get_data())
    return values


def record_type(rq):
    return rq.leader_data()[6:7] or '';


def subject_heading(rq):
    values = []
    for fq in rq.get_field('606').list():
        for sfq in fq.get_subfield('a').list():
            _add_to_values(values, sfq.get_data())

    for fq in _get_each_filed_query(rq, '4'):
        for inner_fq in fq.get_field('606').list():
            _add_to_values(values, inner_fq.get_subfield('a').get_data())

    return values;


def subject_keywords(rq):
    values = []
    for fq in rq.get_field('610').list():
        for sfq in fq.get_subfield('a').list():
            _add_to_values(values, sfq.get_data())

    for fq in _get_each_filed_query(rq, '4'):
        for inner_fq in fq.get_field('610').list():
            _add_to_values(values, inner_fq.get_subfield('a').get_data())

    return values;


def subject_subheading(rq):
    values = []
    for fq in rq.get_field('606').list():
        for sfq in fq.get_subfield('x').list():
            _add_to_values(values, sfq.get_data())

    for fq in _get_each_filed_query(rq, '4'):
        for inner_fq in fq.get_field('606').list():
            _add_to_values(values, inner_fq.get_subfield('x').get_data())

    return values;


def _extract_200_title(fq):
    values = []
    for sfq in fq.get_subfield('a').list():
        _add_to_non_empty_values(values, '; ');
        _add_to_values(values, sfq.get_data().strip())

    #title_part = fq.get_subfield('b').get_data().strip();
    #if title_part:
    #    values.append((' [' + title_part + ']')

    title_part = fq.get_subfield('e').get_data().strip();
    if title_part:
        values.append(': ' + title_part)

    #title_part = fq.get_subfield('f').get_data().strip();
    #if title_part:
    #    values.append(' / ' + title_part)

    title_part = fq.get_subfield('g').get_data().strip();
    if title_part:
        values.append('; ' + title_part)

    title_part = fq.get_subfield('v').get_data().strip();
    if title_part:
        values.append('. ' + title_part)


    if len(values) == 0:
        return ''

    return ''.join(values).strip()


def title(rq):
    title = []
    _add_to_values(title, _extract_200_title(rq.get_field('200')))
    #// var title461 = _extract200Title(rq.getField('461').getInnerField('200'));
    #// var title463 = _extract200Title(rq.getField('463').getInnerField('200'));
    #// if (title463) {
    #//     addToValues(title, title200);
    #//     addToNonEmptyValues(title, ' // ');
    #//     addToValues(title, title461);
    #//     addToNonEmptyValues(title, '. – ');
    #//     addToValues(title, title463);
    #// } else if (title461) {
    #//     addToValues(title, title461);
    #//     addToNonEmptyValues(title, '. – ');
    #//     addToValues(title, title200);
    #// } else {
    #//     addToValues(title, title200);
    #// }

    for fq in _get_each_filed_query(rq, '4'):
        _add_to_values(title, _extract_200_title(fq.get_field('200')))
         
    for fq in _get_each_filed_query(rq, '5'):
        _add_to_values(title, _get_each_subfield_data(fq.get_subfield('a')));
        _add_to_values(title, _get_each_subfield_data(fq.get_subfield('h')));
        _add_to_values(title, _get_each_subfield_data(fq.get_subfield('i')));

    return ' '.join(title)


def title_series(rq):
    
    values = []

    def _title_series(fq):
        for sfq in fq.get_subfield('i').list():
            _add_to_values(values, sfq.get_data())

    for fq in rq.get_field('225').list():
        _title_series(fq)

    for fq4 in _get_each_filed_query(rq, '4'):
        _title_series(fq4.get_field('225'))

    return values


def title_source(rq):
    values = []
    for fq in _get_each_filed_query(rq, '4'):
        _add_to_values(values, _extract_200_title(fq.get_field('200')))
    return values


def udc(rq):
    values = []
    for fq in rq.get_field('686').list():
        sfa = fq.get_subfield('a').get_data()
        sf2 = fq.get_subfield('2').get_data()
        if sf2 == 'udc':
            _add_to_values(values, sfa)
    return values


# local specific attrs

def attributes(rq):
    values = []
    for f856q in rq.get_field('856').list():
        sf_y = f856q.get_subfield('y').get_data()
        sf_z = f856q.get_subfield('z').get_data()
        if not sf_y:
            continue

        if 'Полный текст' in sf_z:
            values.append('have_ft')
        elif 'Содержание' in sf_z:
            values.append('have_content')
        elif 'Видео' in sf_z:
            values.append('have_video')
        elif 'Аудио' in sf_z:
            values.append('have_audio')
    
    if rq.get_field('998').get_subfield('a').get_data() == 'РП':
        values.append('repository')

    return values


def catalog(rq):
    values = []
    for sfq in rq.get_field('966').get_subfield('a').list():
        sf_d = sfq.get_data()
        if sf_d == 'MAGR':
            _add_to_values(values, 'MAG_R')
        elif sf_d == 'MAGF':
            _add_to_values(values, 'MAG_F')
        else:
            _add_to_values(values, sf_d)

    return values


def collection(rq):
    values = []
    _add_to_values(values, rq.get_field('908').get_subfield('a').get_data())
    return values


def date_time_added_to_db(rq):
    values = []
    _add_to_values(values, rq.get_field('100').get_subfield('a').get_data()[0:7])
    return values


def date_time_of_income(rq):
    values = []
    _add_to_values(values, rq.get_field('801').get_subfield('c').get_data())
    return values


def dfs_date_of_publication(rq):
    values = []
    if rq.get_field('966').get_subfield('a').get_data() == 'DFS':
        _add_to_values(values, rq.get_field('200').get_subfield('e').get_data())
    return values


def dfs_document_type(rq):
    values = []
    if rq.get_field('966').get_subfield('a').get_data() == 'DFS':
        _add_to_values(values, rq.get_field('200').get_subfield('d').get_data())
    return values


def dfs_organisation(rq):
    values = []
    if rq.get_field('966').get_subfield('a').get_data() == 'DFS':
        _add_to_values(values, rq.get_field('200').get_subfield('f').get_data())
    return values


def e_version_type(rq):
    values = []
    for f856q in rq.get_field('856').list():
        _add_to_values(values, f856q.get_subfield('z').get_data())
    return values


def linked_record_number(rq):
    values = []
    _add_to_values(values, rq.get_field('461').get_field('001').get_data())
    return values


def sic_collection(rq):
    values = []
    for f910q in rq.get_field('910').list():
        _add_to_values(values, f910q.get_subfield('q').get_data())
    return values


def shifr_izd(rq):
    values = []
    for f850q in rq.get_field('850').list():
        _add_to_values(values, f850q.get_subfield('c').get_data())
    _add_to_values(values, rq.get_field('903').get_subfield('a').get_data())
    return values


attrs = {
    'annotation': annotation(rq),
    'author': author(rq),
    'author_name_corporate': author_name_corporate(rq),
    'bbk': bbk(rq),
    'bib_level': bib_level(rq),
    'code_language': code_language(rq),
    'content_text': content_text(rq),
    'content_type': content_type(rq),
    'content_notes': content_notes(rq),
    'date_of_publication': date_of_publication(rq),
    'date_of_publication_of_original': date_of_publication_of_original(rq),
    'grnti': grnti(rq),
    'isbn': isbn(rq),
    'issn': issn(rq),
    'full_text': full_text(rq),
    'local_number': local_number(rq),
    'notes': notes(rq),
    'material_type': material_type(rq),
    'owner': owner(rq),
    'parent_record_number': parent_record_number(rq),
    'place_publication': place_publication(rq),
    'previose_local_number': previose_local_number(rq),
    'publisher': publisher(rq),
    'record_type': record_type(rq),
    'subject_heading': subject_heading(rq),
    'subject_keywords': subject_keywords(rq),
    'subject_subheading': subject_subheading(rq),
    'title': title(rq),
    'title_source': title_source(rq),
    'udc': udc(rq),
    # local specific attrs
    'attributes': attributes(rq),
    'catalog': catalog(rq),
    'collection': collection(rq),
    'date_time_added_to_db': date_time_added_to_db(rq),
    'date_time_of_income': date_time_of_income(rq),
    'dfs_date_of_publication': dfs_date_of_publication(rq),
    'dfs_document_type': dfs_document_type(rq),
    'dfs_organisation': dfs_organisation(rq),
    'e_version_type': e_version_type(rq),
    'linked_record_number': linked_record_number(rq),
    'shifr_izd': shifr_izd(rq),
    'sic_collection': sic_collection(rq),
}


index_document.add_field('annotation', attrs['annotation']).as_text()
index_document.add_field('author', attrs['author']).as_text()
index_document.add_field('author', attrs['author']).as_string()
index_document.add_field('author', attrs['author']).as_string().sortable()
index_document.add_field('author_name_corporate', attrs['author_name_corporate']).as_text()
index_document.add_field('bbk', attrs['bbk']).as_string()
index_document.add_field('bib_level', attrs['bib_level']).as_string()
index_document.add_field('code_language', attrs['code_language']).as_string()
index_document.add_field('content_notes', attrs['content_notes']).as_text()
index_document.add_field('content_text', attrs['content_text']).as_text('ru')
index_document.add_field('date_of_publication', attrs['date_of_publication']).as_string()
index_document.add_field('date_of_publication', attrs['date_of_publication']).as_datetime()
index_document.add_field('date_of_publication', attrs['date_of_publication']).as_integer()
index_document.add_field('date_of_publication_of_original', attrs['date_of_publication_of_original']).as_string()
index_document.add_field('grnti', attrs['grnti']).as_string()
index_document.add_field('isbn', attrs['isbn']).as_string()
index_document.add_field('issn', attrs['issn']).as_string()
index_document.add_field('full_text', attrs['full_text']).as_text('ru')
index_document.add_field('local_number', attrs['local_number']).as_string()
index_document.add_field('notes', attrs['notes']).as_text()
index_document.add_field('material_type', attrs['material_type']).as_string()
index_document.add_field('owner', attrs['owner']).as_string()
index_document.add_field('parent_record_number', attrs['parent_record_number']).as_string()
index_document.add_field('place_publication', attrs['place_publication']).as_text()
index_document.add_field('previose_local_number', attrs['previose_local_number']).as_string()
index_document.add_field('publisher', attrs['publisher']).as_text()
index_document.add_field('record_type', attrs['record_type']).as_string()
index_document.add_field('subject_heading', attrs['subject_heading']).as_text()
index_document.add_field('subject_keywords', attrs['subject_keywords']).as_text()
index_document.add_field('subject_subheading', attrs['subject_subheading']).as_text()
index_document.add_field('title', attrs['title']).as_text()
index_document.add_field('title', attrs['title']).as_string().sortable()
index_document.add_field('title_source', attrs['title_source']).as_text()
index_document.add_field('udc', attrs['udc']).as_string()

# local specific attrs
index_document.add_field('attributes', attrs['attributes']).as_string()
index_document.add_field('catalog', attrs['catalog']).as_string()
index_document.add_field('collection', attrs['collection']).as_string()
index_document.add_field('date_time_added_to_db', attrs['date_time_added_to_db']).as_datetime()
index_document.add_field('date_time_added_to_db', attrs['date_time_added_to_db']).as_datetime().sortable()
index_document.add_field('date_time_of_income', attrs['date_time_of_income']).as_string()
index_document.add_field('date_time_of_income', attrs['date_time_of_income']).as_datetime()
index_document.add_field('date_time_of_income', attrs['date_time_of_income']).as_datetime().sortable()
index_document.add_field('dfs_date_of_publication', attrs['dfs_date_of_publication']).as_string()
index_document.add_field('dfs_date_of_publication', attrs['dfs_date_of_publication']).as_integer()
index_document.add_field('dfs_date_of_publication', attrs['dfs_date_of_publication']).as_datetime().sortable()
index_document.add_field('dfs_document_type', attrs['dfs_document_type']).as_string()
index_document.add_field('dfs_organisation', attrs['dfs_organisation']).as_string()
index_document.add_field('e_version_type', attrs['e_version_type']).as_string()
index_document.add_field('linked_record_number', attrs['linked_record_number']).as_string()
index_document.add_field('shifr_izd', attrs['shifr_izd']).as_string()
index_document.add_field('sic_collection', attrs['sic_collection']).as_string()
index_document.add_field('subject_heading', attrs['subject_heading']).as_string()
index_document.add_field('subject_keywords', attrs['subject_keywords']).as_string()

all_t = [
    attrs['title'], 
    attrs['title_source'],
    attrs['author'],
    attrs['subject_heading'],
    attrs['subject_keywords'],
    attrs['isbn'],
    attrs['issn'],
    attrs['date_of_publication'],
    attrs['dfs_date_of_publication'],
]

index_document.add_field('all', all_t).as_text()
index_document.add_field('all', all_t).as_text('ru')
"""

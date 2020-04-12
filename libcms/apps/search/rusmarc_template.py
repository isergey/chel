# encoding: utf-8
from datetime import datetime
from libcms.libs import junimarc


def get_income_date(record):
    income_date = None
    f801 = record['801']
    if f801:
        sf_c = f801[0]['c']
        if sf_c:
            income_date = sf_c[0].get_data()
    try:
        return datetime.strptime(income_date, '%Y%m%d')
    except:
        return None


def get_full_text_url(record):
    urls = []
    for f856 in record['856']:
        f856u = f856['y']
        f856z = f856['z']
        url = {
            'type': '',
            'href': '#',
            'title': '#'
        }
        if f856u:
            url['href'] = f856u[0].get_data()
            if f856z:
                url['title'] = f856z[0].get_data()
                url['type'] = url['title'].lower().strip()
            else:
                url['title'] = url['href']
        urls.append(url)
    return urls


def get_source_number(record):
    f461_001 = ''
    f463_001 = ''

    try:
        f461 = record['461']
        if f461:
            f461_1 = f461[0]['1']
            if f461_1:
                for sf_i in f461_1:
                    if isinstance(sf_i, junimarc.record.ExtendedSubfield):
                        f001 = sf_i['001']
                        if f001:
                            f461_001 = f001[0].get_data()
    except Exception as e:
        print('error of extraction 461/1/001')

    try:
        f463 = record['463']
        if f463:
            f463_1 = f463[0]['1']
            if f463_1:
                for sf_i in f463_1:
                    if isinstance(sf_i, junimarc.record.ExtendedSubfield):
                        f001 = sf_i['001']
                        if f001:
                            f463_001 = f001[0].get_data()
    except Exception as e:
        print('error of extraction 463/1/001')

    parent = ''
    main = ''
    if f461_001 and f463_001:
        parent = f463_001
        main = f461_001
    elif f461_001:
        parent = f461_001
    elif f463_001:
        main = f463_001
    return {
        'parent': parent,
        'main': main
    }


def get_title(record):
    def select_title():
        title = ''
        f200 = record['200']
        if f200:
            sf200_a = f200[0]['a']
            if sf200_a:
                title = sf200_a[0].get_data()

            sf200_e = f200[0]['e']
            if sf200_e:
                title += ': ' + sf200_e[0].get_data()

            sf200_h = f200[0]['h']
            if sf200_h:
                title += '. ' + sf200_h[0].get_data()

            sf200_v = f200[0]['v']
            if sf200_v:
                title += '. ' + sf200_v[0].get_data()
        return title

    def select_middle_title():
        middle_title = ''
        f463 = record['463']
        if f463:
            f463_1 = f463[0]['1']
            if f463_1:
                f200 = []
                for sf_i in f463_1:
                    if isinstance(sf_i, junimarc.record.ExtendedSubfield):
                        f200 = sf_i['200']
                    if f200: break
                if f200:
                    sf200_a = f200[0]['a']
                    if sf200_a:
                        middle_title = sf200_a[0].get_data()
        return middle_title

    def select_parent_title(title=''):
        parent_title = ''
        f461 = record['461']
        if f461:
            f461_1 = f461[0]['1']
            if f461_1:
                f200 = []
                for sf_i in f461_1:
                    f200 = sf_i['200']
                    if f200: break
                if f200:
                    sf200_a = f200[0]['a']
                    if sf200_a:
                        parent_title = sf200_a[0].get_data()
                    sf200_e = f200[0]['e']
                    if sf200_e:
                        parent_title += ": " + sf200_e[0].get_data()
                    sf200_v = f200[0]['v']
                    if sf200_v and sf200_v[0].get_data().replace(' ', '') != title.replace(' ', ''):
                        parent_title += " — " + sf200_v[0].get_data()
        return parent_title

    title = select_title()
    middle_title = select_middle_title()
    parent_title = select_parent_title(title)

    title_parts = []

    if parent_title:
        title_parts.append(parent_title)
    if middle_title:
        title_parts.append(middle_title)
    if title:
        title_parts.append(title)

    return __fuzzy_title(title_parts)


def doc_tree_to_dict(doc_tree):
    doc_dict = {}
    for element in doc_tree.getroot().getchildren():
        attrib = element.attrib['name']
        value = element.text
        # если поле пустое, пропускаем
        if not value: continue
        # value = beautify(value)
        values = doc_dict.get(attrib, None)
        if not values:
            doc_dict[attrib] = [value]
        else:
            values.append(value)
    return doc_dict


def beautify(libcard):
    replaces = [
        ('. :', '.:'),
        (', .', '. '),
        ('. .', '. '),
        ('.  .', '. '),
        ('— , ', '— '),
        ('.. ', '. '),
        ('..,', '.,'),
        ("..\n", ".\n"),
        ("..<", ".<"),
        ("..<", ".<"),
        (".</a>\n", ".</a>"),
        (".</p>\n", ".</p>"),
        (".</a>.", ".</a>"),
        (".</div>.", ".</div>"),
        (".<div class=\"links\">.", ".<div class=\"links\">"),
        (".</b>.", ".</b>"),
        (".</p>.", ".</p>"),
        (".</a><p></p>.", ".</a><p></p>"),
        (".</a></div>.", ".</a></div>"),
        ("%2B", "+"),
    ]

    r = libcard
    for replace in replaces:
        r = replace[1].join(r.split(replace[0]))
    return r


def __as_is(title_parts):
    out = {
        'title': ' // '.join(title_parts),
        'parts_of': ''
    }
    return out


def __title_and_parts(title_parts):
    out = {
        'title': title_parts[-1],
        'parts_of': ''
    }

    if len(title_parts) > 1:
        out['parts_of'] = ' — '.join(title_parts[:-1])
    return out


def __fuzzy_title(title_parts):
    min_main_title_length = 10
    max_title_length = 1000
    out = {
        'title': '',
        'parts_of': ''
    }

    if len(title_parts) == 1:
        return __title_and_parts(title_parts)

    title_length = len(title_parts[-1])
    parents_length = len(''.join(title_parts[:-1]))

    if parents_length + title_length > max_title_length:
        return __title_and_parts(title_parts)

    if title_length <= min_main_title_length:
        out['title'] = ' // '.join(title_parts[:-1]) + ' — ' + title_parts[-1]
        out['parts_of'] = title_parts[0]
        return out

    return __title_and_parts(title_parts)

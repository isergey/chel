def subject_render(record_dict):
    try:
        rows = []
        for field in record_dict['df']:
            if field['id'] in ('606', '607', '608'):
                row = []
                for subfield in field['sf']:
                    if subfield['id'] in ('a', 'x', 'y', 'z'):
                        print subfield['d']
                        row.append(subfield['d'])
                rows.append(row)
    except KeyError:
        return None
    return rows

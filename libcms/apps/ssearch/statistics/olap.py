def _collections_to_olap(collections):
    rows = []

    for level_1, collection_data in list(collections.items()):
        children = collection_data.get('children')
        if children:
            for level_2, collection_data in list(children.items()):
                children = collection_data.get('children')
                if children:
                    for level_3, collection_data in list(children.items()):
                        children = collection_data.get('children')
                        if children:
                            for level_4, collection_data in list(children.items()):
                                for date, amount in list(collection_data['create_dates'].items()):
                                    rows.append({
                                        'level_1': level_1,
                                        'level_2': level_2,
                                        'level_3': level_3,
                                        'level_4': level_4,
                                        'date': date,
                                        'amount': amount
                                    })
                        else:
                            for date, amount in list(collection_data['create_dates'].items()):
                                rows.append({
                                    'level_1': level_1,
                                    'level_2': level_2,
                                    'level_3': level_3,
                                    'date': date,
                                    'amount': amount
                                })
                else:
                    for date, amount in list(collection_data['create_dates'].items()):
                        rows.append({
                            'level_1': level_1,
                            'level_2': level_2,
                            'date': date,
                            'amount': amount
                        })
        else:
            for date, amount in list(collection_data['create_dates'].items()):
                rows.append({
                    'level_1': level_1,
                    'date': date,
                    'amount': amount
                })

    return rows


def _collections_to_actions_olap(collections):
    rows = []

    for level_1, collection_data in list(collections.items()):
        children = collection_data.get('children')
        if children:
            for level_2, collection_data in list(children.items()):
                children = collection_data.get('children')
                if children:
                    for level_3, collection_data in list(children.items()):
                        children = collection_data.get('children')
                        if children:
                            for level_4, collection_data in list(children.items()):
                                for date, date_data in list(collection_data['actions_by_date'].items()):
                                    params = {
                                        'level_1': level_1,
                                        'level_2': level_2,
                                        'level_3': level_3,
                                        'level_4': level_4,
                                        'date': date,

                                    }
                                    for action, amount in list(date_data.items()):
                                        params['action_' + str(action)] = amount
                                    rows.append(params)
                        else:
                            for date, date_data in list(collection_data['actions_by_date'].items()):
                                params = {
                                    'level_1': level_1,
                                    'level_2': level_2,
                                    'level_3': level_3,
                                    'date': date,

                                }
                                for action, amount in list(date_data.items()):
                                    params['action_' + str(action)] = amount
                                rows.append(params)
                else:
                    for date, date_data in list(collection_data['actions_by_date'].items()):
                        params = {
                            'level_1': level_1,
                            'level_2': level_2,
                            'date': date,

                        }
                        for action, amount in list(date_data.items()):
                            params['action_' + str(action)] = amount
                        rows.append(params)
        else:
            for date, date_data in list(collection_data['actions_by_date'].items()):
                params = {
                    'level_1': level_1,
                    'date': date,

                }
                for action, amount in list(date_data.items()):
                    params['action_' + str(action)] = amount
                rows.append(params)

    return rows


def _collections_to_users_olap(collections):
    rows = []

    for level_1, collection_data in list(collections.items()):
        children = collection_data.get('children')
        if children:
            for level_2, collection_data in list(children.items()):
                children = collection_data.get('children')
                if children:
                    for level_3, collection_data in list(children.items()):
                        children = collection_data.get('children')
                        if children:
                            for level_4, collection_data in list(children.items()):
                                for date, date_data in list(collection_data['sessions_by_date'].items()):
                                    users = len(list(date_data.keys()))
                                    visits = 0
                                    for value in list(date_data.values()):
                                        visits += value

                                    rows.append({
                                        'level_1': level_1,
                                        'level_2': level_2,
                                        'level_3': level_3,
                                        'level_4': level_4,
                                        'date': date,
                                        'users': users,
                                        'visits': visits
                                    })

                        else:
                            for date, date_data in list(collection_data['sessions_by_date'].items()):
                                users = len(list(date_data.keys()))
                                visits = 0
                                for value in list(date_data.values()):
                                    visits += value

                                rows.append({
                                    'level_1': level_1,
                                    'level_2': level_2,
                                    'level_3': level_3,
                                    'date': date,
                                    'users': users,
                                    'visits': visits
                                })
                else:
                    for date, date_data in list(collection_data['sessions_by_date'].items()):
                        users = len(list(date_data.keys()))
                        visits = 0
                        for value in list(date_data.values()):
                            visits += value

                        rows.append({
                            'level_1': level_1,
                            'level_2': level_2,
                            'date': date,
                            'users': users,
                            'visits': visits
                        })
        else:
            for date, date_data in list(collection_data['sessions_by_date'].items()):
                users = len(list(date_data.keys()))
                visits = 0
                for value in list(date_data.values()):
                    visits += value

                rows.append({
                    'level_1': level_1,
                    'date': date,
                    'users': users,
                    'visits': visits
                })

    return rows


def _collections_to_doc_types_olap(collections):
    rows = []

    for level_1, collection_data in list(collections.items()):
        children = collection_data.get('children')
        if children:
            for level_2, collection_data in list(children.items()):
                children = collection_data.get('children')
                if children:
                    for level_3, collection_data in list(children.items()):
                        children = collection_data.get('children')
                        if children:
                            for level_4, collection_data in list(children.items()):
                                for date, date_data in list(collection_data['doc_types_by_date'].items()):
                                    for doc_type, amount in list(date_data.items()):
                                        rows.append({
                                            'level_1': level_1,
                                            'level_2': level_2,
                                            'level_3': level_3,
                                            'level_4': level_4,
                                            'date': date,
                                            'doc_type': doc_type,
                                            'amount': amount,
                                        })
                        else:
                            for date, date_data in list(collection_data['doc_types_by_date'].items()):
                                for doc_type, amount in list(date_data.items()):
                                    rows.append({
                                        'level_1': level_1,
                                        'level_2': level_2,
                                        'level_3': level_3,
                                        'date': date,
                                        'doc_type': doc_type,
                                        'amount': amount,
                                    })
                else:
                    for date, date_data in list(collection_data['doc_types_by_date'].items()):
                        for doc_type, amount in list(date_data.items()):
                            rows.append({
                                'level_1': level_1,
                                'level_2': level_2,
                                'date': date,
                                'doc_type': doc_type,
                                'amount': amount,
                            })
        else:
            for date, date_data in list(collection_data['doc_types_by_date'].items()):
                for doc_type, amount in list(date_data.items()):
                    rows.append({
                        'level_1': level_1,
                        'date': date,
                        'doc_type': doc_type,
                        'amount': amount,
                    })

    return rows

def _collections_to_content_types_olap(collections):
    rows = []

    for level_1, collection_data in list(collections.items()):
        children = collection_data.get('children')
        if children:
            for level_2, collection_data in list(children.items()):
                children = collection_data.get('children')
                if children:
                    for level_3, collection_data in list(children.items()):
                        children = collection_data.get('children')
                        if children:
                            for level_4, collection_data in list(children.items()):
                                for date, date_data in list(collection_data['content_types_by_date'].items()):
                                    for content_type, amount in list(date_data.items()):
                                        rows.append({
                                            'level_1': level_1,
                                            'level_2': level_2,
                                            'level_3': level_3,
                                            'level_4': level_4,
                                            'date': date,
                                            'content_type': content_type,
                                            'amount': amount,
                                        })
                        else:
                            for date, date_data in list(collection_data['content_types_by_date'].items()):
                                for content_type, amount in list(date_data.items()):
                                    rows.append({
                                        'level_1': level_1,
                                        'level_2': level_2,
                                        'level_3': level_3,
                                        'date': date,
                                        'content_type': content_type,
                                        'amount': amount,
                                    })
                else:
                    for date, date_data in list(collection_data['content_types_by_date'].items()):
                        for content_type, amount in list(date_data.items()):
                            rows.append({
                                'level_1': level_1,
                                'level_2': level_2,
                                'date': date,
                                'content_type': content_type,
                                'amount': amount,
                            })
        else:
            for date, date_data in list(collection_data['content_types_by_date'].items()):
                for content_type, amount in list(date_data.items()):
                    rows.append({
                        'level_1': level_1,
                        'date': date,
                        'content_type': content_type,
                        'amount': amount,
                    })

    return rows
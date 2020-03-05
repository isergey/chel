def _collections_to_olap(collections):
    rows = []

    for level_1, collection_data in collections.items():
        children = collection_data.get('children')
        if children:
            for level_2, collection_data in children.items():
                children = collection_data.get('children')
                if children:
                    for level_3, collection_data in children.items():
                        children = collection_data.get('children')
                        if children:
                            for level_4, collection_data in children.items():
                                for date, amount in collection_data['create_dates'].items():
                                    rows.append({
                                        'level_1': level_1,
                                        'level_2': level_2,
                                        'level_3': level_3,
                                        'level_4': level_4,
                                        'date': date,
                                        'amount': amount
                                    })
                        else:
                            for date, amount in collection_data['create_dates'].items():
                                rows.append({
                                    'level_1': level_1,
                                    'level_2': level_2,
                                    'level_3': level_3,
                                    'date': date,
                                    'amount': amount
                                })
                else:
                    for date, amount in collection_data['create_dates'].items():
                        rows.append({
                            'level_1': level_1,
                            'level_2': level_2,
                            'date': date,
                            'amount': amount
                        })
        else:
            for date, amount in collection_data['create_dates'].items():
                rows.append({
                    'level_1': level_1,
                    'date': date,
                    'amount': amount
                })

    return rows


def _collections_to_actions_olap(collections):
    rows = []

    for level_1, collection_data in collections.items():
        children = collection_data.get('children')
        if children:
            for level_2, collection_data in children.items():
                children = collection_data.get('children')
                if children:
                    for level_3, collection_data in children.items():
                        children = collection_data.get('children')
                        if children:
                            for level_4, collection_data in children.items():
                                for date, date_data in collection_data['actions_by_date'].items():
                                    params = {
                                        'level_1': level_1,
                                        'level_2': level_2,
                                        'level_3': level_3,
                                        'level_4': level_4,
                                        'date': date,

                                    }
                                    for action, amount in date_data.items():
                                        params['action_' + str(action)] = amount
                                    rows.append(params)
                        else:
                            for date, date_data in collection_data['actions_by_date'].items():
                                params = {
                                    'level_1': level_1,
                                    'level_2': level_2,
                                    'level_3': level_3,
                                    'date': date,

                                }
                                for action, amount in date_data.items():
                                    params['action_' + str(action)] = amount
                                rows.append(params)
                else:
                    for date, date_data in collection_data['actions_by_date'].items():
                        params = {
                            'level_1': level_1,
                            'level_2': level_2,
                            'date': date,

                        }
                        for action, amount in date_data.items():
                            params['action_' + str(action)] = amount
                        rows.append(params)
        else:
            for date, date_data in collection_data['actions_by_date'].items():
                params = {
                    'level_1': level_1,
                    'date': date,

                }
                for action, amount in date_data.items():
                    params['action_' + str(action)] = amount
                rows.append(params)

    return rows


def _collections_to_users_olap(collections):
    rows = []

    for level_1, collection_data in collections.items():
        children = collection_data.get('children')
        if children:
            for level_2, collection_data in children.items():
                children = collection_data.get('children')
                if children:
                    for level_3, collection_data in children.items():
                        children = collection_data.get('children')
                        if children:
                            for level_4, collection_data in children.items():
                                for date, date_data in collection_data['sessions_by_date'].items():
                                    users = len(date_data.keys())
                                    visits = 0
                                    for value in date_data.values():
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
                            for date, date_data in collection_data['sessions_by_date'].items():
                                users = len(date_data.keys())
                                visits = 0
                                for value in date_data.values():
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
                    for date, date_data in collection_data['sessions_by_date'].items():
                        users = len(date_data.keys())
                        visits = 0
                        for value in date_data.values():
                            visits += value

                        rows.append({
                            'level_1': level_1,
                            'level_2': level_2,
                            'date': date,
                            'users': users,
                            'visits': visits
                        })
        else:
            for date, date_data in collection_data['sessions_by_date'].items():
                users = len(date_data.keys())
                visits = 0
                for value in date_data.values():
                    visits += value

                rows.append({
                    'level_1': level_1,
                    'date': date,
                    'users': users,
                    'visits': visits
                })

    return rows


def _collections_to_material_types_olap(collections):
    rows = []

    for level_1, collection_data in collections.items():
        children = collection_data.get('children')
        if children:
            for level_2, collection_data in children.items():
                children = collection_data.get('children')
                if children:
                    for level_3, collection_data in children.items():
                        children = collection_data.get('children')
                        if children:
                            for level_4, collection_data in children.items():
                                for date, date_data in collection_data['material_types_by_date'].items():
                                    for material_type, amount in date_data.items():
                                        rows.append({
                                            'level_1': level_1,
                                            'level_2': level_2,
                                            'level_3': level_3,
                                            'level_4': level_4,
                                            'date': date,
                                            'material_type': material_type,
                                            'amount': amount,
                                        })
                        else:
                            for date, date_data in collection_data['material_types_by_date'].items():
                                for material_type, amount in date_data.items():
                                    rows.append({
                                        'level_1': level_1,
                                        'level_2': level_2,
                                        'level_3': level_3,
                                        'date': date,
                                        'material_type': material_type,
                                        'amount': amount,
                                    })
                else:
                    for date, date_data in collection_data['material_types_by_date'].items():
                        for material_type, amount in date_data.items():
                            rows.append({
                                'level_1': level_1,
                                'level_2': level_2,
                                'date': date,
                                'material_type': material_type,
                                'amount': amount,
                            })
        else:
            for date, date_data in collection_data['material_types_by_date'].items():
                for material_type, amount in date_data.items():
                    rows.append({
                        'level_1': level_1,
                        'date': date,
                        'material_type': material_type,
                        'amount': amount,
                    })

    return rows

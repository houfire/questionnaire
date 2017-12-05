from app01 import models


def init_permission(request, user):
    data_list = user.roles.values('permissions__id', 'permissions__title', 'permissions__url', 'permissions__code',
                                  'permissions__menu_ref_id', 'permissions__group_id',
                                  'permissions__group__menu_id', 'permissions__group__menu__title').distinct()

    '''首页展示所有权限'''
    per_index = []
    for dict_item in data_list:
        url_title = dict_item.get('permissions__title')
        if not (url_title in ['主页', '注销']):
            tmp_dict = {
                'url_title': url_title,
                'url': dict_item.get('permissions__url')
            }

            per_index.append(tmp_dict)

    request.session['per_index'] = per_index

    '''权限匹配'''
    per_info_dict = {}
    for dict_item in data_list:
        group_id = dict_item.get('permissions__group_id')
        if not (group_id in per_info_dict):
            per_info_dict[group_id] = {
                'urls_info': [{'url_title': dict_item.get('permissions__title'),
                               'url': dict_item.get('permissions__url')}],
                'codes': [dict_item.get('permissions__code')]
            }
        else:
            per_info_dict[group_id]['urls_info'].append({'url_title': dict_item.get('permissions__title'),
                                                         'url': dict_item.get('permissions__url')})
            per_info_dict[group_id]['codes'].append(dict_item.get('permissions__code'))

    request.session['per_info_dict'] = per_info_dict

    '''菜单展示'''
    per_side_list = []
    for dict_item in data_list:
        tmp_dict = {
            'url_id': dict_item.get('permissions__id'),
            'url_title': dict_item.get('permissions__title'),
            'url': dict_item.get('permissions__url'),
            'menu_ref': dict_item.get('permissions__menu_ref_id'),
            'menu_id': dict_item.get('permissions__group__menu_id'),
            'menu_title': dict_item.get('permissions__group__menu__title')
        }
        per_side_list.append(tmp_dict)

    request.session['per_side_list'] = per_side_list

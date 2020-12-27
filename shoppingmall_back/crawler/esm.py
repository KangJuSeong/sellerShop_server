import json
import re

import requests
from django.utils import timezone


def _get_cookie(_id, _pw, is_esm=False, is_auction=False, is_gmarket=False):
    if not is_esm and not is_auction and not is_gmarket:
        return ''

    url = 'https://www.esmplus.com/Member/SignIn/Authenticate'
    data = {
        'Password': _pw,
        'Type': 'E' if is_esm else 'S',
        'ReturnUrl': '',
        'Id': _id,
        'RememberMe': 'false'
    }
    if is_auction:
        data['SiteType'] = 'IAC'
    if is_gmarket:
        data['SiteType'] = 'GMKT'
    resp = requests.post(url, data=data)

    results = []
    for cookie in list(resp.history[-1].cookies):
        results.append('%s=%s;' % (cookie.name, cookie.value))

    return ' '.join(results).strip()


def get_auction_cookie(_id, _pw):
    return _get_cookie(_id, _pw, is_auction=True)


def get_gmarket_cookie(_id, _pw):
    return _get_cookie(_id, _pw, is_gmarket=True)


def get_esm_cookie(_id, _pw):
    return _get_cookie(_id, _pw, is_esm=True)


def get_cookie_method(shop):
    return {3: get_auction_cookie, 4: get_gmarket_cookie, 5: get_esm_cookie}[shop]


def get_api_response(url, data, account_info):
    headers = {
        'cache-control': 'no-cache',
        'cookie': account_info.session
    }
    fail_count = 0
    while True:
        if fail_count >= 5:
            break

        try:
            resp = requests.post(url, data, headers=headers)
            return resp.json()
        except json.decoder.JSONDecodeError:
            cookie = get_cookie_method(account_info.shop)(account_info._login_id, account_info._login_pw)
            headers['cookie'] = cookie

            fail_count += 1

            account_info.session = cookie
            account_info.save()
            continue
    return None


def get_default_data(start_date, end_date, search_account, site_number, search_date_type, search_all=False, extra_data={}):
    data = {
        'page': '1',
        'limit': '500',
        'siteGbn': site_number,
        'searchAccount': search_account,
        'searchDateType': search_date_type,
        'searchSDT': start_date,
        'searchEDT': end_date,
        'searchKey': 'ON',
        'searchKeyword': '',
        'searchDistrType': 'AL',
        'searchAllYn': 'Y' if search_all else 'N',
        'SortFeild': 'PayDate',
        'SortType': 'Desc',
        'start': '0',
        'searchTransPolicyType': ''
    }
    if extra_data:
        data.update(extra_data)
    return data


def get_today_order(account_info, date_string):
    url = 'https://www.esmplus.com/Escrow/Order/NewOrderSearch'
    search_date_type = 'ODD' if account_info.shop <= 3 else 'DCD'
    site_number = 1 if account_info.shop <= 3 else 0
    data = get_default_data(date_string, date_string, account_info.extra_data, site_number, search_date_type)
    resp = get_api_response(url, data, account_info)
    if resp:
        return resp
    return {'total': 0, 'data': []}


def get_today_checked_order(account_info, date_string):
    url = 'https://www.esmplus.com/Escrow/Delivery/GeneralDeliverySearch'
    extra_data = {
        'excelInfo': '', 'searchStatus': 0, 'searchOrderType': '', 'searchDeliveryType': '', 'searchPaking': 'false'
    }
    search_date_type = 'ODD' if account_info.shop <= 3 else 'DCD'
    data = get_default_data(
        date_string, date_string, account_info.extra_data, 0, search_date_type, search_all=True, extra_data=extra_data
    )
    resp = get_api_response(url, data, account_info)
    if resp:
        return resp
    return {'total': 0, 'data': []}


def get_today_shipped(account_info, date_string):
    url = 'https://www.esmplus.com/Escrow/Delivery/GetSendingSearch'
    extra_data = {
        'searchType': 0, 'excelInfo': '', 'searchStatus': 0,
    }
    search_date_type = 'ODD' if account_info.shop <= 3 else 'DCD'
    data = get_default_data(date_string, date_string, account_info.extra_data, 0, search_date_type, extra_data=extra_data)
    resp = get_api_response(url, data, account_info)
    if resp:
        return resp
    return {'total': 0, 'data': []}


def get_esm_account_id(account_info):
    url = 'https://www.esmplus.com/Escrow/Order/NewOrder?menuCode=TDM105'
    headers = {
        'Cookie': account_info.session,
        'Host': 'www.esmplus.com',
        'Sec-Fetch-Mode': 'nested-navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Upgrade-Insecure-Requests': '1',
    }
    fail_count = 0
    while True:
        if fail_count >= 5:
            break

        try:
            html = requests.get(url, headers=headers).text.strip()
            return re.compile('var masterID = "(?P<number>\d+)";').search(html).group('number')
        except (json.decoder.JSONDecodeError, AttributeError):
            cookie = get_cookie_method(account_info.shop)(account_info._login_id, account_info._login_pw)
            headers['cookie'] = cookie

            fail_count += 1

            account_info.session = cookie
            account_info.save()
            continue
    return ''


def get_today_order_number(account_info):
    today = timezone.localdate().strftime('%Y-%m-%d')
    return {
        'total': get_today_order(account_info, today)['total'] + get_today_checked_order(account_info, today)['total'],
        'shipped': get_today_shipped(account_info, today)['total']
    }

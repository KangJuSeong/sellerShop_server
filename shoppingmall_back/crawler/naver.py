from json import JSONDecodeError

import requests
from django.utils import timezone


def get_today_order(account_info):
    if not account_info.session:
        account_info.session = get_nsi(account_info._login_id, account_info._login_pw)
        account_info.save()
    nsi = account_info._session

    headers = {
        'cache-control': 'no-cache',
        'cookie': 'NSI=%s' % nsi,
    }
    date = timezone.localdate().strftime('%Y.%m.%d')
    page = 1
    base_url = 'https://sell.smartstore.naver.com/o/manage/order/json'
    data = []
    fail_count = 0

    while True:
        if fail_count >= 5:
            break

        payload = {
            'range.type': 'PAY_COMPLETED',
            'range.fromDate': date,
            'range.toDate': date,
            'detailSearch.type': '',
            'paging.current': page,
            'paging.rowsPerPage': 100
        }
        req = requests.get(base_url, payload, headers=headers)
        try:
            result = req.json()['htReturnValue']['pagedResult']
        except JSONDecodeError:
            nsi = get_nsi(account_info._login_id, account_info._login_pw)
            headers['cookie'] = 'NSI=%s' % nsi
            fail_count += 1

            account_info.session = nsi
            account_info.save()
            continue

        data += result['content']
        if result['totalElements'] < 100:
            break
        page += 1

    return data


def get_today_order_number(account_info):
    shipped = 0
    orders = get_today_order(account_info)
    for order in orders:
        if order['PRODUCT_ORDER_DETAIL_PRODUCT_ORDER_STATUS'] == '배송중':
            shipped += 1
    return {'total': len(orders), 'shipped': shipped}


def get_nsi(_id, _pw):
    url = 'https://sell.smartstore.naver.com/api/login?url=https://sell.smartstore.naver.com/#'
    payload = {
        'captchaInput': "",
        'id': _id,
        'pw': _pw,
        'url': "https%3A%2F%2Fsell.smartstore.naver.com%2F%23"
    }

    headers = {
        'x-current-state': 'https://sell.smartstore.naver.com/#/login',
        'x-current-statename': 'login',
        'x-to-statename': 'login'
    }

    r = requests.post(url, json=payload, headers=headers)
    try:
        return r.cookies.values()[0]
    except IndexError:
        pass
    return ''


def is_valid_account(_id, _pw):
    if get_nsi(_id, _pw):
        return True
    return False

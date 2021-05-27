import requests
from django.utils import timezone
from bs4 import BeautifulSoup


def get_today_order_number(account_info):
    if not account_info.session:
        account_info.session = get_pdt(account_info._login_id, account_info._login_pw)
        account_info.save()

    pdt = account_info._session

    headers = {
        'cache-control': 'no-cache',
        'cookie': 'pdt-boecn=%s' % pdt,
    }
    date = timezone.localdate().strftime('%Y-%m-%d')
    url = 'https://wing.coupang.com/delivery/management/list'
    page = 1
    next_ship_id = 0
    shipped = 0
    total = 0
    fail_count = 0
    while True:
        if fail_count >= 5:
            break

        payload = {
            'from': date,
            'to': date,
            'page': page,
            'maxPage': page
        }
        if page > 1 and next_ship_id != 0:
            payload['nextShipmentBoxId'] = next_ship_id

        req = requests.get(url, payload, headers=headers)
        if req.status_code >= 400:
            pdt = get_pdt(account_info._login_id, account_info._login_pw)
            headers['cookie'] = 'pdt-boecn=%s' % pdt
            fail_count += 1

            account_info.session = pdt
            account_info.save()
            continue

        soup = BeautifulSoup(req.text.strip(), 'lxml')
        trs = soup.find_all('tr')
        if not trs:
            break
        next_ship_id = trs[-1]['class'][0][3:]

        for idx in range(0, len(trs), 2):
            customer_info = trs[idx]
            if '배송' in customer_info.find_all('td')[8]:
                shipped += 1
            # product_info = trs[idx+1]
            total += 1

        page += 1

    return {'total': total, 'shipped': shipped}


def get_pdt(_id, _pw):
    url = 'https://wing.coupang.com/login'
    payload = {'username': 'VENDOR,%s' % _id, 'password': '%s' % _pw}
    return requests.post(url, payload).cookies['pdt-boecn']


def is_valid_account(_id, _pw):
    if len(get_pdt(_id, _pw)) > 5:
        return True
    return False

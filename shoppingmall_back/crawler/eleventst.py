import json

import requests
from django.utils import timezone
from selenium import webdriver


def get_today_order(account_info):
    if not account_info.session:
        account_info.session = get_cookies(account_info._login_id, account_info._login_pw)
        account_info.save()

    cookie = account_info._session

    url = 'https://soffice.11st.co.kr/escrow/OrderingLogisticsAction.tmall'
    date = timezone.localdate().strftime('%Y%m%d')
    payload = {
        'method': 'getOrderLogisticsList',
        'listType': 'orderingLogistics',
        'start': '0',
        'limit': '500',
        'shDateType': '01',
        'shDateFrom': '20191212',
        'shDateTo': date,
        'shBuyerType': '',
        'shBuyerText': '',
        'shProductStat': 'ALL',
        'shDelayReport': '',
        'shPurchaseConfirm': '',
        'shGblDlv': 'N',
        'prdNo': '',
        'shStckNo': '',
        'shOrderType': 'on',
        'shToday': '',
        'shDelay': '',
        'addrSeq': '',
        'isAbrdSellerYn': '',
        'abrdOrdPrdStat': '',
        'isItalyAgencyYn': '',
        'shErrYN': '',
        'gblRcvrNm': '%EA%B8%80%EB%A1%9C%EB%B2%8C%ED%86%B5%ED%95%A9%EB%B0%B0%EC%86%A1%EC%A7%80',
        'gblRcvrMailNo': '17382',
        'gblRcvrBaseAddr': '%EA%B2%BD%EA%B8%B0%EB%8F%84%20%EC%9D%B4%EC%B2%9C%EC%8B%9C%20%EB%A7%88%EC%9E%A5%EB%A9%B4%20%EB%A7%88%EB%8F%84%EB%A1%9C%20177%20',
        'gblRcvrDtlsAddr': '%EA%B2%BD%EA%B8%B0%EB%8F%84%20%EC%9D%B4%EC%B2%9C%EC%8B%9C%20%EB%A7%88%EC%9E%A5%EB%A9%B4%20%EB%A7%88%EB%8F%84%EB%A1%9C%20177%20%204%EC%B8%B5%20%EC%A0%84%EC%84%B8%EA%B3%84%5BEMS%5D%EB%B0%B0%EC%86%A1%20%EB%8B%B4%EB%8B%B9%EC%9E%90',
        'gblRcvrTlphn': '1599-5115',
        'gblRcvrPrtblNo': '000-000-0000',
        'shOrdLang': '',
        'shDlvClfCd': '',
        'shVisitDlvYn': 'N',
        'shUsimDlvYn': 'N'
    }
    headers = {
        'cache-control': 'no-cache',
        'cookie': cookie
    }
    fail_count = 0
    while True:
        if fail_count >= 5:
            break

        try:
            return requests.post(url, payload, headers=headers).json()
        except json.decoder.JSONDecodeError:
            cookie = get_cookies(account_info._login_id, account_info._login_pw)
            headers['cookie'] = cookie

            fail_count += 1

            account_info.session = cookie
            account_info.save()
            continue

    return {'totalCount': 0, 'orderingLogistics': []}


def get_today_order_number(account_info):
    shipped = 0

    # 배송 상태
    # FR_ORD_PRD_STAT_NM: "Completed transaction"
    # FR_ORD_PRD_STAT_NM: "Preparing for shipment"
    # FR_ORD_PRD_STAT_NM: "Shipment in transit"
    # FR_ORD_PRD_STAT_NM: "Completed shipment"
    orders = get_today_order(account_info)
    for order in orders['orderingLogistics']:
        if order['FR_ORD_PRD_STAT_NM'] in ('Shipment in transit', 'Completed shipment'):
            shipped += 1
    return {'total': orders['totalCount'], 'shipped': shipped}


def get_cookies(_id, _pw):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")

    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
    )
    options.add_argument("lang=ko_KR")
    driver = webdriver.Chrome('./chromedriver', options=options)

    driver.get('https://login.11st.co.kr/auth/front/selleroffice/login.tmall?returnURL=http://soffice.11st.co.kr')
    driver.implicitly_wait(1.5)
    driver.find_element_by_id('user-id').send_keys(_id)
    driver.find_element_by_id('passWord').send_keys(_pw)
    driver.find_element_by_tag_name('button').click()
    driver.implicitly_wait(2)

    results = []
    for cookie in driver.get_cookies():
        results.append('%s=%s;' % (cookie['name'], cookie['value']))

    return ' '.join(results).strip()


def is_valid_account(_id, _pw):
    return 'TMALL_AUTH' in get_cookies(_id, _pw)

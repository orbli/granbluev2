import requests
import fs_configs
from http.cookies import SimpleCookie
from requests.cookies import *
from lxml import etree
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

TIMEOUT = (5, 30)  # (connect, read) seconds

session = None
xversion = None

def init():
    # lazy one-time setup: shared session with retries + X-VERSION scrape.
    # runs on the first get() call, never again.
    global session, xversion
    if session is not None:
        return

    s = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=frozenset(['GET', 'POST'])
    )
    s.mount('https://', HTTPAdapter(max_retries=retry))

    t = s.get("https://game.granbluefantasy.jp", timeout=TIMEOUT)
    tree = etree.HTML(t.text)
    txt = tree.xpath('/html/head/script[@id="server-props"]')[0].text
    j = json.loads(txt)
    xversion = j['version']
    print("X-VERSION: %s" % xversion)

    session = s

def get(url):
    init()

    scookie = SimpleCookie()
    scookie.load(fs_configs.cookie)
    cookiesdict = {}
    for key, morsel in scookie.items():
        cookiesdict[key] = morsel.value

    cookies = cookiejar_from_dict(cookiesdict)

    # cookie state lives in fs_configs.cookie, not in the session jar -
    # clear the jar so each request sends exactly the stored cookie
    session.cookies.clear()

    resp = session.get(
        "https://game.granbluefantasy.jp/%s%s" % (fs_configs.teamraid, url),
        headers={
            "X-VERSION": xversion,
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8,zh-TW;q=0.7,zh;q=0.6,zh-CN;q=0.5,ja;q=0.4",
            "User-Agent": fs_configs.useragent,
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": "https://game.granbluefantasy.jp/",
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive",
        },
        cookies=cookies,
        timeout=TIMEOUT
    )

    rt_cookie = {}
    for k, v in cookies.items():
        rt_cookie[k] = v
    for k, v in resp.cookies.items():
        rt_cookie[k] = v
    rt_cookie_txt = '; '.join("%s=%s" % (k, v) for k, v in rt_cookie.items())

    fs_configs.cookie = rt_cookie_txt

    try:
        data = json.loads(resp.text)
        if data.get('auth_status') == 'require_auth':
            raise ValueError('Authentication required: %s' % resp.text)
    except json.JSONDecodeError:
        pass

    return resp.text

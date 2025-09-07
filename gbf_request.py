import requests
import fs_configs
from http.cookies import SimpleCookie
from requests.cookies import *
from lxml import etree
import json

t = requests.get("https://game.granbluefantasy.jp")
tree = etree.HTML(t.text)
txt = tree.xpath('/html/head/script[@id="server-props"]')[0].text
j = json.loads(txt)
xversion = j['version']
print("X-VERSION: %s" % xversion)

def get(url):
    scookie = SimpleCookie()
    scookie.load(fs_configs.cookie)
    cookiesdict = {}
    for key, morsel in scookie.items():
        cookiesdict[key] = morsel.value

    cookies = cookiejar_from_dict(cookiesdict)

    resp = requests.get(
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
        cookies=cookies
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
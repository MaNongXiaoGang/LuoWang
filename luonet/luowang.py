# coding=utf-8
# !/usr/bin python
'''

Author: lifenggang
        ZsLfg
Python3 环境
Email: 15116211002@163.com
'''
import json
import re
import cv2
import base64
import requests
import numpy as np
from selenium import webdriver

from selenium.webdriver.chrome.options import Options

chrome_options = Options()
# 设置chrome浏览器无界面模式
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(chrome_options=chrome_options)


def decode_image(src, filename):
    """
    解码图片
    :param src: 图片编码
        eg:
            src="data:image/gif;base64,R0lGODlhMwAxAIAAAAAAAP///
                yH5BAAAAAAALAAAAAAzADEAAAK8jI+pBr0PowytzotTtbm/DTqQ6C3hGX
                ElcraA9jIr66ozVpM3nseUvYP1UEHF0FUUHkNJxhLZfEJNvol06tzwrgd
                LbXsFZYmSMPnHLB+zNJFbq15+SOf50+6rG7lKOjwV1ibGdhHYRVYVJ9Wn
                k2HWtLdIWMSH9lfyODZoZTb4xdnpxQSEF9oyOWIqp6gaI9pI1Qo7BijbF
                ZkoaAtEeiiLeKn72xM7vMZofJy8zJys2UxsCT3kO229LH1tXAAAOw=="

    :return: str 保存到本地的文件名
    """
    # 1、信息提取
    result = re.search("data:image/(?P<ext>.*?);base64,(?P<data>.*)", src, re.DOTALL)
    if result:
        ext = result.groupdict().get("ext")
        data = result.groupdict().get("data")

    else:
        raise Exception("Do not parse!")

    # 2、base64解码
    img = base64.urlsafe_b64decode(data)

    # 3、二进制文件保存
    # filename = "{}.{}".format(uuid.uuid4(), ext)
    with open(filename, "wb") as f:
        f.write(img)

    return img


def get_image_position():
    driver.get('https://www.luonet.com/login')
    cookies = driver.get_cookies()
    deviceId = list(filter(lambda key: 'deviceId' == key['name'], cookies))[0]
    ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:56.0) Gecko/20100101 Firefox/56.0'
    img_url = 'https://www.luonet.com/dcapi/captcha'
    s = requests.session()

    # jar = RequestsCookieJar()
    for cookie in cookies:
        # jar.set(cookie['name'], cookie['value'])
        s.cookies.set(cookie['name'], cookie['value'])
    # s.cookies = jar
    req = s.get(img_url, headers={'User-Agent': ua})
    jso = req.json()
    image1 = jso['bg']
    image2 = jso['front']
    decode_image(image2, 'slide_bkg.png')
    decode_image(image1, 'slide_block.png')

    block = cv2.imread('slide_block.png', 0)
    template = cv2.imread('slide_bkg.png', 0)

    cv2.imwrite('template.jpg', template)
    cv2.imwrite('block.jpg', block)
    block = cv2.imread('block.jpg')
    # 创建一个原始图像的灰度版本，所有操作在灰度版本中处理，然后在RGB图像中使用相同坐标还原
    block_cvt = cv2.cvtColor(block, cv2.COLOR_BGR2GRAY)  # 把图像从BGR转换到HSV,HSV分别是色调（Hue），饱和度（Saturation）和明度（Value）
    block_cvt = abs(255 - block_cvt)
    cv2.imwrite('block.jpg', block_cvt)

    block_cvt = cv2.imread('block.jpg')
    template = cv2.imread('template.jpg')
    # 使用matchTemplate对原始灰度图像和图像模板进行匹配
    result = cv2.matchTemplate(block_cvt, template, cv2.TM_CCOEFF_NORMED)
    x, y = np.unravel_index(result.argmax(), result.shape)
    print(x, y)
    data = {
        'offsetLeft': y + 0.132941176470587,
        'offsetTop': x
    }
    url = 'https://www.luonet.com/dcapi/captcha/verify'

    res = s.post(url=url, headers={'User-Agent': ua}, data=data)
    jso = res.json()
    if jso['success']:
        validate = jso['validate']
        payload = {
            "username": "17600696038",
            "password": "772781",
            "validate": validate,
            "id": deviceId['value']
        }
        login_url = 'https://www.luonet.com/dcapi/oauth/token'
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=UTF-8',
            'deviceId': deviceId['value'],
            'Host': 'www.luonet.com',
            'If-Modified-Since': 'Thu, 01 Jun 1970 00:00:00 GMT',
            'Origin': 'https://www.luonet.com',
            'Pragma': 'no-cache',
            'Referer': 'https://www.luonet.com/login',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'shouldIntercept': 'true',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }

        res = s.post(url=login_url, headers=headers, data=json.dumps(payload))
        print(res.json())
        res.json()


if __name__ == '__main__':
    get_image_position()

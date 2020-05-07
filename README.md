**今后会发布更多反爬虫文章，点波关注不迷路哦。**

*在做罗某某网站登陆的时候，发现有滑块验证码*

**[github地址](https://github.com/MaNongXiaoGang/LuoWang/tree/master)**

![登陆界面.png](https://upload-images.jianshu.io/upload_images/14530364-6a6e313904e3d8f6.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

**接下来我们研究一下这个滑块**
![登陆滑块.png](https://upload-images.jianshu.io/upload_images/14530364-e1bf9098e64634db.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

**进入调试模式 (按F12)，抓包发现这个接口和下面的参数**
![滑块接口url.png](https://upload-images.jianshu.io/upload_images/14530364-5db2c0acace3aa31.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

![滑块接口参数.png](https://upload-images.jianshu.io/upload_images/14530364-73a08950440dadc6.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
**这是验证接口，返回validate的关键登陆参数**

**接下来我们获取验证图片，处理和计算缺口到左边距离**
![灰值化图片1.png](https://upload-images.jianshu.io/upload_images/14530364-d579147d03499c16.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

###在运行代码前，我们先安装所需要的包。
>安装前先升级pip
>python -m pip install --upgrade pip # 如果是python3，修改成pip3
>安装cv2
>[pip install -i [https://pypi.tuna.tsinghua.edu.cn/simple](https://links.jianshu.com/go?to=https%3A%2F%2Fpypi.tuna.tsinghua.edu.cn%2Fsimple) opencv-python
](https://www.jianshu.com/p/33bbaadd604a)
>安装selenium
>pip install -i [https://pypi.tuna.tsinghua.edu.cn/simple](https://links.jianshu.com/go?to=https%3A%2F%2Fpypi.tuna.tsinghua.edu.cn%2Fsimple) selenium
>安装numpy
>pip install -i [https://pypi.tuna.tsinghua.edu.cn/simple](https://links.jianshu.com/go?to=https%3A%2F%2Fpypi.tuna.tsinghua.edu.cn%2Fsimple) numpy

####！！如果运行的时候selenium报错，可能是没有下载chrom驱动
下载地址:[http://npm.taobao.org/mirrors/chromedriver/](http://npm.taobao.org/mirrors/chromedriver/)
注意要下载对应自己Google浏览器的版本，不然也会报错。

####接下来放代码
```python
# coding=utf-8
# !/usr/bin python
'''

Author: [MaNongXiaoGang](https://www.jianshu.com/u/2f19d18204ce)
Python3 环境
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
    # 1、信息提取
    result = re.search("data:image/(?P<ext>.*?);base64,(?P<data>.*)", src, re.DOTALL)
    if result:
        ext = result.groupdict().get("ext")
        data = result.groupdict().get("data")
    else:
        raise Exception("Do not parse!")
    img = base64.urlsafe_b64decode(data)
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

    for cookie in cookies:
        s.cookies.set(cookie['name'], cookie['value'])
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

    block_cvt = cv2.cvtColor(block, cv2.COLOR_BGR2GRAY)  
    block_cvt = abs(255 - block_cvt)
    cv2.imwrite('block.jpg', block_cvt)

    block_cvt = cv2.imread('block.jpg')
    template = cv2.imread('template.jpg')

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

```

#### 运行结果截图

![运行数据截图.png](https://upload-images.jianshu.io/upload_images/14530364-7921f68d3fab7d3d.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

#### 此篇文章用于学术交流，不可用于商业

#coding=utf-8
# -*- coding: utf-8 -*-
import requests,logging
from bs4 import BeautifulSoup
import os
import re

#日志模块
logger = logging.getLogger(__name__)  # 定义对应的程序模块名name，默认是root
logger.setLevel(level=logging.DEBUG)  # root默认输出等级是INFO

ch = logging.StreamHandler()  # 日志输出到屏幕控制台
ch.setLevel(logging.DEBUG)  # 设置日志等级
fh = logging.FileHandler('test1.log', encoding='utf-8')  # 向文件access.log输出日志信息
fh.setLevel(logging.INFO)  # 设置输出到文件最低日志级别
formatter = logging.Formatter('%(asctime)s %(name)s- %(levelname)s - %(message)s')  # 定义日志输出格式

ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)

txt=open('url.txt')
with open('url.txt','r') as file:
    url=file.read()

def newgetHtml(url,postDataList=None,pdata=None,headers=None):
    logger.info("******************************开始获取网页************************************")
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0'
    }

    try:
        res=None
        res = requests.get(url, headers=headers)
    except Exception as e:
        print('Error code:', str(e))
        logger.error('Error code:', str(e))
    if res==None:
        raise Exception('未获取数据')
    page = res.text
    return page


def parsemeta():
    if not os.path.exists('url.txt'):
        logger.error('url.txt文件不存在')
        raise Exception('url.txt文件不存在')
    with open('url.txt', 'r') as file:
        url = file.read()
    if not url.endswith('/'):
        url = url + '/'
    strlst = url.split('/')
    id=strlst[-2]
    htmldata = newgetHtml(url=url)
    soup = BeautifulSoup(htmldata, 'html.parser')
    titlelst = soup.select('.o77S .title')
    title=titlelst[0].text
    try:
        if not os.path.exists(title):
            os.makedirs(title)
    except Exception as e:
        logger.error(str(e))
    outdir = title
    logger.info('outdir={}'.format(outdir))
    lst= soup.select('div .dOi2 .head > h2')
    cnt=int(lst[0].text[-4:-1])
    logger.info('cnt={}'.format(cnt))
    return id,outdir,cnt


if __name__=='__main__':
    parsemeta()
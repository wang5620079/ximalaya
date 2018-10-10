#coding=utf-8
# -*- coding: utf-8 -*-
import requests,logging

#日志模块
logger = logging.getLogger(__name__)  # 定义对应的程序模块名name，默认是root
logger.setLevel(level=logging.DEBUG)  # root默认输出等级是INFO

ch = logging.StreamHandler()  # 日志输出到屏幕控制台
ch.setLevel(logging.DEBUG)  # 设置日志等级
fh = logging.FileHandler('test.log', encoding='utf-8')  # 向文件access.log输出日志信息
fh.setLevel(logging.INFO)  # 设置输出到文件最低日志级别
formatter = logging.Formatter('%(asctime)s %(name)s- %(levelname)s - %(message)s')  # 定义日志输出格式

ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)

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
    page = res.text
    return page

if __name__=='__main__':
    pagedata=newgetHtml(url='https://www.ximalaya.com/yinyue/364431/')
    print(pagedata)



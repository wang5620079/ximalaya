#coding=utf-8
# -*- coding: utf-8 -*-
import requests,logging,json
import os
from bs4 import BeautifulSoup


#日志模块
logger = logging.getLogger(__name__)  # 定义对应的程序模块名name，默认是root
logger.setLevel(level=logging.DEBUG)  # root默认输出等级是INFO

ch = logging.StreamHandler()  # 日志输出到屏幕控制台
ch.setLevel(logging.DEBUG)  # 设置日志等级
fh = logging.FileHandler('log.log', encoding='utf-8')  # 向文件access.log输出日志信息
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
    if res==None:
        raise Exception('未获取数据')
    page = res.text
    return page

def parsemeta(htmldata):
    pass


def parsejson(jsonstr):
    if jsonstr==None:
        return None
    jsonobj=json.loads(jsonstr)
    datalst=jsonobj['data']['tracksAudioPlay']
    print(len(datalst))
    infolst=[]
    for datadict in datalst:
        trackName=datadict['trackName']
        src=datadict['src']
        if '：' in trackName:
            fname = trackName[trackName.index('：') + 1:].strip()
        else:
            fname=trackName
        #去掉括号等的异常字符
        if '(' in fname:
            fname=fname.replace('(','_')
        if ')' in fname:
            fname=fname.replace(')','_')
        infolst.append((fname,src))
    return infolst

def cmd_download(fname,url):
    try:
        info = os.system(r'you-get --debug -O {}.m4a {}'.format(fname,url))
        logger.debug(info)
    except Exception as e:
        logger.error(str(e))

def download(datalst):
    if datalst:
        for fname,url in datalst:
            logger.info('start download {}.m4a url={}'.format(fname,url))
            cmd_download(fname, url)
            logger.info('done')
    else:
        return
    logger.info('finish!')
    pass

if __name__=='__main__':
    #胎教故事
    #jsonstr=newgetHtml(url='https://www.ximalaya.com/revision/play/album?albumId=3509228&pageNum=1&sort=-1&pageSize=1000')
    #世界公认胎教音乐
    jsonstr=newgetHtml(url='https://www.ximalaya.com/revision/play/album?albumId=10258536&pageNum=1&sort=-1&pageSize=50')
    print('********************************************')
    infolst=parsejson(jsonstr)
    download(infolst)

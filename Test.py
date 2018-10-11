#coding=utf-8
# -*- coding: utf-8 -*-
import requests,logging,json
import os
from bs4 import BeautifulSoup
from http import cookiejar



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

# cookie初始化
httpsession = requests.session()
newcj = cookiejar.LWPCookieJar()
httpsession.cookies = newcj

def testgetHtml(url):
    logger.info("******************************开始获取网页测试页************************************")
    print('url={}'.format(url),end='')
    print('start',end='')
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': 'www.ximalaya.com',
        'Upgrade-Insecure-Requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.17 Safari/537.36'
    }

    try:
        res = None
        req = requests.request(url=url,headers=headers,method='GET').request.__dict__
        print(req)

    except Exception as e:
        print('Error code:', str(e))
        logger.error('Error code:', str(e))

def newgetHtml(url):
    logger.info("******************************开始获取网页************************************")
    logger.info('url={}'.format(url))
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host':'www.ximalaya.com',
        'Upgrade-Insecure-Requests':'1',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.17 Safari/537.36'
    }

    try:
        res=None
        res = httpsession.get(url, headers=headers)

    except Exception as e:
        print('Error code:', str(e))
        logger.error('Error code:', str(e))
    if res==None:
        logger.error('未获取数据')
        raise Exception('未获取数据')
    page = res.text
    return page


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

def cmd_download(fname,url,outdir=None):
    if 'google' in url:
        logger.info('google查询的url，越过！')
        return
    try:
        if not outdir:
            cmdstr = r'you-get --debug -O {}.m4a {}'.format(fname, url)
        else:
            cmdstr = r'you-get --debug -o {} -O {}.m4a {}'.format(outdir,fname, url)
        logger.info(cmdstr)
        info = os.system(cmdstr)
        logger.debug(info)
    except Exception as e:
        logger.error(str(e))

def download(datalst,outdir):
    if datalst:
        for fname,url in datalst:
            if not outdir:
                logger.info('start download {}.m4a url={}'.format(fname,url))
                cmd_download(fname, url)
            else:
                logger.info('start download {}.m4a url={} outdir={}'.format(fname, url,outdir))
                cmd_download(fname, url,outdir)
            logger.info('done')
    else:
        return
    logger.info('finish!')
    pass

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
    logger.info('titlelst={}'.format(str(titlelst)))
    title=titlelst[0].text
    try:
        if not os.path.exists(title):
            os.makedirs(title)
    except Exception as e:
        logger.error(str(e))
    outdir = title
    logger.info('make outdir {}'.format(outdir))
    lst= soup.select('div .dOi2 .head > h2')
    cnt=int(lst[0].text[-4:-1])
    logger.info('cnt={}'.format(cnt))
    return id,outdir,cnt

def test():
    if not os.path.exists('url.txt'):
        logger.error('url.txt文件不存在')
        raise Exception('url.txt文件不存在')
    urllines=[]
    with open('url.txt', 'r') as file:
        for line in file:
            urllines.append(line.strip())
    print(urllines)
    # url=url.strip()
    # testgetHtml(url=url)


if __name__=='__main__':
    test()
    # id,outdir,cnt=parsemeta()
    # jsonstr=newgetHtml(url='https://www.ximalaya.com/revision/play/album?albumId={}&pageNum=1&sort=-1&pageSize={}'.format(id,cnt))
    # datalst=parsejson(jsonstr)
    # download(datalst,outdir)


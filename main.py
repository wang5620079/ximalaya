#coding=utf-8
# -*- coding: utf-8 -*-
import requests,logging,json,os,re
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

def newgetHtml(url,postDataList=None,pdata=None,headers=None):
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
        #忽略google这样的url
        if 'google' in src:
            continue
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
    try:
        if not outdir:
            cmdstr = r'you-get --debug -O "{}".m4a {}'.format(fname, url)
        else:
            cmdstr = r'you-get --debug -o {} -O "{}".m4a {}'.format(outdir,fname, url)
        logger.info(cmdstr)
        info = os.system(cmdstr)
        logger.debug(info)
    except Exception as e:
        logger.error(str(e))

def download(datalst,outdir):
    if datalst:
        for fname,url in datalst:
            if 'google' in url:
                logger.info('google查询的url，越过！')
                continue
            if not outdir:
                logger.info('start download "{}".m4a url={}'.format(fname,url))
                cmd_download(fname, url)
            else:
                logger.info('start download "{}".m4a url={} outdir={}'.format(fname, url,outdir))
                cmd_download(fname, url,outdir)
            logger.info('done')
    else:
        return
    logger.info('finish!')
    pass

#批量下载
def batdownload(paramlst):
    for id, outdir, cnt in paramlst:
        #先生成目录
        try:
            if not os.path.exists(outdir):
                os.makedirs(outdir)
        except Exception as e:
            logger.error(str(e))
        #生成对应连接
        jsonstr=newgetHtml(url='https://www.ximalaya.com/revision/play/album?albumId={}&pageNum=1&sort=-1&pageSize={}'.format(id,cnt))
        datalst=parsejson(jsonstr)
        download(datalst,outdir)
    pass

def parsemeta():
    if not os.path.exists('url.txt'):
        logger.error('url.txt文件不存在')
        raise Exception('url.txt文件不存在')
    #所有参数的list
    paramlst=[]
    #存储url的list
    urllst = []
    with open('url.txt', 'r') as file:
        for line in file:
            if len(line.strip())>0:
                urllst.append(line.strip())
    #开始逐个解析，并生成数据
    for url in urllst:
        #获取id
        strlst = url.split('/')
        if url.endswith('/'):
            id = strlst[-2]
        else:
            id=strlst[-1]
        htmldata = newgetHtml(url=url)
        soup = BeautifulSoup(htmldata, 'html.parser')
        titlelst = soup.select('.o77S .title')
        logger.info('titlelst={}'.format(str(titlelst)))
        title = titlelst[0].text
        outdir = re.sub(':|：','_',str(title))

        logger.info('make outdir {}'.format(outdir))
        lst = soup.select('div .dOi2 .head > h2')
        cntstrlst = re.findall(r'\d+',str(lst[0].text))
        cnt=int(cntstrlst[0])
        logger.info('cnt={}'.format(cnt))
        paramlst.append((id,outdir,cnt))
    return paramlst



if __name__=='__main__':
    paramlst=parsemeta()
    batdownload(paramlst)


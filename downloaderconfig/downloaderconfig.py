#coding=utf-8
# -*- coding: utf-8 -*-

import logging
import os



"""
配置文件
"""

#日志配置
gloableloglevel = logging.DEBUG
fileloglevel = logging.INFO
consoleloglevel = logging.DEBUG

#url列表文件名称
config_path = os.path.realpath(__file__)
config_dir = os.path.dirname(os.path.abspath(os.path.join(os.path.realpath(__file__), "..")))
workdir= os.path.dirname(os.path.abspath(os.path.join(os.path.realpath(__file__), ".."))) + os.path.sep
urlsconfig= workdir + 'urls.txt'


if __name__=='__main__':
    print(config_path)
    print(config_dir)
    print(workdir)
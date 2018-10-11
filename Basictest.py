#coding=utf-8
# -*- coding: utf-8 -*-
import re
aa='胎教音乐：贝:多芬精选音乐'

print(re.sub(':|：','_',aa))
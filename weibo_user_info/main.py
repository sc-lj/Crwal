import sys
import os
from scrapy.cmdline import execute

path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(path)

execute('scrapy crawl weibo_user'.split())
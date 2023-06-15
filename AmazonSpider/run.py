from scrapy import cmdline

cmdline.execute('scrapy crawl amazon -o amazon.csv'.split())
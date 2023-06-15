# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AmazonspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    movie_name = scrapy.Field()
    movie_time = scrapy.Field()
    movie_format = scrapy.Field()
    movie_starring = scrapy.Field()
    movie_directed = scrapy.Field()
    movie_publishTime = scrapy.Field()
    # pass

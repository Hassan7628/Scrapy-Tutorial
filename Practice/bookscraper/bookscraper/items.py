# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookscraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class BookItem(scrapy.Item):
    Url = scrapy.Field()
    Title = scrapy.Field()
    Author = scrapy.Field()
    Rating = scrapy.Field()
    Price = scrapy.Field()
    Discount = scrapy.Field()
    Publication_Date = scrapy.Field()
    Pages = scrapy.Field()
    Binding = scrapy.Field()
    ISBN = scrapy.Field()
    Stock = scrapy.Field()
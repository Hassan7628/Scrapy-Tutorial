# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookscraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    Url=scrapy.Field()
    Title=scrapy.Field()
    Category=scrapy.Field()
    Product_type=scrapy.Field()
    Price=scrapy.Field()
    Price_excl_tax=scrapy.Field()
    Price_incl_tax=scrapy.Field()
    Tax=scrapy.Field()
    Availability=scrapy.Field()
    Number_of_reviews=scrapy.Field()
    Rating=scrapy.Field()
    Description=scrapy.Field()
    
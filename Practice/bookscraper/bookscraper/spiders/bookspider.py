import scrapy
from bookscraper.items import BookItem


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["www.libertybooks.com"]
    start_urls = ["https://www.libertybooks.com/trending/trending-now"]

    custom_settings = {"FEEDS": {"data.json": {"format": "json", "overwrite": True}}}

    def parse(self, response):
        books = response.css("div.ls-featured-book")
        for book in books:
            book_url = book.css("a.heading-books::attr(href)").get()
            yield response.follow(book_url, callback=self.parse_book)

            next_page = response.css("ul.pagination li a::attr(href)")[-1].get()

            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        table_rows = response.css("table tr td")
        bookitem = BookItem()

        bookitem["Url"] = response.url
        bookitem["Title"] = response.css(".ls-product-content-title h1::text").get()
        bookitem["Rating"] = response.css(".ls-product-raiting-star span::text").get()
        bookitem["Author"] = response.css(".ls-product-title-child h2 a::text").get()
        bookitem["Price"] = response.css(".ls-product-content-price div h2::text").get()
        bookitem["Discount"] = response.css(
            ".ls-product-content-price .badge-sucess::text"
        ).get()
        bookitem["Publication_Date"] = table_rows[1].css("td::text").get()
        bookitem["Pages"] = table_rows[3].css("td::text").get()
        bookitem["Binding"] = table_rows[5].css("td::text").get()
        bookitem["ISBN"] = table_rows[7].css("td::text").get()
        bookitem["Stock"] = response.css(
            ".ls-product-view-header h3 span.badge-sucess::text"
        ).get()

        yield bookitem

import scrapy
from bookscraper.items import BookItem


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        books = response.css("article.product_pod")

        for book in books:
            relative_url = book.css("h3 a::attr(href)").get()

            if "catalogue/" in relative_url:
                book_url = "https://books.toscrape.com/" + relative_url
            else:
                book_url = "https://books.toscrape.com/catalogue/" + relative_url

            yield response.follow(book_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            if "catalogue/" not in next_page:
                next_page_url = "https://books.toscrape.com/catalogue/" + next_page
            else:
                next_page_url = "https://books.toscrape.com/" + next_page

            yield response.follow(next_page_url, callback=self.parse)

    def parse_book(self, response):
        table_rows = response.css("table tr")
        book_item = BookItem()

        book_item["Url"] = (response.url,)
        book_item["Name"] = (response.css(".product_main h1::text").get(),)
        book_item["Genre"] = (
            response.xpath(
                "//ul[@class='breadcrumb'] //li[@class='active']/preceding-sibling::li[1]/a/text()"
            ).get(),
        )
        book_item["Product_type"] = (table_rows[1].css("td::text").get(),)
        book_item["Price_excl_tax"] = (table_rows[2].css("td::text").get(),)
        book_item["Price_incl_tax"] = (table_rows[3].css("td::text").get(),)
        book_item["Tax"] = (table_rows[4].css("td::text").get(),)
        book_item["Availability"] = (table_rows[5].css("td::text").get(),)
        book_item["Number_of_reviews"] = (table_rows[6].css("td::text").get(),)
        book_item["Rating"] = (response.css(".star-rating::attr(class)").get(),)
        book_item["Description"] = (
            response.xpath(
                "//div[@id='product_description']/following-sibling::p/text()"
            ).get(),
        )
        yield book_item
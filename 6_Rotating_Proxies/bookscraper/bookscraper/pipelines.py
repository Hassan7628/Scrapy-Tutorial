# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class BookscraperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        field_name = adapter.field_names()

        for name in field_name:
            value = adapter.get(name)

            if name != "Description":
                if isinstance(value, tuple):
                    value = value[0]

                if isinstance(value, str):
                    value = value.strip()

                adapter[name] = value

        avail = adapter.get("Availability")

        if isinstance(avail, tuple):
            avail = avail[0]

        spl_avail = avail.split("(")

        if len(spl_avail) < 2:
            adapter["Availability"] = 0

        avail = spl_avail[1]
        clean_avail = avail.split(" ")
        avail = clean_avail[0]

        adapter["Availability"] = avail

        price_keys = ["Price", "Price_excl_tax", "Price_incl_tax", "Tax"]

        for key in price_keys:
            price = adapter.get(key)

            if isinstance(price, tuple):
                price = price[0]

            if isinstance(price, str):
                spl_price = price.split("£")
                price = spl_price[1]

                try:
                    adapter[key] = float(price)
                except ValueError:
                    adapter[key] = 0.0

            rev = adapter.get("Reviews")
            if isinstance(rev, tuple):
                rev = rev[0]

            if isinstance(rev, str):
                try:
                    adapter["Reviews"] = int(rev)

                except (ValueError, TypeError):
                    adapter["Reviews"] = 0

        stars = adapter.get("Rating")

        spl_star = stars.split(" ")
        stars = spl_star[1]
        stars = stars.lower()

        if stars == "zero":
            adapter["Rating"] = " "

        elif stars == "one":
            adapter["Rating"] = "⭐"

        elif stars == "two":
            adapter["Rating"] = "⭐⭐"

        elif stars == "three":
            adapter["Rating"] = "⭐⭐⭐"

        elif stars == "four":
            adapter["Rating"] = "⭐⭐⭐⭐"

        elif stars == "five":
            adapter["Rating"] = "⭐⭐⭐⭐⭐"

        return item
    
import mysql.connector

class SaveToMySqlPipeline:
    def __init__(self):
        self.conn=mysql.connector.connect(
            host='localhost', user='root', password='1999', database='books'
        )

        self.cur=self.conn.cursor()

        self.cur.execute(
            """
                CREATE TABLE IF NOT EXISTS books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                Url VARCHAR(255),
                Title TEXT,
                Category VARCHAR(100),
                Product_type VARCHAR(100),
                Price VARCHAR(20),
                Price_excl_tax VARCHAR(20),
                Price_incl_tax VARCHAR(20),
                Tax VARCHAR(20),
                Availability VARCHAR(100),
                Number_of_reviews INT,
                Rating VARCHAR(50),
                Description TEXT
                )
            """)
        
    def process_item(self,item,spider):
        if isinstance(item.get('Rating'),str):
            item['Rating']=item.get('Rating').count('⭐')
        
        elif item['Rating'] is None:
            item['Rating']=0

        self.cur.execute("""
            INSERT INTO books (
                Url, Title, Category, Product_type,
                Price, Price_excl_tax, Price_incl_tax, Tax,
                Availability, Number_of_reviews, Rating, Description
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            item.get('Url'),
            item.get('Title'),
            item.get('Category'),
            item.get('Product_type'),
            item.get('Price'),
            item.get('Price_excl_tax'),
            item.get('Price_incl_tax'),
            item.get('Tax'),
            item.get('Availability'),
            int(item.get('Number_of_reviews', 0)),
            item.get('Rating'),
            item.get('Description')
        ))
        self.conn.commit()

        return item

    def close_process(self,spider):
        self.conn.close()
        self.cur.close()
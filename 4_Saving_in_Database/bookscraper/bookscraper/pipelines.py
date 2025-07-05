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

        for names in field_name:
            value = adapter.get(names)

            if isinstance(value, tuple):
                value[0] = value

            if isinstance(value, str):
                if names != "Description":
                    adapter[names] = value.strip()

        lowercase_keys = ["Category", "Product_type"]
        for keys in lowercase_keys:
            value = adapter.get(keys)

            if isinstance(value, tuple):
                value[0] = value

            if isinstance(value, str):
                adapter[keys] = value.lower()

        value = adapter.get("Availability")
        split_value = value.split("(")
        clean_value = split_value[1].split(" ")

        if len(split_value) < 2:
            adapter["Availability"] = 0
        else:
            adapter["Availability"] = int(clean_value[0])

        str1 = adapter.get("Number_of_reviews")

        try:
            adapter["Number_of_reviews"] = int(str1)

        except (ValueError, TypeError):
            adapter["Number_of_reviews"] = 0

        price_keys = ["Price", "Price_excl_tax", "Price_incl_tax", "Tax"]

        for keys in price_keys:
            value = adapter.get(keys)

            if isinstance(value, tuple):
                value = value[0]

            if isinstance(value, str):
                cleaned = value.replace("£", "")

                try:
                    adapter[keys] = cleaned
                except (ValueError, TypeError):
                    adapter[keys] = 0.0

        star_value = adapter.get("Rating")
        split_array = star_value.split(" ")
        star_value = split_array[1].lower()

        if star_value == "zero":
            adapter["Rating"] = ""

        elif star_value == "one":
            adapter["Rating"] = "⭐"

        elif star_value == "two":
            adapter["Rating"] = "⭐⭐"

        elif star_value == "three":
            adapter["Rating"] = "⭐⭐⭐"

        elif star_value == "four":
            adapter["Rating"] = "⭐⭐⭐⭐"

        elif star_value == "five":
            adapter["Rating"] = "⭐⭐⭐⭐⭐"

        return item


import mysql.connector


class SaveToMySqlPipeline:
    def __init__(self):
        # Connect to MySQL
        # Create cursor
        # Create table if it doesn't exist


        self.conn = mysql.connector.connect(
            host="localhost", user="root", password="1999", database="books"
        )

        # Create cursor used to execute command
        self.cur = self.conn.cursor()

        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                Url VARCHAR(255),
                Title TEXT,
                Category VARCHAR(255),
                Product_type VARCHAR(255),
                Price DECIMAL(10, 2),
                Price_excl_tax DECIMAL(10, 2),
                Price_incl_tax DECIMAL(10, 2),
                Tax DECIMAL(10, 2),
                Availability INT,
                Number_of_reviews INT,
                Rating INT,
                Description TEXT
                );"""
        )

    def process_item(self, item, spider):
        
        if isinstance(item.get("Rating"), str):
            item["Rating"] = item["Rating"].count("⭐")
        elif item.get("Rating") is None:
            item["Rating"] = 0 


        self.cur.execute(
            """
        INSERT INTO books (
            Url,
            Title,
            Category,
            Product_type,
            Price,
            Price_excl_tax,
            Price_incl_tax,
            Tax,
            Availability,
            Number_of_reviews,
            Rating,
            Description
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """,
            (
                item["Url"],
                item["Title"],
                item["Category"],
                item["Product_type"],
                item["Price"],
                item["Price_excl_tax"],
                item["Price_incl_tax"],
                item["Tax"],
                item["Availability"],
                item["Number_of_reviews"],
                item["Rating"],
                item["Description"],
            ),
        )

        self.conn.commit()

        return item

    def close_spider(self, spider):
        self.conn.close()
        self.cur.close()

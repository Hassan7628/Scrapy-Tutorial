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

        for i in field_name:
            value = adapter.get(i)
            if isinstance(value, tuple):
                value = value[0]

            if isinstance(value, str):
                value = value.strip()

            adapter[i] = value

        toint = ["Pages"]

        for i in toint:
            value = adapter.get(i)
            if isinstance(value, tuple):
                value = value[0]

            if isinstance(value, str):
                value = value.strip()

                if value.isdigit():
                    value = int(value)
                else:
                    None

            adapter[i] = value

        pr_val = ["Price", "Discount"]

        for i in pr_val:
            value = adapter.get(i)

            if isinstance(value, tuple):
                value = value[0]

            if isinstance(value, str):
                value_ls = value.split("Rs ")
                value = value_ls[1]
                value = value.replace(",", "")
                value = value.split(".")
                value = value[0]

            if value is not None:
                adapter[i] = int(value)
            else:
                adapter[i] = 0

        val = adapter.get("Rating")
        val = val.strip("()")
        val = int(val)

        if val == 0:
            adapter["Rating"] = " "

        elif val == 1:
            adapter["Rating"] = "⭐"

        elif val == 2:
            adapter["Rating"] = "⭐⭐"

        elif val == 3:
            adapter["Rating"] = "⭐⭐⭐"

        elif val == 4:
            adapter["Rating"] = "⭐⭐⭐⭐"

        elif val == 5:
            adapter["Rating"] = "⭐⭐⭐⭐⭐"

        val2 = adapter.get("Author")
        val2 = val2.replace('"', "")

        adapter["Author"] = val2

        return item


import mysql.connector


class SaveToMySql:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost", user="root", password="1999", database="books"
        )

        self.cur = self.conn.cursor()

        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS books(
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            Url TEXT,
            Author TEXT,
            Rating INTEGER,
            Price INTEGER,
            Discount INTEGER,
            Publication_Date TEXT,
            Pages INTEGER,
            Binding TEXT,
            ISBN TEXT,
            Stock TEXT)"""
        )

    def process_item(self, item, spider):
        value = item.get("Rating")
        if isinstance(value, str):
            item["Rating"] = value.count("⭐")

        elif item["Rating"] is None:
            item["Rating"] = 0

        self.cur.execute(
            """INSERT INTO books(
            Url, 
            Author, 
            Rating, 
            Price, 
            Discount, 
            Publication_Date, 
            Pages, 
            Binding, 
            ISBN, 
            Stock) 
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                item.get("Url"),
                item.get("Author"),
                item.get("Rating"),
                item.get("Price"),
                item.get("Discount"),
                item.get("Publication_Date"),
                item.get("Pages"),
                item.get("Binding"),
                item.get("ISBN"),
                item.get("Stock"),
            ),
        )

        self.conn.commit()

        return item

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()

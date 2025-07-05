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

        # Remove Whitespaces
        for name in field_name:
            value = adapter.get(name)
            if isinstance(value, tuple):
                value = value[0]

            if name != "Description" and isinstance(value, str):
                adapter[name] = value.strip()

        # Genre and Product Type to lowercase
        lowercase_keys = ["Genre", "Product_type"]
        for key in lowercase_keys:
            value = adapter.get(key)
            if isinstance(value, str):
                adapter[key] = value.lower()

        # Price convert to float
        price_keys = ["Price_excl_tax", "Price_incl_tax", "Tax"]
        for key in price_keys:
            value = adapter.get(key)

            if isinstance(value, tuple):
                value = value[0]

            else:

                value = value.replace("£", " ")
                try:
                    adapter[key] = float(value)
                except ValueError:
                    adapter[key] = 0.0

        # Availability -> Extract only number
        string = adapter.get("Availability")

        if isinstance(string, tuple):
            string = string[0]

        value = string.split("(")
        if len(value) < 2:
            adapter["Availability"] = 0
        else:
            availability_array = value[1].split(" ")
            adapter["Availability"] = int(availability_array[0])

        # Reviews -> convert text to number
        string = adapter.get("Number_of_reviews")
        try:
            adapter["Number_of_reviews"] = int(string)
        except (TypeError, ValueError):
            adapter["Number_of_reviews"] = 0

        # Stars -> convert text to number
        value = adapter.get("Rating")
        split_array = value.split(" ")
        value = split_array[1].lower()

        if value == "zero":
            adapter["Rating"] = ""

        elif value == "one":
            adapter["Rating"] = "⭐"

        elif value == "two":
            adapter["Rating"] = "⭐⭐"

        elif value == "three":
            adapter["Rating"] = "⭐⭐⭐"

        elif value == "four":
            adapter["Rating"] = "⭐⭐⭐⭐"

        elif value == "five":
            adapter["Rating"] = "⭐⭐⭐⭐⭐"

        return item

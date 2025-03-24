import scrapy
from datetime import datetime

class ExchangeRateSpider(scrapy.Spider):
    name = 'exchange'
    start_urls = ['https://cuantoestaeldolar.pe/']

    def parse(self, response):
        # Get current timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Extract exchange houses data
        exchange_houses_items = response.css(".ExchangeHouseItem_column__xGGy9 .ExchangeHouseItem_item__FLx1C")
        for item in exchange_houses_items:
            # Get the name from the title/header of the exchange house
            name = item.css(".ExchangeHouseItem_content_img__l76YK a img::attr(alt)").get()
            # Get rates
            rates = item.css(".flex .block p::text").getall()
            
            if name and len(rates) >= 2:
                try:
                    yield {
                        'timestamp': timestamp,
                        'type': 'exchange_house',
                        'name': name.strip(),
                        'buy_rate': float(rates[0].strip()),
                        'sell_rate': float(rates[2].strip())
                    }
                except (ValueError, TypeError):
                    self.logger.warning(f"Could not parse rates for {name}")

        # Extract banks data
        exchange_banks_items = response.css(".InterbankSection_item_bancos__eILoC")
        for item in exchange_banks_items:
            # Get the name from the title/header of the exchange house
            name = item.css(".InterbankSection_content_img_bancos__5tEpz a img::attr(alt)").get()
            # Get rates
            rates = item.css(".flex .block p::text").getall()
            
            if name and len(rates) >= 2:
                try:
                    yield {
                        'timestamp': timestamp,
                        'type': 'bank',
                        'name': name.strip(),
                        'buy_rate': float(rates[0].strip()),
                        'sell_rate': float(rates[2].strip())
                    }
                except (ValueError, TypeError):
                    self.logger.warning(f"Could not parse rates for {name}")

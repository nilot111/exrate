import scrapy
from datetime import datetime

class ExchangeRateSpider(scrapy.Spider):
    name = 'exchange'
    start_urls = ['https://cuantoestaeldolar.pe/']
    mappingurlsbanks={
        "bbva":"https://www.bbva.pe/personas/servicios-digitales/bbva-t-cambio.html",
        "Interbank":"https://interbank.pe/servicios/cambio-moneda/compra-venta-moneda-extranjera?tabs=tab-como-cierro-mi-operacion",
        "bcp":"https://www.viabcp.com/tipodecambio/dolares",
        "scotiabank":"https://www.scotiabank.com.pe/cambiar-dolares",
        "Banco de la nación":"https://www.bn.com.pe/clientes/servicios-adicionales/cambio-moneda.asp",
    }
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
            urlchange=item.css("div a.Button_button_change__PYUxL::attr(href)").get()
            urlchange=urlchange.split("?")[0]
            if name and len(rates) >= 2:
                if name=="Perú dolar":
                    name="Peru dolar"
                try:
                    yield {
                        'timestamp': timestamp,
                        'type': 'exchange_house',
                        'name': name.strip(),
                        'buy_rate': float(rates[0].strip()),
                        'sell_rate': float(rates[2].strip()),
                        'link':urlchange
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
                if name=="nacion":
                    name="Banco de la nación"                
                try:
                    yield {
                        'timestamp': timestamp,
                        'type': 'bank',
                        'name': name.strip(),
                        'buy_rate': float(rates[0].strip()),
                        'sell_rate': float(rates[2].strip()),
                        'link':self.mappingurlsbanks[name.strip()]
                    }
                except (ValueError, TypeError):
                    self.logger.warning(f"Could not parse rates for {name}")

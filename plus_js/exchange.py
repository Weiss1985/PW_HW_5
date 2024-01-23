import aiohttp
import asyncio
from datetime import datetime, timedelta
import sys
from time import time


VALID_CURRENCIES = [
    'USD',   # Долар США
    'EUR',   # Євро
    'CHF',   # Швейцарський франк
    'GBP',   # Британський фунт
    'PLN',   # Польський злотий
    'SEK',   # Шведська крона
    'XAU',   # Золото
    'CAD',   # Канадський долар
    'UZS',   # Узбецький сум
    'AUD',   # Австралійський долар
    'AZN',   # Азербайджанський манат
    'BYN',   # Білоруський рубль
    'CNY',   # Китайський юань
    'CZK',   # Чеська крона
    'DKK',   # Данська крона
    'GEL',   # Грузинський ларі
    'HUF',   # Угорський форинт
    'ILS',   # Ізраїльський шекель
    'JPY',   # Японська єна
    'KZT',   # Казахстанський тенге
    'MDL',   # Молдовський лей
    'NOK',   # Норвезька крона
]


async def monitoring():
    while True:
        await asyncio.sleep(1)
        print(f'Monitoring {time()}')


async def fetch_exchange_rate(date, currency):
    url = f"https://api.privatbank.ua/p24api/exchange_rates?json&date={date.strftime('%d.%m.%Y')}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception("Error accessing PrivatBank API")
                data = await response.json()
                for rate in data.get('exchangeRate', []):
                    if rate.get('currency') == currency:
                        return rate.get('saleRateNB')
        except Exception as e:
            print(f"Error fetching data: {e}")



async def main(days, currency):
    current_date = datetime.now()
    tasks = []
    response = []
    # asyncio.create_task(monitoring())

    for day in range(days):
        date = current_date - timedelta(days=day)
        tasks.append(fetch_exchange_rate(date, currency))

    rates = await asyncio.gather(*tasks)
    for i, rate in enumerate(rates):
        if rate:
            response.append(f"{currency} rate {days - i} days ago: {rate}")
    response_str = "\n".join(response)
    return response_str

if __name__ == "__main__":
    try:
        days = int(sys.argv[1])
        if not 1 <= days <= 10:
            raise ValueError("Days should be within 1 to 10")
        currency = sys.argv[2].upper()
        if currency not in VALID_CURRENCIES:
            raise ValueError(f"Currency should be one of {', '.join(VALID_CURRENCIES)}")
        print(asyncio.run(main(days, currency)))
    except Exception as e:
        print(f"Error: {e}")


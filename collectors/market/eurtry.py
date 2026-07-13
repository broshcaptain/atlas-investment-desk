from collectors.market.common import fetch_price, save_market_data

TICKER = "EURTRY=X"
SYMBOL = "EURTRY"


def collect() -> float:
    price = fetch_price(TICKER)
    save_market_data(SYMBOL, price, source=f"yfinance:{TICKER}")
    return price


if __name__ == "__main__":
    price = collect()
    print(f"{SYMBOL}: {price}")

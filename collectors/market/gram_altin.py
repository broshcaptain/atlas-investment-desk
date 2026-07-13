from collectors.market.common import GRAM_PER_TROY_OUNCE, fetch_price, save_market_data

# Doğrudan bir ticker'ı yok; Ons Altın (USD) ve USDTRY'den türetilir.
ONS_TICKER = "GC=F"
USDTRY_TICKER = "USDTRY=X"
SYMBOL = "GRAMALTIN"


def collect() -> float:
    ons_altin_usd = fetch_price(ONS_TICKER)
    usdtry = fetch_price(USDTRY_TICKER)

    gram_altin_try = (ons_altin_usd / GRAM_PER_TROY_OUNCE) * usdtry

    save_market_data(
        SYMBOL,
        gram_altin_try,
        source=f"derived: {ONS_TICKER} / {GRAM_PER_TROY_OUNCE} * {USDTRY_TICKER}",
    )
    return gram_altin_try


if __name__ == "__main__":
    price = collect()
    print(f"{SYMBOL}: {price:.2f} TL")

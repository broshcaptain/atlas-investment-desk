from collectors.market import bist100, brent, eurtry, gram_altin, ons_altin, usdtry

COLLECTORS = [usdtry, eurtry, ons_altin, gram_altin, brent, bist100]


def run_all() -> None:
    for module in COLLECTORS:
        try:
            price = module.collect()
            print(f"{module.SYMBOL}: {price}")
        except Exception as exc:
            print(f"{module.SYMBOL}: HATA - {exc}")


if __name__ == "__main__":
    run_all()

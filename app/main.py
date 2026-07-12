from app.database import engine, Base
from app.portfolio import add_stock, list_portfolio


Base.metadata.create_all(engine)


print("Atlas Investment Desk")


# Test için sadece ilk çalıştırmada aç
add_stock(
    "THYAO.IS",
    300,
    10
)


print("\nPortföy:")
list_portfolio()
from app.database import SessionLocal
from app.models import Portfolio
import yfinance as yf


def add_stock(symbol, buy_price, quantity):
    db = SessionLocal()

    existing = db.query(Portfolio).filter(
        Portfolio.symbol == symbol
    ).first()

    if existing:
        print(f"{symbol} zaten portföyde var.")
        db.close()
        return

    stock = Portfolio(
        symbol=symbol,
        buy_price=buy_price,
        quantity=quantity
    )

    db.add(stock)
    db.commit()
    db.close()

    print(f"{symbol} portföye eklendi.")


def get_current_price(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d")

    if data.empty:
        return 0

    return float(data["Close"].iloc[-1])


def list_portfolio():
    db = SessionLocal()

    stocks = db.query(Portfolio).all()

    result = []

    for stock in stocks:
        current_price = get_current_price(stock.symbol)

        cost = stock.buy_price * stock.quantity
        value = current_price * stock.quantity
        profit = value - cost

        result.append({
            "Hisse": stock.symbol,
            "Lot": stock.quantity,
            "Alış": stock.buy_price,
            "Güncel": round(current_price, 2),
            "Değer": round(value, 2),
            "Kar/Zarar": round(profit, 2)
        })

    db.close()

    return result
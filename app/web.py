import sys
import os

sys.path.append(os.path.dirname(__file__))

import streamlit as st
from app.portfolio import list_portfolio, add_stock
from app.database import engine, Base

Base.metadata.create_all(engine)


st.title("📈 Atlas Investment Desk")

st.subheader("Portföye Hisse Ekle")


symbol = st.text_input(
    "Hisse kodu",
    "THYAO.IS"
)

price = st.number_input(
    "Alış fiyatı",
    min_value=0.0
)

quantity = st.number_input(
    "Lot",
    min_value=1
)


if st.button("Ekle"):
    if price > 0 and quantity > 0:
        add_stock(
            symbol,
            price,
            quantity
        )
        st.success("Hisse eklendi")
    else:
        st.warning("Fiyat ve lot giriniz")

st.subheader("Portföy")

if st.button("Listele"):
    data = list_portfolio()

    if data:
        import pandas as pd

df = pd.DataFrame(data)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

        total_cost = sum(
            x["Alış"] * x["Lot"] for x in data
        )

        total_value = sum(
            x["Değer"] for x in data
        )

        profit = total_value - total_cost

        st.divider()

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Toplam Yatırım",
            f"{total_cost:,.2f} TL"
        )

        col2.metric(
            "Güncel Değer",
            f"{total_value:,.2f} TL"
        )

        col3.metric(
            "Kâr/Zarar",
            f"{profit:,.2f} TL"
        )
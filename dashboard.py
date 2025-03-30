import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt


# Menampilkan dashboard order terbanyak berdasarkan kota
def create_bycity_df(df):
    # Menghitung jumlah order per kota
    bycity_df = df.groupby(by="customer_city").order_id.nunique().reset_index()
    bycity_df.rename(columns={
        "order_id": "order_count"
    }, inplace=True)

    return bycity_df


# Menampilkan dashboard revenue terbanyak berdasarkan kategori produk
def create_category_orders_df(df):
    # Mengatur kolom 'order_purchase_timestamp' sebagai index untuk resample
    df.set_index('order_purchase_timestamp', inplace=True)

    # Resampling untuk menghitung total order dan revenue per hari
    category_orders_df = df.resample(rule='D').agg({
        "order_id": "nunique",  # Menghitung jumlah unik order_id per hari
        "payment_value": "sum"  # Menghitung total pembayaran per hari
    })

    category_orders_df = category_orders_df.reset_index()  # Reset index setelah resample
    category_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)

    return category_orders_df


# Membaca data dari CSV
all_df = pd.read_csv("main_data2.csv")

# Mendefinisikan kolom datetime
datetime_columns = ["order_purchase_timestamp"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(drop=True, inplace=True)  # Pastikan index kembali setelah sorting

# Mengkonversi kolom datetime
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Menentukan rentang tanggal minimum dan maksimum
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

# Menambahkan sidebar untuk memilih rentang waktu
with st.sidebar:
    # Pastikan `value` adalah list atau tuple yang berisi dua nilai (start_date, end_date)
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]  # Pastikan ini adalah list dengan dua nilai
    )

# Filter data berdasarkan rentang waktu yang dipilih
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) &
                 (all_df["order_purchase_timestamp"] <= str(end_date))]

# Menghasilkan data berdasarkan kota dan kategori produk
bycity_df = create_bycity_df(main_df)
category_orders_df = create_category_orders_df(main_df)

# Menampilkan header dashboard
st.header('Brazilian E-Commerce Dashboard :sparkles:')
st.subheader('Orders Demographics')

# Membatasi hanya 10 data terbanyak berdasarkan jumlah order
top10_bycity_df = bycity_df.sort_values(by="order_count", ascending=False).head(10)

colors = ["#FF6347", "#FFD700", "#98FB98", "#8A2BE2", "#FF4500", "#00FA9A",
          "#2E8B57", "#FF1493", "#4682B4", "#D2691E"]

fig, ax = plt.subplots(figsize=(20, 12))

sns.barplot(
    x="customer_city",
    y="order_count",
    data=top10_bycity_df,
    palette=colors,
    ax=ax
)

ax.set_title("10 Kota Dengan Order Terbanyak (Ribu)", loc="center", fontsize=50)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=25, rotation=45)  # Rotasi 45 derajat untuk label x
ax.tick_params(axis='y', labelsize=30)

plt.tight_layout()  # Ini akan memastikan layout menyesuaikan dan tidak terpotong
st.pyplot(fig)

# Membatasi hanya 10 data terbanyak berdasarkan payment_value
revenue_by_category_df = all_df.groupby('product_category_name').agg({
    "payment_value": "sum"  # Menghitung total payment_value untuk setiap kategori produk
}).reset_index()

revenue_by_category_df.rename(columns={
    "payment_value": "total_revenue",
    "product_category_name": "category"
}, inplace=True)

# Mengurutkan kategori produk berdasarkan total revenue terbanyak
revenue_by_category_df = revenue_by_category_df.sort_values(by='total_revenue', ascending=False)

# Menampilkan 10 kategori produk dengan revenue terbanyak
top_10_revenue_categories = revenue_by_category_df.head(10)

fig2, ax2 = plt.subplots(figsize=(20, 12))  # Ukuran grafik

sns.barplot(
    x="total_revenue",
    y="category",
    data=top_10_revenue_categories,  # Menampilkan hanya 10 kategori produk terbanyak
    palette=colors,
    ax=ax2
)

ax2.set_title("10 Kategori Produk Dengan Revenue Terbanyak (Juta)", loc="center", fontsize=50)
ax2.tick_params(axis='x', labelsize=25)
ax2.tick_params(axis='y', labelsize=30)

plt.tight_layout()

st.pyplot(fig2)

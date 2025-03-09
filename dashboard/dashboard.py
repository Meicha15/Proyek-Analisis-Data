import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_mapping_hari(df):
    weekday_usage = df.groupby("weekday")["cnt"].sum().sort_values(ascending=False).reset_index()
    return weekday_usage
def create_cluster(df):
    weekday_usage = df.groupby("weekday")["cnt"].sum().sort_values(ascending=False).reset_index()
    # Hitung mean dan standar deviasi
    mean_usage = weekday_usage["cnt"].mean()
    std_usage = weekday_usage["cnt"].std()
    def categorize_usage(cnt):
        if cnt >= mean_usage + std_usage:
            return "Tinggi"
        elif cnt <= mean_usage - std_usage:
            return "Rendah"
        else:
            return "Sedang"
    weekday_usage["cluster"] = weekday_usage["cnt"].apply(categorize_usage)
    return weekday_usage
def create_day_melted(df):
    day_melted = df.groupby(by='weather_category').agg({
    "cnt": "sum",
    "registered": "sum",
    "casual": "sum"}).reindex(["Cerah", "Berawan", "Hujan Ringan", "Hujan Lebat"]).fillna(0)
    return day_melted
def create_day_df(df):
    day_df = df.groupby(by='dteday').agg({
        'cnt':'sum',
        'registered':'sum',
        'casual':'sum'
    })
    day_df = day_df.reset_index()
    return day_df
def create_rfm_df(df):
    rfm_df = df.groupby('dteday').agg({
    "cnt": "sum",  # Total peminjaman sebagai Monetary
    "registered": "sum"  # Pengguna terdaftar sebagai Frequency
    }).reset_index()
    # Hitung Recency (hari sejak transaksi terakhir)
    max_date = rfm_df["dteday"].max()
    rfm_df["Recency"] = (max_date - rfm_df['dteday']).dt.days
    # Normalisasi nilai RFM
    rfm_df["Monetary"] = rfm_df["cnt"]
    rfm_df["Frequency"] = rfm_df["registered"]
    return rfm_df
all_df = pd.read_csv("dashboard/all_data (2).csv")

datetime_columns = ["dteday"]
all_df.sort_values(by="dteday", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])
min_date = all_df["dteday"].min()
max_date = all_df["dteday"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.header("Penyewaan Sepeda MS")
    st.image("dashboard/logo.png", width=200)
    st.subheader("Hallo,selamat datang di penyewaan sepeda MS!!")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["dteday"] >= str(start_date)) & 
                (all_df["dteday"] <= str(end_date))]

weekday_usage_df = create_mapping_hari(main_df)
day_melted_df = create_day_melted(main_df)
day_df = create_day_df(main_df)
rfm_df = create_rfm_df(main_df)
cluster_df = create_cluster(main_df)

st.header("Selamat Datang di Pusat Analisis Penyewaan Sepeda :sparkles:")
st.subheader("Total Penyewaan")
col1, col2, col3 = st.columns(3)
with col1:
    total_cnt = day_df.cnt.sum()
    st.metric("Jumlah keseluruhan penyewaan", value=total_cnt)
with col2:
    total_registered = day_df.registered.sum()
    st.metric("Jumlah regristred", value=total_registered)
with col3:
    total_casual = day_df.casual.sum()
    st.metric("Jumlah casual", value=total_casual)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    day_df["dteday"],
    day_df["cnt"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

st.subheader("Hari dengan Penggunaan Sepeda Terbanyak dan Tersedikit")
fig1, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3","#D3D3D3","#D3D3D3"]

# hari dengan penggunaan sepeda terbanyak
sns.barplot(x="cnt", y="weekday", data=weekday_usage_df, palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Total Penggunaan Sepeda")
ax[0].set_title("Hari dengan Penggunaan Sepeda Terbanyak", loc="center", fontsize=15)
ax[0].tick_params(axis='y', labelsize=12)

# hari dengan penggunaan sepeda tersedikit
sns.barplot(x="cnt", y="weekday", data=weekday_usage_df.sort_values(by="cnt", ascending=True), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Total Penggunaan Sepeda")
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Hari dengan Penggunaan Sepeda Tersedikit", loc="center", fontsize=15)
ax[1].tick_params(axis='y', labelsize=12)

plt.suptitle("Hari dengan Penggunaan Sepeda Terbanyak dan Tersedikit", fontsize=20)
st.pyplot(fig1)

st.subheader('Cluster Pengguna Sepeda Berdasarkan Hari')
pp = plt.figure(figsize=(10, 5))
sns.barplot(x="weekday", y="cnt", hue="cluster", data= cluster_df, palette={"Tinggi":"red","Rendah":"green","Sedang":"yellow"})
plt.title("Cluster Pengguna Sepeda Berdasarkan Hari")
plt.xlabel("Hari")
plt.ylabel("Jumlah Pengguna Sepeda")
st.pyplot(pp)

# Scatter plot antara suhu dan jumlah penyewaan sepeda
st.subheader("Scatter plot antara suhu dan jumlah penyewaan sepeda")
yy = plt.figure(figsize=(10, 5))
sns.scatterplot(x=all_df['temp'], y=all_df['cnt'])
plt.xlabel("Suhu (Normalized)")
plt.ylabel("Jumlah Penyewaan Sepeda")
plt.title("Hubungan Suhu dan Penyewaan Sepeda")
st.pyplot(yy)
xx = plt.figure(figsize=(10, 5))
sns.regplot(x=all_df['temp'], y=all_df['cnt'])
plt.xlabel("Suhu (Normalized)")
plt.ylabel("Jumlah Penyewaan Sepeda")
plt.title("Hubungan Suhu dan Penyewaan Sepeda")
st.pyplot(xx)

st.subheader("Distribusi Penyewaan Sepeda Berdasarkan Kondisi Cuaca")
zz = plt.figure(figsize=(8, 5))
sns.boxplot(x=all_df['weathersit'], y=all_df['cnt'],palette="rocket")
plt.xlabel("Kondisi Cuaca (1=Cerah, 2=Berawan, 3=Hujan Ringan, 4=Hujan Lebat)")
plt.ylabel("Jumlah Penyewaan Sepeda")
plt.title("Distribusi Penyewaan Sepeda Berdasarkan Kondisi Cuaca")
st.pyplot(zz)

st.subheader("Perbandingan Penyewaan Sepeda Berdasarkan Kondisi Cuaca")
#Membuat baar plot untuk weathercategory dengan cnt, registered, dan casual ada dalam satu plot
fig2=day_melted_df[['registered', 'casual']].plot(kind='bar', figsize=(10, 5),color=['green','blue']).get_figure()
plt.xlabel("Kondisi Cuaca")
plt.ylabel("Jumlah Penyewaan Sepeda")
plt.title("Perbandingan Penyewaan Sepeda Berdasarkan Kondisi Cuaca")
plt.legend()
plt.gca().ticklabel_format(style='plain', axis='y')
st.pyplot(fig2)

st.subheader("Best Customer Based on RFM Parameters")
fig3, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))
 
colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]
 
sns.barplot(y="Recency", x="registered", data=rfm_df.sort_values(by="Recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
ax[0].tick_params(axis ='x', labelsize=15)
 
sns.barplot(y="Frequency", x="registered", data=rfm_df.sort_values(by="Frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=18)
ax[1].tick_params(axis='x', labelsize=15)
 
sns.barplot(y="Monetary", x="registered", data=rfm_df.sort_values(by="Monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=18)
ax[2].tick_params(axis='x', labelsize=15)
 
plt.suptitle("Best Customer Based on RFM Parameters", fontsize=20)
st.pyplot(fig3)

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_working_day(df):
    working_day = df.groupby(by='workingday').agg({
    "cnt": "mean",
    "registered": "mean",
    "casual": "mean"})
    return working_day
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
def create_monthly_usage(df):
    monthly_usage = day_df.resample(rule='M', on='dteday').agg({
    "cnt": "sum"})
    return monthly_usage

all_df = pd.read_csv("dashboard/all_data.csv")

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

working_day_df = create_working_day(main_df)
weekday_usage_df = create_mapping_hari(main_df)
day_melted_df = create_day_melted(main_df)
day_df = create_day_df(main_df)
cluster_df = create_cluster(main_df)
monthly_usage_df = create_monthly_usage(main_df)

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

st.subheader("Jumlah Penyewaan Sepeda Berdasarkan Bulan")
mm = plt.figure(figsize=(25, 10))
plt.plot(monthly_usage_df.index, monthly_usage_df["cnt"], marker='o', linestyle='-')
month = monthly_usage_df.index.strftime('%m-%Y')
plt.title("Jumlah Penyewaan Sepeda Berdasarkan Bulan")
plt.xlabel("Bulan")
plt.xticks(monthly_usage_df.index, month, rotation=45, ha='right')
plt.ylabel("Jumlah Penyewaan")
st.pyplot(mm)

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

fig2, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))
colors = ["#72BCD4", "#D3D3D3", "#D5D5D5", "#D3D3D3"]
sns.barplot(x=day_melted_df.index, y=day_melted_df['cnt'], palette=colors, ax=ax[0])
ax[0].set_title("Total Keseluruhan Penyewaan Sepeda", loc="center", fontsize=15)
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].tick_params(axis='x', labelsize=15)

sns.barplot(x='weather_category', y='value', hue='variable', 
            data=day_melted_df[['registered','casual']].reset_index().melt(id_vars=['weather_category']), 
            palette=['green', 'blue'], ax=ax[1]) 

ax[1].set_title("Jumlah Penyewaan Sepeda Berdasarkan Pengguna", loc="center", fontsize=15)
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].tick_params(axis='x', labelsize=15)

plt.suptitle("Pengaruh Kondisi Cuaca Terhadap Jumlah Penyewaan Sepeda", fontsize=20)
st.pyplot(fig2)

st.subheader('Cluster Pengguna Sepeda Berdasarkan Hari')
pp = plt.figure(figsize=(10, 5))
sns.scatterplot(x="weekday", y="cnt", hue="cluster", data=cluster_df, 
                palette={"Tinggi": "red", "Rendah": "green", "Sedang": "yellow"}, s=100)
plt.title("Cluster Pengguna Sepeda Berdasarkan Hari")
plt.xlabel("Hari")
plt.ylabel("Jumlah Pengguna Sepeda")
plt.grid(True)
st.pyplot(pp)



import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='dark')

#Helper function
def create_daily_rentals_df(df):
    daily_rentals_df = df.resample(rule='D', on='dteday').agg({
        "yr": "first",
        "casual": "sum",
        "registered": "sum",
        "cnt": "sum"
    })
    daily_rentals_df = daily_rentals_df.reset_index()
    daily_rentals_df.rename(columns={
        "yr": "tahun",
        "casual": "pengguna_biasa",
        "registered": "pengguna_terdaftar",
        "cnt": "jumlah_penyewa"
    }, inplace=True)

    return daily_rentals_df

def create_user_status_df(df):
    user_status_df = df.groupby(by= 'yr')[['casual', 'registered']].sum().reset_index()
    user_status_df['yr'] = user_status_df['yr'].map({0: 2011, 1: 2012})

    user_status_df = user_status_df.melt(id_vars='yr', var_name='Tipe Pengguna', value_name='Jumlah Penyewaan')

    return user_status_df

def create_month_rentals_df(df):
    month_rentals_df = df.resample(rule='M', on='dteday').agg({
        "cnt": "sum"
    }).reset_index()
    month_rentals_df['yr'] = month_rentals_df['dteday'].dt.year
    month_rentals_df['month'] = month_rentals_df['dteday'].dt.strftime('%B')

    month_rentals_df.rename(columns={
        "cnt": "jumlah_penyewa"
    }, inplace=True)
    month_rentals_df.drop(columns='dteday', inplace=True)
    month_rentals_df = month_rentals_df.set_index('yr')

    return month_rentals_df

def create_week_rentals_df(df):
    week_rentals_df = df.groupby(by=['yr', 'weekday']).cnt.sum().reset_index()
    week_rentals_df['yr'] = week_rentals_df['yr'].map({0: 2011, 1: 2012})
    week_rentals_df['weekday'] = week_rentals_df['weekday'].map({0: 'Minggu', 1: 'Senin', 2: 'Selasa', 3: 'Rabu', 4: 'Kamis', 5: 'Jumat', 6: 'Sabtu'}) 

    return week_rentals_df

def create_day_status_df(df):
    day_status_df = df.groupby(by=['yr', 'group_day']).cnt.sum().reset_index()
    day_status_df['yr'] = day_status_df['yr'].map({0: 2011, 1: 2012})
    day_status_df['group_day'] = day_status_df['group_day'].map({0: "Hari Kerja", 1: "Akhir Pekan", 2: "Hari Libur"})

    return day_status_df

def create_season_status_df(df):
    season_status_df = df.groupby(by=['yr', 'season']).cnt.sum().reset_index()
    season_status_df['yr'] = season_status_df['yr'].map({0: 2011, 1: 2012})
    season_status_df['season'] = season_status_df['season'].map({1: "Musim Semi", 2: "Musim Panas", 3: "Musim Gugur", 4: "Musim Dingin"})

    return season_status_df

def create_weather_status_df(df):
    weather_status_df = df.groupby(by=['yr', 'weathersit']).cnt.sum().reset_index()
    weather_status_df['yr'] = weather_status_df['yr'].map({0: 2011, 1: 2012})
    weather_status_df['weathersit'] = weather_status_df['weathersit'].map({1: "Cerah Berawan", 2: "Kabut Berawan", 3: "Hujan/Salju Ringan", 4: "Cuaca Ekstrem"})

    return weather_status_df

def create_year_rentals_df(df):
    year_rentals_df = df.groupby(by=['yr', 'time_categories']).cnt.sum().reset_index()
    year_rentals_df['yr'] = year_rentals_df['yr'].map({0: 2011, 1: 2012})

    return year_rentals_df

def create_user_rentals_df(df):
    user_rentals_df = df.groupby(by='user_categories').cnt.count()

    return user_rentals_df

def create_rentals_categories_df(df):
    if df < 1000:
        return 'Rendah'
    elif 1000 <= df <= 5000:
        return 'Sedang'
    else:
        return 'Tinggi'

def create_time_categories_df(df):
    if 0 <= df < 6:
        return 'Dini Hari'
    elif 6 <= df < 11:
        return 'Pagi'
    elif 11 <= df < 15:
        return 'Siang'
    elif 15 <= df < 18:
        return 'Sore'
    else:
        return 'Malam'

def create_user_categories_df(df):
    if df['casual'] > df['registered']:
        return 'Mayoritas Pengguna Biasa'
    else:
        return 'Mayoritas Pengguna Terdaftar'

hour_df = pd.read_csv("./dashboard/hour_df.csv")

hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

hour_df['time_categories'] = hour_df['hr'].apply(create_time_categories_df)
hour_df['user_categories'] = hour_df.apply(create_user_categories_df, axis=1)

hour_df['group_day'] = hour_df.apply(
    lambda row: 1 if row['workingday'] == 0 and row['holiday'] == 0 else
                2 if row['workingday'] == 0 and row['holiday'] == 1 else
                2 if row['workingday'] == 1 and row['holiday'] == 1 else
                0, axis=1
)

min_date = hour_df['dteday'].min()
max_date = hour_df['dteday'].max()

with st.sidebar:
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date, value=[min_date, max_date]
    )

    start_hour, end_hour = st.slider("Rentang Jam", min_value=0, max_value=23, value=(0, 23), format="%d:00")

    st.write("Tipe Pengguna")
    show_registered = st.checkbox("Registered", value=True)
    show_casual = st.checkbox("Casual", value=True)
    
    st.write("Kondisi Musim")
    season_labels = {1: "Musim Semi", 2: "Musim Panas", 3: "Musim Gugur", 4: "Musim Dingin"}
    selected_season = []
    for season, label in season_labels.items():
        if st.checkbox(label, value=True):
           selected_season.append(season)

    st.write("Kondisi Hari")
    day_labels = {0: "Hari Kerja", 1: "Akhir Pekan", 2: "Hari Libur"}
    selected_day = []
    for day, label in day_labels.items():
        if st.checkbox(label, value=True):
           selected_day.append(day)

    st.write("Kondisi Cuaca") 
    weather_labels = {1: "Cerah Berawan", 2: "Kabut Berawan", 3: "Hujan/Salju Ringan", 4: "Cuaca Ekstrem"}
    selected_weather = []
    for weather, label in weather_labels.items():
        if st.checkbox(label, value=True):
           selected_weather.append(weather)

main_df = hour_df[(hour_df["dteday"] >= str(start_date)) &
                (hour_df["dteday"] <= str(end_date)) &
                (hour_df["hr"] >= start_hour) &
                (hour_df["hr"] <= end_hour) &
                (hour_df["season"].isin(selected_season)) &
                (hour_df["weathersit"].isin(selected_weather)) &
                (hour_df["group_day"].isin(selected_day))]

daily_rentals_df = create_daily_rentals_df(main_df)
daily_rentals_df["rental_categories"] = daily_rentals_df["jumlah_penyewa"].apply(create_rentals_categories_df)
month_rentals_df = create_month_rentals_df(main_df)
week_rentals_df = create_week_rentals_df(main_df)
user_status_df = create_user_status_df(main_df)
day_status_df = create_day_status_df(main_df)
season_status_df = create_season_status_df(main_df)
weather_status_df = create_weather_status_df(main_df)
year_rentals_df = create_year_rentals_df(main_df)
user_rentals_df = create_user_rentals_df(main_df)

st.header('Bike Sharing Dashboard')
st.subheader('Daily rentals (Casual vs Registered)')

col1, col2, col3 = st.columns(3)

with col1:
    total_rentals = daily_rentals_df.jumlah_penyewa.sum()
    st.metric("Total Penyewa", value=total_rentals)

with col2:
    total_rentals_casual = daily_rentals_df.pengguna_biasa.sum()
    st.metric("Pengguna Biasa", value=total_rentals_casual)

with col3:
    total_rentals_registered = daily_rentals_df.pengguna_terdaftar.sum()
    st.metric("Pengguna Terdaftar", value=total_rentals_registered)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_rentals_df["dteday"],
    daily_rentals_df["pengguna_biasa"],
    marker='o', 
    linewidth=2,
    label="Pengguna Biasa",
    color="#FFA07A"
)

ax.plot(
    daily_rentals_df["dteday"],
    daily_rentals_df["pengguna_terdaftar"],
    marker='o', 
    linewidth=2,
    label="Pengguna Terdaftar",
    color="#1976D2"
)

ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
ax.legend()
st.pyplot(fig)

st.subheader("User Status")

fig, ax = plt.subplots(figsize=(16, 8))

sns.barplot(
    y="Jumlah Penyewaan",
    x="yr",
    hue="Tipe Pengguna",
    data=user_status_df,
    palette='coolwarm',
    ax=ax
)
ax.set_title("Jumlah Penyewa Sepeda Berdasarkan Tipe Pengguna (2011 vs 2012)", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=15)
ax.tick_params(axis='y', labelsize=15)
st.pyplot(fig)

st.subheader("Time Based Pattern")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(16, 8))

    month_2011 = month_rentals_df.query("yr == 2011")
    month_2012 = month_rentals_df.query("yr == 2012")

    ax.plot(
        month_2011.month,
        month_2011.jumlah_penyewa,
        marker='o',
        linewidth=2,
        label='2011',
        color='#72BCD4'    
    )

    ax.plot(
        month_2012.month,
        month_2012.jumlah_penyewa,
        marker='o',
        linewidth=2,
        label='2012',
        color='#FFA07A'
    )

    ax.set_title('Jumlah Penyewaan Sepeda per Bulan (2011 vs 2012)', loc='center', fontsize=30)
    ax.tick_params(axis='y', labelsize=15)
    ax.tick_params(axis='x', labelsize=15)
    ax.legend()
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(16, 8))

    week_2011 = week_rentals_df.query("yr == 2011")
    week_2012 = week_rentals_df.query("yr == 2012")

    ax.plot(
        week_2011.weekday,
        week_2011.cnt,
        marker='o',
        linewidth=2,
        label='2011',
        color='#72BCD4'    
    )

    ax.plot(
        week_2012.weekday,
        week_2012.cnt,
        marker='o',
        linewidth=2,
        label='2012',
        color='#FFA07A'
    )

    ax.set_title('Jumlah Penyewaan Sepeda per Hari dalam Seminggu (2011 vs 2012)', loc='center', fontsize=30)
    ax.tick_params(axis='y', labelsize=15)
    ax.tick_params(axis='x', labelsize=15)
    ax.legend()
    st.pyplot(fig)

st.subheader("Day, Season, and Weather Changes (2011 vs 2012)")
avg_temp = main_df["temp"].mean()
avg_atemp = main_df["atemp"].mean()
avg_hum = main_df["hum"].mean()
avg_windspeed = main_df["windspeed"].mean()

col1, col2 = st.columns(2)
col1.metric(label="Rata-rata Suhu (temp)", value=f"{avg_temp:.2f}")
col2.metric(label="Rata-rata Suhu Terasa (atemp)", value=f"{avg_atemp:.2f}")

col3, col4 = st.columns(2)
col3.metric(label="Rata-rata Kelembaban (hum)", value=f"{avg_hum:.2f}")
col4.metric(label="Rata-rata Kecepatan Angin (windspeed)", value=f"{avg_windspeed:.2f}")

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = 'Set2'
sns.barplot(
    y="cnt",
    x="group_day",
    hue="yr",
    data=day_status_df,
    palette=colors,
    ax=ax[0]
)
ax[0].set_title("Day Changes", fontsize=30)
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].tick_params(axis='x', labelsize=15)
ax[0].tick_params(axis='y', labelsize=15)
ax[0].legend(title="Tahun")

sns.barplot(
    y="cnt",
    x="season",
    hue="yr",
    data=season_status_df,
    palette=colors,
    ax=ax[1]
)
ax[1].set_title("Season Changes", fontsize=30)
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].tick_params(axis='x', labelsize=15)
ax[1].tick_params(axis='y', labelsize=15)
ax[1].legend(title="Tahun")

sns.barplot(
    y="cnt",
    x="weathersit",
    hue="yr",
    data=weather_status_df,
    palette=colors,
    ax=ax[2]
)
ax[2].set_title("Weather Changes", fontsize=30)
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].tick_params(axis='x', labelsize=15)
ax[2].tick_params(axis='y', labelsize=15)
ax[2].legend(title="Tahun")

st.pyplot(fig)

rental_counts = daily_rentals_df["rental_categories"].value_counts()
most_common_rental_category = rental_counts.idxmax() 
avg_rental_count = daily_rentals_df[daily_rentals_df["rental_categories"] == most_common_rental_category]["jumlah_penyewa"].mean()

time_counts = year_rentals_df.groupby("time_categories")["cnt"].sum()
most_popular_time = time_counts.idxmax()  

time_ranges = {
    "Dini Hari": "00:00 - 05:59",
    "Pagi": "06:00 - 10:59",
    "Siang": "11:00 - 14:59",
    "Sore": "15:00 - 17:59",
    "Malam": "18:00 - 23:59"
}
most_popular_time_range = time_ranges.get(most_popular_time, "Tidak diketahui")

total_casual = user_status_df[user_status_df["Tipe Pengguna"] == "casual"]["Jumlah Penyewaan"].sum()
total_registered = user_status_df[user_status_df["Tipe Pengguna"] == "registered"]["Jumlah Penyewaan"].sum()

if total_casual > total_registered:
    majority_user = "Biasa (Casual)"
    avg_user_count = total_casual / 2  
else:
    majority_user = "Terdaftar (Registered)"
    avg_user_count = total_registered / 2  

st.subheader("Clustered (Manual Grouping)")

col1, col2 = st.columns(2)
col1.metric(label="Kategori Penyewaan Terbanyak", value=most_common_rental_category, help=f"Rata-rata: {avg_rental_count:.2f}")
col2.metric(label="Waktu Paling Diminati", value=most_popular_time, help=f"Rentang Waktu: {most_popular_time_range}")

col3 = st.columns(1)
col3[0].metric(label="Mayoritas Pengguna", value=majority_user, help=f"Rata-rata Pengguna: {avg_user_count:.2f}")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
colors = 'Set2'
sns.countplot(
    data=daily_rentals_df,
    x="rental_categories",
    hue="tahun",
    palette=colors,
    ax=ax[0]
)
ax[0].set_title("Rental Group Categories", fontsize=30)
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].legend(title="Tahun", labels=["2011", "2012"])

time_2011 = year_rentals_df.query("yr == 2011")
time_2012 = year_rentals_df.query("yr == 2012")

ax[1].plot(
    time_2011.time_categories,
    time_2011.cnt,
    marker='o',
    linewidth=2,
    label='2011',
    color='#72BCD4'    
)

ax[1].plot(
    time_2012.time_categories,
    time_2012.cnt,
    marker='o',
    linewidth=2,
    label='2012',
    color='#FFA07A'
)

ax[1].set_title('Time Group Categories', loc='center', fontsize=30)
ax[1].tick_params(axis='y', labelsize=15)
ax[1].tick_params(axis='x', labelsize=15)
ax[1].legend()

st.pyplot(fig)

fig, ax = plt.subplots(figsize=(2, 2))

user_rentals_df.plot.pie(
    autopct='%1.1f%%',
    colors=['skyblue', 'orange', 'green'],
    startangle=90,
    textprops={'fontsize': 4},
    ax=ax
)
ax.set_title("User Group Categories", fontsize=6)
ax.set_ylabel(None)
ax.set_aspect("equal")
ax.axis('off')

st.pyplot(fig)

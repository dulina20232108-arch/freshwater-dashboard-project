import streamlit as st
import pandas as pd
import plotly.express as px

# Page setup
st.set_page_config(
    page_title="Freshwater & Cultivated Area Dashboard",
    page_icon="💧",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_freshwater_cultivated_area.csv")
    return df

df = load_data()

# Title
st.title("💧 Global Freshwater Withdrawal and Cultivated Land Dashboard")

st.markdown("""
This dashboard explores the relationship between **total freshwater withdrawal** 
and the **percentage of total country area cultivated**.  
It helps identify countries where agricultural land use may place pressure on freshwater resources.
""")

# Sidebar filters
st.sidebar.header("Dashboard Filters")

years = sorted(df["Year"].unique())
selected_year = st.sidebar.selectbox("Select Year", years, index=len(years)-1)

countries = sorted(df["Country"].unique())
selected_countries = st.sidebar.multiselect(
    "Select Countries",
    countries,
    default=["India", "China", "United States"] if all(c in countries for c in ["India", "China", "United States"]) else countries[:3]
)

withdrawal_categories = sorted(df["Freshwater_Withdrawal_Category"].dropna().unique())
selected_withdrawal_categories = st.sidebar.multiselect(
    "Freshwater Withdrawal Category",
    withdrawal_categories,
    default=withdrawal_categories
)

cultivation_categories = sorted(df["Cultivation_Category"].dropna().unique())
selected_cultivation_categories = st.sidebar.multiselect(
    "Cultivation Category",
    cultivation_categories,
    default=cultivation_categories
)

# Filter data
filtered_year_df = df[
    (df["Year"] == selected_year) &
    (df["Freshwater_Withdrawal_Category"].isin(selected_withdrawal_categories)) &
    (df["Cultivation_Category"].isin(selected_cultivation_categories))
]

country_df = df[df["Country"].isin(selected_countries)]

# KPI cards
st.subheader(f"Key Indicators for {selected_year}")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Number of Countries", filtered_year_df["Country"].nunique())

with col2:
    avg_water = filtered_year_df["Total_Freshwater_Withdrawal"].mean()
    st.metric("Average Freshwater Withdrawal", f"{avg_water:,.2f}")

with col3:
    avg_cultivated = filtered_year_df["Cultivated_Area_Percentage"].mean()
    st.metric("Average Cultivated Area %", f"{avg_cultivated:.2f}%")

with col4:
    highest_country = filtered_year_df.loc[
        filtered_year_df["Total_Freshwater_Withdrawal"].idxmax(), "Country"
    ] if not filtered_year_df.empty else "N/A"
    st.metric("Highest Withdrawal Country", highest_country)

st.divider()

# Map
st.subheader("Global Freshwater Withdrawal Map")

fig_map = px.choropleth(
    filtered_year_df,
    locations="Country_Code",
    color="Total_Freshwater_Withdrawal",
    hover_name="Country",
    hover_data={
        "Total_Freshwater_Withdrawal": True,
        "Cultivated_Area_Percentage": True,
        "Country_Code": False
    },
    color_continuous_scale="Blues",
    title=f"Total Freshwater Withdrawal by Country ({selected_year})"
)

st.plotly_chart(fig_map, use_container_width=True)

# Scatter plot
st.subheader("Relationship Between Cultivated Area and Freshwater Withdrawal")

fig_scatter = px.scatter(
    filtered_year_df,
    x="Cultivated_Area_Percentage",
    y="Total_Freshwater_Withdrawal",
    hover_name="Country",
    size="Total_Freshwater_Withdrawal",
    color="Freshwater_Withdrawal_Category",
    title=f"Cultivated Area % vs Total Freshwater Withdrawal ({selected_year})",
    labels={
        "Cultivated_Area_Percentage": "Cultivated Area (% of Country Area)",
        "Total_Freshwater_Withdrawal": "Total Freshwater Withdrawal"
    }
)

st.plotly_chart(fig_scatter, use_container_width=True)

# Efficiency chart
st.subheader("Water Use Efficiency Analysis")

fig_efficiency = px.scatter(
    filtered_year_df,
    x="Cultivated_Area_Percentage",
    y="Water_per_Cultivation",
    hover_name="Country",
    color="Freshwater_Withdrawal_Category",
    size="Total_Freshwater_Withdrawal",
    title=f"Water Use per Cultivated Area ({selected_year})",
    labels={
        "Cultivated_Area_Percentage": "Cultivated Area (% of Country Area)",
        "Water_per_Cultivation": "Freshwater Withdrawal per 1% Cultivated Area",
        "Total_Freshwater_Withdrawal": "Total Freshwater Withdrawal"
    }
)

st.plotly_chart(fig_efficiency, use_container_width=True)

st.info("""
This chart shows how much freshwater is withdrawn in relation to cultivated land area. 
Countries with high values may indicate higher water pressure or less efficient water use for agriculture-related land activity.
""")

# Trend chart
st.subheader("Country Trend Over Time")

if selected_countries:
    fig_line = px.line(
        country_df,
        x="Year",
        y="Total_Freshwater_Withdrawal",
        color="Country",
        markers=True,
        title="Freshwater Withdrawal Trend by Selected Countries"
    )
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.warning("Please select at least one country from the sidebar.")

# Top 10 countries
st.subheader("Top 10 Countries by Freshwater Withdrawal")

top10 = filtered_year_df.sort_values(
    by="Total_Freshwater_Withdrawal",
    ascending=False
).head(10)

fig_bar = px.bar(
    top10,
    x="Country",
    y="Total_Freshwater_Withdrawal",
    color="Cultivated_Area_Percentage",
    title=f"Top 10 Freshwater Withdrawal Countries ({selected_year})",
    labels={
        "Total_Freshwater_Withdrawal": "Total Freshwater Withdrawal",
        "Cultivated_Area_Percentage": "Cultivated Area %"
    }
)

st.plotly_chart(fig_bar, use_container_width=True)

# Cultivated area ranking
st.subheader("Top 10 Countries by Cultivated Area Percentage")

top_cultivated = filtered_year_df.sort_values(
    by="Cultivated_Area_Percentage",
    ascending=False
).head(10)

fig_cultivated = px.bar(
    top_cultivated,
    x="Country",
    y="Cultivated_Area_Percentage",
    color="Total_Freshwater_Withdrawal",
    title=f"Top 10 Countries by Cultivated Area Percentage ({selected_year})",
    labels={
        "Cultivated_Area_Percentage": "Cultivated Area %",
        "Total_Freshwater_Withdrawal": "Total Freshwater Withdrawal"
    }
)

st.plotly_chart(fig_cultivated, use_container_width=True)

# Data table
st.subheader("Cleaned Dataset Preview")

st.dataframe(filtered_year_df, use_container_width=True)

# Download button
csv = filtered_year_df.to_csv(index=False)

st.download_button(
    label="Download Filtered Data as CSV",
    data=csv,
    file_name="filtered_freshwater_cultivated_area.csv",
    mime="text/csv"
)
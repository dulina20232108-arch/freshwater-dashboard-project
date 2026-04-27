import pandas as pd;
import os;

# File paths
cultivated_path = "data_raw/cultivated_area.csv"
freshwater_path = "data_raw/total_freshwater_withdrawal.csv"

output_path = "data_cleaned/cleaned_freshwater_cultivated_area.csv";

# Load datasets
cultivated = pd.read_csv(cultivated_path);
freshwater = pd.read_csv(freshwater_path);

print("Cultivated area dataset shape:", cultivated.shape);
print("Freshwater withdrawal dataset shape:", freshwater.shape);

# Keep only useful columns
cultivated_clean = cultivated[[
    "REF_AREA",
    "REF_AREA_LABEL",
    "TIME_PERIOD",
    "OBS_VALUE",
    "OBS_STATUS_LABEL",
    "UNIT_MEASURE_LABEL"
]].copy();

freshwater_clean = freshwater[[
    "REF_AREA",
    "REF_AREA_LABEL",
    "TIME_PERIOD",
    "OBS_VALUE",
    "OBS_STATUS_LABEL",
    "UNIT_MEASURE_LABEL"
]].copy();

# Rename columns
cultivated_clean = cultivated_clean.rename(columns={
    "REF_AREA": "Country_Code",
    "REF_AREA_LABEL": "Country",
    "TIME_PERIOD": "Year",
    "OBS_VALUE": "Cultivated_Area_Percentage",
    "OBS_STATUS_LABEL": "Cultivated_Data_Status",
    "UNIT_MEASURE_LABEL": "Cultivated_Unit"
});

freshwater_clean = freshwater_clean.rename(columns={
    "REF_AREA": "Country_Code",
    "REF_AREA_LABEL": "Country",
    "TIME_PERIOD": "Year",
    "OBS_VALUE": "Total_Freshwater_Withdrawal",
    "OBS_STATUS_LABEL": "Freshwater_Data_Status",
    "UNIT_MEASURE_LABEL": "Freshwater_Unit"
});

# Convert data types
cultivated_clean["Year"] = pd.to_numeric(cultivated_clean["Year"], errors="coerce");
freshwater_clean["Year"] = pd.to_numeric(freshwater_clean["Year"], errors="coerce");

cultivated_clean["Cultivated_Area_Percentage"] = pd.to_numeric(
    cultivated_clean["Cultivated_Area_Percentage"], errors="coerce"
);

freshwater_clean["Total_Freshwater_Withdrawal"] = pd.to_numeric(
    freshwater_clean["Total_Freshwater_Withdrawal"], errors="coerce"
);

# Remove rows with missing key values
cultivated_clean = cultivated_clean.dropna(subset=[
    "Country_Code", "Country", "Year", "Cultivated_Area_Percentage"
]);

freshwater_clean = freshwater_clean.dropna(subset=[
    "Country_Code", "Country", "Year", "Total_Freshwater_Withdrawal"
]);

# Remove duplicates
cultivated_clean = cultivated_clean.drop_duplicates();
freshwater_clean = freshwater_clean.drop_duplicates();

# Merge both datasets using country and year
df = pd.merge(
    freshwater_clean,
    cultivated_clean,
    on=["Country_Code", "Country", "Year"],
    how="inner"
);

# Filter recent years for dashboard
df = df[(df["Year"] >= 2014) & (df["Year"] <= 2022)];

# Remove impossible values
df = df[df["Cultivated_Area_Percentage"] >= 0];
df = df[df["Cultivated_Area_Percentage"] <= 100];
df = df[df["Total_Freshwater_Withdrawal"] >= 0];

# Round values
df["Cultivated_Area_Percentage"] = df["Cultivated_Area_Percentage"].round(2);
df["Total_Freshwater_Withdrawal"] = df["Total_Freshwater_Withdrawal"].round(2);

# Create categories for dashboard filtering
df["Cultivation_Category"] = pd.cut(
    df["Cultivated_Area_Percentage"],
    bins=[0, 10, 30, 60, 100],
    labels=[
        "Low Cultivation",
        "Moderate Cultivation",
        "High Cultivation",
        "Very High Cultivation"
    ],
    include_lowest=True
);

df["Freshwater_Withdrawal_Category"] = pd.cut(
    df["Total_Freshwater_Withdrawal"],
    bins=[0, 1, 10, 50, 1000],
    labels=[
        "Low Withdrawal",
        "Medium Withdrawal",
        "High Withdrawal",
        "Very High Withdrawal"
    ],
    include_lowest=True
);
df["Water_per_Cultivation"] = (
    df["Total_Freshwater_Withdrawal"] / df["Cultivated_Area_Percentage"]
)
# Sort data
df = df.sort_values(by=["Country", "Year"]);

# Final quality checks
print("\nFinal cleaned dataset shape:", df.shape);
print("\nMissing values:");
print(df.isnull().sum());

print("\nDuplicate rows:");
print(df.duplicated().sum());

print("\nYear range:");
print(df["Year"].min(), "to", df["Year"].max());

print("\nNumber of countries:");
print(df["Country"].nunique());

print("\nPreview:");
print(df.head());

# Save cleaned dataset
os.makedirs("data_cleaned", exist_ok=True);
df.to_csv(output_path, index=False);

print("\nCleaned dataset saved successfully:");
print(output_path);
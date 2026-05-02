import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("Food_Inspections_20260406.csv")

print(df.head())
print(df.columns)
print(df.dtypes)
print(df.isna().sum())
# print(df["Violations"].unique())

df["Inspection Date"] = pd.to_datetime(df["Inspection Date"], errors = "coerce")

#visualization #1 - Geospatial
import plotly.express as px

#also filter out "Business Not Located" and "No Entry" 
excluded_statuses = ['Out of Business', 'Business Not Located', 'No Entry']
df_business = df[~df['Results'].isin(excluded_statuses)]

#ensure Latitude and Longitude are numeric
df_business['Latitude'] = pd.to_numeric(df_business['Latitude'], errors='coerce')
df_business['Longitude'] = pd.to_numeric(df_business['Longitude'], errors='coerce')

#drop any rows missing coordinates
df_map = df_business.dropna(subset=['Latitude', 'Longitude'])

#create the map
fig = px.scatter_map(
    df_map, 
    lat="Latitude", 
    lon="Longitude", 
    color="Results",          
    hover_name="DBA Name",     
    hover_data=["Address", "Facility Type", "Risk"],
    zoom=10,                
    center={"lat": 41.8781, "lon": -87.6298}, 
    height=600,
    title="Chicago Food Inspection Map"
)

#set a map style
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})

fig.show()

#visualization #2 - Distribution

#calculate number of violations per row
df['Violation_Count'] = df['Violations'].fillna('').apply(
    lambda x: len(x.split('|')) if x != '' else 0
)

#set the order for the x-axis
risk_order = ['Risk 1 (High)', 'Risk 2 (Medium)', 'Risk 3 (Low)']

#create the box plot
plt.figure(figsize=(10, 6))
sns.boxplot(x='Risk', y='Violation_Count', data=df, order=risk_order, palette='Set2', hue="Risk", legend = False)

#add labels
plt.title('Distribution of Violation Counts by Establishment Risk Level', fontsize=14)
plt.xlabel('Risk Category', fontsize=12)
plt.ylabel('Number of Violations Found', fontsize=12)

plt.tight_layout()
plt.show()

# #visualization #3 - Multivariate

#set keywords
keywords = ['INSECT', 'TEMPERATURE', 'CLEANING', 'TOILET', 'EQUIPMENT', 'PERSONNEL', 'STORAGE']
for word in keywords:
    df[word] = df['Violations'].str.contains(word, case=False, na=False)

#group by facility type and sum
failure_reasons = df.groupby('Facility Type')[keywords].sum()

#normailze number by setting data to proportions
normalized_reasons = failure_reasons.div(failure_reasons.sum(axis=1), axis=0)

#filter for Top n facilities so the chart isn't too tall
top_facilities = failure_reasons.sum(axis=1).nlargest(10).index
normalized_reasons = normalized_reasons.loc[top_facilities]

#plot the heatmap
plt.figure(figsize=(12, 8))
sns.heatmap(normalized_reasons, annot=True, cmap="YlGnBu", fmt=".2%") # Show as percentage

plt.title("Proportional Failure Reasons by Facility Type (Normalized)")
plt.xlabel("Violation Category")
plt.ylabel("Facility Type")
plt.show()

#visualizition #4 - Stacked Bar
excluded_statuses = ['Out of Business', 'Business Not Located', 'No Entry']
df_status = df[~df['Results'].isin(excluded_statuses)]

df_status = df_status.groupby(['Facility Type', 'Results']).size().unstack().fillna(0)
top_facilities = df_status.sum(axis=1).nlargest(5).index
filtered_data = df_status.loc[top_facilities]

filtered_data.plot(kind='bar', stacked=True, figsize=(10, 6), color=['#ff9999','#66b3ff','#99ff99'])
plt.show()
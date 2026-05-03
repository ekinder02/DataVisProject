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
 
#ensure Latitude and Longitude are numeric
df['Latitude']  = pd.to_numeric(df['Latitude'],  errors='coerce')
df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
 

#drop any rows missing coordinates
df_map = df[~df['Results'].isin(excluded_statuses)].dropna(subset=['Latitude', 'Longitude'])
 
#colors based on passing results
result_colors = {
    'Pass':               '#2ca02c',
    'Pass w/ Conditions': '#98df8a',
    'Fail':               '#d62728',
    'Not Ready':          '#ff7f0e',
}

#create the map
fig = px.scatter_map(
    df_map,
    lat="Latitude", lon="Longitude",
    color="Results",
    color_discrete_map=result_colors, 
    hover_name="DBA Name",
    hover_data=["Address", "Facility Type", "Risk"],
    opacity=0.65,                    
    zoom=10,
    center={"lat": 41.8781, "lon": -87.6298},
    height=600,
    title="Chicago Food Inspection Map"
)

#set a map style
fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":40,"l":0,"b":0})

fig.show()


#visualization #2 - Distribution

#calculate number of violations per row
df['Violation_Count'] = df['Violations'].fillna('').apply(
    lambda x: len(x.split('|')) if x != '' else 0
)

#set the order for the x-axis
risk_order = ['Risk 1 (High)', 'Risk 2 (Medium)', 'Risk 3 (Low)']

#drop unknown risk values
df_risk = df[df['Risk'].isin(risk_order)]


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


# set keywords
keywords = ['INSECT', 'TEMPERATURE', 'CLEANING', 'TOILET', 'EQUIPMENT', 'PERSONNEL', 'STORAGE']
for word in keywords:
    df[word] = df['Violations'].str.contains(word, case=False, na=False)
 

#group by facility type and sum
failure_reasons   = df.groupby('Facility Type')[keywords].sum()

#normailze number by setting data to proportions
normalized_reasons = failure_reasons.div(failure_reasons.sum(axis=1), axis=0)


#filter for Top n facilities so the chart isn't too tall
top_facilities    = failure_reasons.sum(axis=1).nlargest(10).index
normalized_reasons = normalized_reasons.loc[top_facilities]
 

#plot the heatmap
plt.figure(figsize=(12, 8))
sns.heatmap(normalized_reasons, annot=True, cmap="YlGnBu", fmt=".1%")
 
plt.title("Proportional Failure Reasons by Facility Type")
plt.xlabel("Violation Category")
plt.ylabel("Facility Type")
plt.xticks(rotation=30, ha='right') 
plt.tight_layout()
plt.show()




#visualization #4 - Stacked Bar

#exclude inspections where the business wasn't actually open/available
excluded_statuses = ['Out of Business', 'Business Not Located', 'No Entry']
df_status = df[~df['Results'].isin(excluded_statuses)]

#count inspections for each facility type + result combination, then pivot to wide format
df_status = df_status.groupby(['Facility Type', 'Results']).size().unstack().fillna(0)

#keep only the 5 facility types with the most total inspections
top_facilities = df_status.sum(axis=1).nlargest(5).index
filtered_data  = df_status.loc[top_facilities]

#convert raw counts to proportions so facilities of different sizes are comparable
props = filtered_data.div(filtered_data.sum(axis=1), axis=0)

#assign colors by result name so each category always gets the right color
color_map = {
    'Fail':               '#d62728',
    'Not Ready':          '#ff7f0e',
    'Pass':               '#2ca02c',
    'Pass w/ Conditions': '#98df8a',
}
colors = [color_map[col] for col in props.columns if col in color_map]

ax = props.plot(kind='bar', stacked=True, figsize=(10, 6),
                color=colors, edgecolor='white')



ax.set_title('Inspection Outcomes by Facility Type', fontsize=14)
ax.set_xlabel('')
ax.set_ylabel('Share of Inspections', fontsize=12)
plt.xticks(rotation=25, ha='right')

#format y-axis as percentages
ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax.set_yticklabels(['0%', '25%', '50%', '75%', '100%'])

plt.legend(title='Result', bbox_to_anchor=(1.01, 1), loc='upper left', frameon=False)
plt.tight_layout()
plt.show()


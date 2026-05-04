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
df = df[(df["Inspection Date"].dt.year == 2022) | (df["Inspection Date"].dt.year == 2026)]

#visualization #1 - Geospatial
import plotly.express as px


#also filter out "Business Not Located" and "No Entry" 
 
#ensure Latitude and Longitude are numeric
df['Latitude']  = pd.to_numeric(df['Latitude'],  errors='coerce')
df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
 

#drop any rows missing coordinates
 
#colors based on passing results
result_colors = {
    'Risk 3 (Low)':       '#2ca02c',
    'Risk 2 (Medium)': "#d5c214",
    'Risk 1 (High)':               '#d62728',
}

#create the map
fig = px.scatter_map(
    df,
    lat="Latitude", lon="Longitude",
    color="Risk",
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


# 1. Set keywords and create boolean columns (Keep as is)
keywords = ['INSECT', 'TEMPERATURE', 'CLEANING', 'TOILET', 'EQUIPMENT', 'STORAGE', 'PHYSICAL', 'FOOD']
for word in keywords:
    df[word] = df['Violations'].str.contains(word, case=False, na=False)

# 2. Group by 'Risk'
failure_reasons = df.groupby('Risk')[keywords].sum()

# 3. Normalize: Convert counts to proportions (Keep as is)
normalized_reasons = failure_reasons.div(failure_reasons.sum(axis=1), axis=0)

# 4. Reorder and then TRANSPOSE (.T)
risk_order = ['Risk 1 (High)', 'Risk 2 (Medium)', 'Risk 3 (Low)']
# We transpose here so categories become rows and Risk becomes columns
flipped_reasons = normalized_reasons.reindex(risk_order).fillna(0).T

# 5. Plot the heatmap
plt.figure(figsize=(10, 8)) # Adjusted height for better category reading
sns.heatmap(flipped_reasons, annot=True, cmap="YlGnBu", fmt=".1%")

# Update labels to match the flip
plt.title("What Drives the Failure? Violation Types by Assigned Risk Level", fontsize=14)
plt.xlabel("Assigned Risk Level", fontsize=12)
plt.ylabel("Violation Category", fontsize=12)

plt.tight_layout()
plt.show()

#visualization #4 - Stacked Bar

# 1. Prepare the Data: Group by Risk and Results

target_results = ['Pass', 'Fail', 'Pass w/ Conditions']
df = df[df['Results'].isin(target_results)]

# We use normalize='index' to turn counts into percentages (0.0 to 1.0)
risk_results = pd.crosstab(df['Risk'], df['Results'], normalize='index') * 100

# 2. Reorder for logical flow
risk_order = ['Risk 1 (High)', 'Risk 2 (Medium)', 'Risk 3 (Low)']
risk_results = risk_results.reindex(risk_order)

# 3. Create the Grouped Bar Chart
ax = risk_results.plot(kind='bar', 
                       stacked=False, 
                       figsize=(12, 7), 
                       color=['#e74c3c', '#2ecc71', '#f1c40f'], # Red, Yellow, Green
                       width=0.8)

# 4. Styling for clarity
plt.title("Is Risk Predictive? Outcome Percentages by Assigned Risk Level", fontsize=15)
plt.ylabel("Percentage of Inspections (%)", fontsize=12)
plt.xlabel("City-Assigned Risk Level", fontsize=12)
plt.legend(title="Inspection Result", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.ylim(0, 100) # Ensure the scale is always 0-100%

# Add percentage labels on top of the bars
for p in ax.patches:
    ax.annotate(f'{p.get_height():.1f}%', 
                (p.get_x() + p.get_width() / 2., p.get_height()), 
                ha = 'center', va = 'center', 
                xytext = (0, 9), 
                textcoords = 'offset points',
                fontsize=9)

plt.tight_layout()
plt.show()

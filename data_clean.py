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

#visualization #1 - Geospatial data showing pass or fail by location, or maybe density of passes in chicago

#visualization #2 - Group by pass or fail and then show facility type
#Calculate the number of violations per row
df['Violation_Count'] = df['Violations'].fillna('').apply(
    lambda x: len(x.split('|')) if x != '' else 0
)

#Set the order for the X-axis so it goes High -> Medium -> Low
risk_order = ['Risk 1 (High)', 'Risk 2 (Medium)', 'Risk 3 (Low)']

#Create the Box Plot
plt.figure(figsize=(10, 6))
sns.boxplot(x='Risk', y='Violation_Count', data=df, order=risk_order, palette='Set2')

#Add labels and title
plt.title('Distribution of Violation Counts by Establishment Risk Level', fontsize=14)
plt.xlabel('Risk Category', fontsize=12)
plt.ylabel('Number of Violations Found', fontsize=12)

plt.tight_layout()
plt.show()

# #visualization #3 - Distribution of risk or violations or results
# plt.hist(df["Results"].dropna())
# plt.tight_layout()
# plt.show()

#visualizition #4 - Griup by facility type and then show pass/fail
df_status = df.groupby(['Facility Type', 'Results']).size().unstack().fillna(0)
top_facilities = df_status.sum(axis=1).nlargest(5).index
filtered_data = df_status.loc[top_facilities]
print(filtered_data)

filtered_data.plot(kind='bar', stacked=True, figsize=(10, 6), color=['#ff9999','#66b3ff','#99ff99'])
plt.show()

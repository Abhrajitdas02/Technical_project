import pandas as pd
import numpy as np

# Load the CSV files into DataFrames
df1 = pd.read_csv('day1.csv')
df2 = pd.read_csv('day2.csv')

array1=np.array(df1)
array2=np.array(df2)


df1_CSV = pd.DataFrame(array1,columns=['element','id', 'class', 'text'])
df2_CSV = pd.DataFrame(array2,columns=['element','id', 'class', 'text'])

df1_CSV.index +=1
df2_CSV.index+=1

a= df1[df1.eq(df2).all(axis=1) == False]
a.index +=1
print(a.to_string(index=False))
print("\n")

# # Ensure both DataFrames have the specified columns
# for column in columns_to_check:
#     if column not in df1.columns:
#         print(f"Column '{column}' is missing in df1.")
#     if column not in df2.columns:
#         print(f"Column '{column}' is missing in df2.")

# # Merge DataFrames to identify modified fields in specified columns
# merged = df1[columns_to_check].merge(df2[columns_to_check], 
#                                       how='outer', 
#                                       left_index=True, 
#                                       right_index=True, 
#                                       suffixes=('_df1', '_df2'), 
#                                       indicator=True)

# # Identify modified rows
# modified_rows = merged[merged['_merge'] != 'both']

# # Print missing elements
# missing_in_df1 = df2[~df2.index.isin(df1.index)]
# missing_in_df2 = df1[~df1.index.isin(df2.index)]

# print("Missing in df1:")
# print(missing_in_df1.to_string(index=False))

# print("\nMissing in df2:")
# print(missing_in_df2.to_string(index=False))

# # Print modified rows and show differences
# if not modified_rows.empty:
#     print("\nModified fields:")
#     for idx, row in modified_rows.iterrows():
#         diff = {}
#         for column in columns_to_check:
#             val_df1 = row[column + '_df1']
#             val_df2 = row[column + '_df2']
#             if pd.notna(val_df1) and pd.notna(val_df2) and val_df1 != val_df2:
#                 diff[column] = (val_df1, val_df2)
#         if diff:
#             print(f"Element: {idx}, Differences: {diff}")
# else:
#     print("No modified fields found.")

import pandas as pd
import sys

df = pd.read_csv(sys.argv[1])
# Display the first 5 rows of the DataFrame
print(df.head())
print(type(df[1]))
print(type(df[1][0]))
print(type(df[1][1]))
print(type(df[1][2]))

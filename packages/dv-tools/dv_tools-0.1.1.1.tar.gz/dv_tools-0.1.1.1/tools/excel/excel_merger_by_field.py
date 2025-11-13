
import pandas as pd

file1 = 'productos.xlsx'
file2 = 'merged_excel.xlsx'

df1 = pd.read_excel(file1)
df2 = pd.read_excel(file2)

df_merged = pd.merge(df1, df2, on='NOMBRE', how='inner')

df_merged.to_excel('resultado_filtrado.xlsx', index=False)
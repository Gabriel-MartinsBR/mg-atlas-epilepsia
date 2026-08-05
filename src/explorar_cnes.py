from pysus import cnes
import pandas as pd

# Baixa os profissionais do CNES de MG para uma competência de referência (dez/2022,
# mesmo mês final do período das internações, pra manter coerência temporal)
df = cnes(state='MG', year=2022, month=12, group='PF', as_dataframe=True)

print("Formato:", df.shape)
print("\nColunas disponíveis:")
print(df.columns.tolist())
print("\nPrimeiras linhas:")
print(df.head())
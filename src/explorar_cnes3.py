import pandas as pd

df = pd.read_parquet('cnes_pf_mg_202212.parquet')

# Verifica os valores de CBO que contêm "23" no meio (faixa de médicos clínicos/especialistas)
cbo_medicos = df[df['CBO'].astype(str).str.startswith('2231') | df['CBO'].astype(str).str.startswith('2251')]
print("Códigos CBO únicos nessa faixa:")
print(cbo_medicos['CBO'].value_counts().head(20))
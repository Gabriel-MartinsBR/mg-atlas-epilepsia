import pyreaddbc
from dbfread import DBF
import pandas as pd

nome_dbc = 'PFMG2212.dbc'
nome_dbf = 'PFMG2212.dbf'

# ---------------------------------------------------------
# Converte .dbc -> .dbf
# ---------------------------------------------------------
print("Convertendo .dbc para .dbf...")
pyreaddbc.dbc2dbf(nome_dbc, nome_dbf)
print("Conversão concluída.")

# ---------------------------------------------------------
# Lê o .dbf e transforma em DataFrame
# ---------------------------------------------------------
print("\nLendo o .dbf...")
tabela = DBF(nome_dbf, encoding='iso-8859-1')
df = pd.DataFrame(iter(tabela))

print("Formato:", df.shape)
print("\nColunas disponíveis:")
print(df.columns.tolist())
print("\nPrimeiras linhas:")
print(df.head())

# ---------------------------------------------------------
# Salva como parquet
# ---------------------------------------------------------
df.to_parquet('cnes_pf_mg_202212.parquet', index=False)
print("\nArquivo salvo: cnes_pf_mg_202212.parquet")
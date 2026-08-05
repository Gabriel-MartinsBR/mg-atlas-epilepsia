import ftplib
import pyreaddbc
import pandas as pd

# ---------------------------------------------------------
# 1) Baixa o arquivo .dbc direto do FTP do DATASUS
#    Padrão de nome: PF (Profissionais) + MG (estado) + AAMM (ano/mês) + .dbc
#    Vamos usar dez/2022, mesmo mês final do período das internações
# ---------------------------------------------------------
nome_arquivo = 'PFMG2212.dbc'
caminho_ftp = 'dissemin/publicos/CNES/200508_/Dados/PF/'

print(f"Conectando ao FTP do DATASUS e baixando {nome_arquivo}...")

with ftplib.FTP('ftp.datasus.gov.br') as ftp:
    ftp.login()  # login anônimo, sem senha
    ftp.cwd(caminho_ftp)
    with open(nome_arquivo, 'wb') as f:
        ftp.retrbinary(f'RETR {nome_arquivo}', f.write)

print(f"Download concluído: {nome_arquivo}")

# ---------------------------------------------------------
# 2) Converte o .dbc para DataFrame
# ---------------------------------------------------------
print("\nConvertendo para DataFrame...")
df = pyreaddbc.read_dbc(nome_arquivo, encoding='iso-8859-1')

print("Formato:", df.shape)
print("\nColunas disponíveis:")
print(df.columns.tolist())
print("\nPrimeiras linhas:")
print(df.head())

# ---------------------------------------------------------
# 3) Salva como parquet, pra não precisar baixar de novo depois
# ---------------------------------------------------------
df.to_parquet('cnes_pf_mg_202212.parquet', index=False)
print("\nArquivo salvo: cnes_pf_mg_202212.parquet")
import sidrapy
import pandas as pd
import time

def limpar_tabela_sidra(df):
    """Remove a primeira linha de cabeçalho descritivo que a API do SIDRA retorna."""
    return df.iloc[1:].reset_index(drop=True)

def filtrar_mg(df, col_codigo='D1C'):
    """Mantém apenas municípios de Minas Gerais (código IBGE começa com 31)."""
    return df[df[col_codigo].astype(str).str.startswith('31')].copy()

def filtrar_total_sexo(df):
    """Encontra a coluna de classificação (sexo) e mantém somente a categoria 'Total'."""
    colunas_classificacao = [c for c in df.columns if c.startswith('D') and c.endswith('N') and c != 'D1N']
    for col in colunas_classificacao:
        if 'Total' in df[col].unique():
            return df[df[col] == 'Total'].copy()
    raise ValueError(
        "Não encontrei uma coluna de classificação com a categoria 'Total'. "
        f"Colunas disponíveis: {df.columns.tolist()}"
    )

# ---------------------------------------------------------
# 1) Censo 2010 - Tabela 200 (variável 93 = população residente, classificação 2 = sexo)
# ---------------------------------------------------------
print("Baixando população do Censo 2010 (tabela 200)...")
df_2010 = sidrapy.get_table(
    table_code='200',
    territorial_level='6',
    ibge_territorial_code='all',
    period='2010',
    variable='93',
    classification='2/all'
)
df_2010 = limpar_tabela_sidra(df_2010)
df_2010 = filtrar_total_sexo(df_2010)
df_2010 = filtrar_mg(df_2010)
df_2010 = df_2010[['D1C', 'D1N', 'V']].rename(
    columns={'D1C': 'codigo_municipio', 'D1N': 'nome_municipio', 'V': 'populacao'})
df_2010['ano'] = 2010

# ---------------------------------------------------------
# 2) Estimativas 2011-2021 - Tabela 6579 (sem classificação, um valor por município/ano)
# ---------------------------------------------------------
lista_estimativas = []
for ano in range(2011, 2022):
    print(f"Baixando estimativa de {ano} (tabela 6579)...")
    df_ano = sidrapy.get_table(
        table_code='6579',
        territorial_level='6',
        ibge_territorial_code='all',
        period=str(ano)
    )
    df_ano = limpar_tabela_sidra(df_ano)
    df_ano = filtrar_mg(df_ano)
    df_ano = df_ano[['D1C', 'D1N', 'V']].rename(
        columns={'D1C': 'codigo_municipio', 'D1N': 'nome_municipio', 'V': 'populacao'})
    df_ano['ano'] = ano
    lista_estimativas.append(df_ano)
    time.sleep(1)  # evita sobrecarregar a API do IBGE

df_estimativas = pd.concat(lista_estimativas, ignore_index=True)

# ---------------------------------------------------------
# 3) Censo 2022 - Tabela 9514 (variável 93, classificação 2 = sexo)
# ---------------------------------------------------------
print("Baixando população do Censo 2022 (tabela 9514)...")
df_2022 = sidrapy.get_table(
    table_code='9514',
    territorial_level='6',
    ibge_territorial_code='all',
    period='2022',
    variable='93',
    classification='2/all'
)
df_2022 = limpar_tabela_sidra(df_2022)
df_2022 = filtrar_total_sexo(df_2022)
df_2022 = filtrar_mg(df_2022)
df_2022 = df_2022[['D1C', 'D1N', 'V']].rename(
    columns={'D1C': 'codigo_municipio', 'D1N': 'nome_municipio', 'V': 'populacao'})
df_2022['ano'] = 2022

# ---------------------------------------------------------
# 4) 2023 - sem estimativa própria publicada; repete o valor do Censo 2022
#    (limitação a ser registrada explicitamente na Metodologia)
# ---------------------------------------------------------
df_2023 = df_2022.copy()
df_2023['ano'] = 2023

# ---------------------------------------------------------
# Junta tudo em uma única tabela final
# ---------------------------------------------------------
populacao_mg = pd.concat([df_2010, df_estimativas, df_2022, df_2023], ignore_index=True)
populacao_mg['populacao'] = pd.to_numeric(populacao_mg['populacao'], errors='coerce')
populacao_mg = populacao_mg.sort_values(['codigo_municipio', 'ano']).reset_index(drop=True)

print(populacao_mg.head(15))
print(f"\nTotal de linhas: {len(populacao_mg)}")
print(f"Municípios únicos: {populacao_mg['codigo_municipio'].nunique()}")
print(f"Anos cobertos: {sorted(populacao_mg['ano'].unique())}")

populacao_mg.to_csv('populacao_mg_2010_2023.csv', index=False, encoding='utf-8-sig')
print("\nArquivo salvo: populacao_mg_2010_2023.csv")
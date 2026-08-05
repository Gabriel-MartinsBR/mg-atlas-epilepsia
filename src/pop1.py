import pandas as pd
import geopandas as gpd

# ---------------------------------------------------------
# 1) Carrega e filtra as internações (só residentes de MG)
# ---------------------------------------------------------
internacoes = pd.read_csv('internacoes_epilepsia_mg_2015_2023 (1).csv')
internacoes['MUNIC_RES'] = internacoes['MUNIC_RES'].astype(str)
internacoes = internacoes[internacoes['MUNIC_RES'].str.startswith('31')]

print("Período real dos dados (ANO_CMPT):",
      internacoes['ANO_CMPT'].min(), "a", internacoes['ANO_CMPT'].max())
anos_estudo = sorted(internacoes['ANO_CMPT'].unique())

# Agrega total de internações por município no período todo
internacoes_agregado = (
    internacoes
    .groupby('MUNIC_RES')
    .size()
    .reset_index(name='n_internacoes')
)

# ---------------------------------------------------------
# 2) Carrega a população e soma "pessoas-ano" no MESMO período
# ---------------------------------------------------------
populacao = pd.read_csv('populacao_mg_2010_2023.csv')
populacao = populacao[populacao['ano'].isin(anos_estudo)]  # só os anos que existem nas internações

# cria a chave de 6 dígitos (mesmo padrão do DATASUS, sem dígito verificador)
populacao['munic_res'] = populacao['codigo_municipio'].astype(str).str[:6]

pessoas_ano = (
    populacao
    .groupby('munic_res')['populacao']
    .sum()
    .reset_index(name='soma_populacao_periodo')
)

print(f"\nAnos usados no denominador: {anos_estudo}")
print(f"Número de anos: {len(anos_estudo)}")

# ---------------------------------------------------------
# 3) Carrega a malha (garante que TODOS os 853 municípios apareçam)
# ---------------------------------------------------------
mg = gpd.read_file('mg_municipios.gpkg')
mg['munic_res'] = mg['code_muni'].astype(str).str[:6]

# ---------------------------------------------------------
# 4) Junta tudo: malha + internações + população
# ---------------------------------------------------------
gdf = mg.merge(internacoes_agregado, left_on='munic_res', right_on='MUNIC_RES', how='left')
gdf = gdf.merge(pessoas_ano, on='munic_res', how='left')

gdf['n_internacoes'] = gdf['n_internacoes'].fillna(0).astype(int)

# ---------------------------------------------------------
# 5) Calcula a taxa média anual de internação por 100.000 habitantes
# ---------------------------------------------------------
gdf['taxa_internacao_100k'] = (gdf['n_internacoes'] / gdf['soma_populacao_periodo']) * 100000

print("\nConferência:")
print(f"Total de municípios: {len(gdf)}")
print(f"Municípios sem nenhuma internação no período: {(gdf['n_internacoes'] == 0).sum()}")
print(f"Municípios sem dado de população (verificar!): {gdf['soma_populacao_periodo'].isnull().sum()}")

print("\nTop 10 maiores taxas:")
print(gdf[['name_muni', 'n_internacoes', 'soma_populacao_periodo', 'taxa_internacao_100k']]
      .sort_values('taxa_internacao_100k', ascending=False).head(10))

print("\nTop 10 menores taxas (excluindo municípios sem internação, que dão taxa 0):")
print(gdf[gdf['n_internacoes'] > 0][['name_muni', 'n_internacoes', 'soma_populacao_periodo', 'taxa_internacao_100k']]
      .sort_values('taxa_internacao_100k').head(10))

# ---------------------------------------------------------
# 6) Salva o resultado
# ---------------------------------------------------------
if 'MUNIC_RES' in gdf.columns:
    gdf = gdf.drop(columns=['MUNIC_RES'])

gdf.to_file('mg_taxa_internacao_epilepsia.gpkg', driver='GPKG')
gdf.drop(columns='geometry').to_csv('mg_taxa_internacao_epilepsia.csv', index=False, encoding='utf-8-sig')
print("\nArquivos salvos: mg_taxa_internacao_epilepsia.gpkg e .csv")
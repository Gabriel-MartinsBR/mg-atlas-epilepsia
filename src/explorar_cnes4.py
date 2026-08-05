import pandas as pd
import geopandas as gpd

# ---------------------------------------------------------
# 1) Carrega os dados do CNES
# ---------------------------------------------------------
df = pd.read_parquet('cnes_pf_mg_202212.parquet')

# ---------------------------------------------------------
# 2) Filtra só neurologistas (CBO 225112)
# ---------------------------------------------------------
neurologistas = df[df['CBO'].astype(str) == '225112'].copy()
print(f"Total de vínculos de neurologista em MG (dez/2022): {len(neurologistas)}")

# ---------------------------------------------------------
# 3) Conta neurologistas ÚNICOS por município (evita contar
#    duplicado o mesmo profissional que atende em 2+ estabelecimentos
#    na mesma cidade)
# ---------------------------------------------------------
neurologistas_unicos = neurologistas.drop_duplicates(subset=['CODUFMUN', 'CPF_PROF'])
print(f"Vínculos únicos (profissional x município): {len(neurologistas_unicos)}")

neurologistas_por_municipio = (
    neurologistas_unicos
    .groupby('CODUFMUN')
    .size()
    .reset_index(name='n_neurologistas')
)

print(f"\nMunicípios de MG com pelo menos 1 neurologista: {len(neurologistas_por_municipio)}")
print("\nTop 10 municípios com mais neurologistas:")
print(neurologistas_por_municipio.sort_values('n_neurologistas', ascending=False).head(10))

# ---------------------------------------------------------
# 4) Junta com a malha (garante que TODOS os 853 municípios apareçam,
#    mesmo os que têm ZERO neurologista - isso é informação importante!)
# ---------------------------------------------------------
mg = gpd.read_file('mg_municipios.gpkg')
mg['munic_res'] = mg['code_muni'].astype(str).str[:6]

gdf = mg.merge(
    neurologistas_por_municipio,
    left_on='munic_res', right_on='CODUFMUN',
    how='left'
)
gdf['n_neurologistas'] = gdf['n_neurologistas'].fillna(0).astype(int)

print(f"\nMunicípios SEM nenhum neurologista: {(gdf['n_neurologistas'] == 0).sum()} de {len(gdf)}")

# ---------------------------------------------------------
# 5) Calcula neurologistas por 100 mil habitantes (usando população de 2022,
#    mesma competência de referência do CNES)
# ---------------------------------------------------------
populacao = pd.read_csv('populacao_mg_2010_2023.csv')
pop_2022 = populacao[populacao['ano'] == 2022].copy()
pop_2022['munic_res'] = pop_2022['codigo_municipio'].astype(str).str[:6]

gdf = gdf.merge(pop_2022[['munic_res', 'populacao']], on='munic_res', how='left')
gdf['neurologistas_100k'] = (gdf['n_neurologistas'] / gdf['populacao']) * 100000

print("\nEstatística de neurologistas por 100k habitantes:")
print(gdf['neurologistas_100k'].describe())

if 'CODUFMUN' in gdf.columns:
    gdf = gdf.drop(columns=['CODUFMUN'])

# ---------------------------------------------------------
# 6) Salva
# ---------------------------------------------------------
gdf.to_file('mg_neurologistas.gpkg', driver='GPKG')
gdf.drop(columns='geometry').to_csv('mg_neurologistas.csv', index=False, encoding='utf-8-sig')
print("\nArquivos salvos: mg_neurologistas.gpkg e .csv")
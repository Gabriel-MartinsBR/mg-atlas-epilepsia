import pandas as pd
import geopandas as gpd

# Carrega os dois datasets
internacoes = pd.read_csv('internacoes_epilepsia_mg_2015_2023 (1).csv')
mg = gpd.read_file('mg_municipios.gpkg')

# Cria a chave de 6 dígitos na malha (remove o dígito verificador)
mg['munic_res'] = mg['code_muni'].astype(str).str[:6].astype(int)

# Confere que os dois lados batem
print("Municípios na malha:", mg['munic_res'].nunique())
print("Municípios nas internações:", internacoes['MUNIC_RES'].nunique())

# Agrega internações por município (conta total de internações no período)
internacoes_agregado = (
    internacoes
    .groupby('MUNIC_RES')
    .size()
    .reset_index(name='n_internacoes')
)

# Faz o merge: mantém TODOS os municípios da malha (how='left'),
# mesmo os que tiveram zero internações no período
gdf = mg.merge(
    internacoes_agregado,
    left_on='munic_res',
    right_on='MUNIC_RES',
    how='left'
)

# Municípios sem internação no período viram NaN -> substitui por 0
gdf['n_internacoes'] = gdf['n_internacoes'].fillna(0).astype(int)

print("\nTotal de municípios após merge:", len(gdf))
print("Municípios sem nenhuma internação no período:", (gdf['n_internacoes'] == 0).sum())
print(gdf[['name_muni', 'n_internacoes']].sort_values('n_internacoes', ascending=False).head(10))

# Remove coluna duplicada (colide com 'munic_res' no GeoPackage, que não diferencia maiúsculas)
gdf = gdf.drop(columns=['MUNIC_RES'])

# Salva o resultado
gdf.to_file('mg_internacoes_epilepsia.gpkg', driver='GPKG')
print("\nArquivo salvo: mg_internacoes_epilepsia.gpkg")
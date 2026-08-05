import geopandas as gpd
import libpysal
from libpysal.weights import Queen
from esda.smoothing import Spatial_Empirical_Bayes
import numpy as np

# ---------------------------------------------------------
# 1) Carrega os dados já com a taxa bruta calculada
# ---------------------------------------------------------
gdf = gpd.read_file('mg_taxa_internacao_epilepsia.gpkg')
print("Municípios carregados:", len(gdf))

# ---------------------------------------------------------
# 2) Constrói a matriz de vizinhança espacial (contiguidade Queen)
#    Queen = considera vizinho qualquer município que compartilhe
#    fronteira ou até um único ponto de contato
# ---------------------------------------------------------
w = Queen.from_dataframe(gdf, use_index=False)
w.id_order = list(range(len(gdf)))  # alinha a ordem da matriz com a ordem das linhas do gdf

# Verifica se existem "ilhas" (municípios sem nenhum vizinho) -
# isso quebraria a suavização local pra esses casos
ilhas = w.islands
print(f"\nMunicípios sem vizinhos (ilhas): {len(ilhas)}")
if len(ilhas) > 0:
    print("Índices das ilhas:", ilhas)
    print(gdf.iloc[ilhas][['name_muni']])

# ---------------------------------------------------------
# 3) Aplica a Suavização Bayesiana Empírica Local
#    e = número de eventos (internações)
#    b = população em risco (soma de pessoas-ano no período)
# ---------------------------------------------------------
e = gdf['n_internacoes'].values
b = gdf['soma_populacao_periodo'].values

eb_local = Spatial_Empirical_Bayes(e, b, w)

# O resultado (.r) vem como taxa "por 1 habitante" -> multiplicamos por 100.000
gdf['taxa_suavizada_100k'] = eb_local.r * 100000

# ---------------------------------------------------------
# 4) Compara a taxa bruta com a suavizada
# ---------------------------------------------------------
print("\nComparação - taxa bruta vs. suavizada (10 maiores taxas BRUTAS):")
comparacao = gdf[['name_muni', 'n_internacoes', 'taxa_internacao_100k', 'taxa_suavizada_100k']]
print(comparacao.sort_values('taxa_internacao_100k', ascending=False).head(10))

print("\nEstatísticas descritivas:")
print("Taxa bruta      - desvio padrão:", gdf['taxa_internacao_100k'].std().round(2))
print("Taxa suavizada  - desvio padrão:", gdf['taxa_suavizada_100k'].std().round(2))

# ---------------------------------------------------------
# 5) Salva o resultado
# ---------------------------------------------------------
gdf.to_file('mg_taxa_suavizada_epilepsia.gpkg', driver='GPKG')
gdf.drop(columns='geometry').to_csv('mg_taxa_suavizada_epilepsia.csv', index=False, encoding='utf-8-sig')
print("\nArquivos salvos: mg_taxa_suavizada_epilepsia.gpkg e .csv")
import geopandas as gpd
import matplotlib.pyplot as plt
from libpysal.weights import Queen
from esda.moran import Moran_Local
from splot.esda import lisa_cluster

# ---------------------------------------------------------
# 1) Carrega os dados com a taxa já suavizada
# ---------------------------------------------------------
gdf = gpd.read_file('mg_taxa_suavizada_epilepsia.gpkg')
print("Municípios carregados:", len(gdf))

# ---------------------------------------------------------
# 2) Reconstrói a matriz de vizinhança (mesma de sempre)
# ---------------------------------------------------------
w = Queen.from_dataframe(gdf, use_index=False)
w.id_order = list(range(len(gdf)))
w.transform = 'r'

# ---------------------------------------------------------
# 3) Calcula o Índice de Moran Local (LISA)
# ---------------------------------------------------------
y = gdf['taxa_suavizada_100k'].values
lisa = Moran_Local(y, w, permutations=999, seed=42)

# ---------------------------------------------------------
# 4) Classifica cada município em um dos 5 grupos:
#    1 = Alto-Alto (HH)   -> cluster de alta internação
#    2 = Baixo-Baixo (LL) -> cluster de baixa internação
#    3 = Baixo-Alto (LH)  -> outlier (baixo rodeado de alto)
#    4 = Alto-Baixo (HL)  -> outlier (alto rodeado de baixo)
#    0 = Não significativo
# ---------------------------------------------------------
gdf['lisa_q'] = lisa.q            # quadrante (1,2,3,4)
gdf['lisa_p'] = lisa.p_sim        # p-valor de cada município

sig = gdf['lisa_p'] < 0.05

mapa_categorias = {1: 'Alto-Alto (HH)', 2: 'Baixo-Alto (LH)', 3: 'Baixo-Baixo (LL)', 4: 'Alto-Baixo (HL)'}
gdf['cluster'] = 'Não significativo'
gdf.loc[sig, 'cluster'] = gdf.loc[sig, 'lisa_q'].map(mapa_categorias)

# ---------------------------------------------------------
# 5) Resumo dos clusters encontrados
# ---------------------------------------------------------
print("\nContagem de municípios por categoria de cluster (p < 0.05):")
print(gdf['cluster'].value_counts())

print("\nMunicípios do cluster Alto-Alto (focos de alta internação cercados de vizinhos também altos):")
print(gdf[gdf['cluster'] == 'Alto-Alto (HH)'][['name_muni', 'taxa_suavizada_100k']]
      .sort_values('taxa_suavizada_100k', ascending=False))

print("\nMunicípios do cluster Baixo-Baixo (áreas de baixa internação, cercadas de vizinhos também baixos):")
print(gdf[gdf['cluster'] == 'Baixo-Baixo (LL)'][['name_muni', 'taxa_suavizada_100k']]
      .sort_values('taxa_suavizada_100k').head(15))

# ---------------------------------------------------------
# 6) Gera o mapa de clusters (LISA cluster map)
# ---------------------------------------------------------
fig, ax = lisa_cluster(lisa, gdf, p=0.05, figsize=(10, 10))
ax.set_title("Clusters LISA - Taxa de internação por epilepsia/EME (MG, 2010-2022)", fontsize=13)
plt.savefig('mapa_lisa_clusters.png', dpi=200, bbox_inches='tight')
print("\nMapa salvo: mapa_lisa_clusters.png")
plt.close()

# ---------------------------------------------------------
# 7) Salva os resultados completos
# ---------------------------------------------------------
gdf.to_file('mg_resultado_lisa.gpkg', driver='GPKG')
gdf.drop(columns='geometry').to_csv('mg_resultado_lisa.csv', index=False, encoding='utf-8-sig')
print("Arquivos salvos: mg_resultado_lisa.gpkg, .csv e mapa_lisa_clusters.png")
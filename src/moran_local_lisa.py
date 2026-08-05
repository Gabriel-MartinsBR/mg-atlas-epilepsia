# ============================================================
# Moran Local (LISA) - Internacoes por Epilepsia/EME em MG (2015-2022)
# Etapa 5 do projeto: identificar clusters espaciais
# ============================================================

import geopandas as gpd
import libpysal as lps
from esda.moran import Moran_Local
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ----------------------------------------------------------------
# 1. Carregar o resultado da etapa anterior (Moran Global)
# ----------------------------------------------------------------
gdf = gpd.read_file("resultado_moran_global_2015_2022.gpkg")
print(f"Malha carregada: {gdf.shape}")

# Variavel de entrada: taxa suavizada (Empirical Bayes espacial)
# -> usamos a suavizada, nao a bruta, pelo mesmo motivo da etapa 4:
#    a bruta tem instabilidade estatistica em municipios pequenos,
#    que contaminaria o LISA com falsos clusters/outliers.
y = gdf["TAXA_SUAVIZADA_EB_100MIL"].values

# ----------------------------------------------------------------
# 2. Matriz de vizinhanca (Queen) - mesma logica da etapa 4
# ----------------------------------------------------------------
w = lps.weights.Queen.from_dataframe(gdf, use_index=False)
w.transform = "r"  # padronizacao em linha (row-standardized)

ilhas = (w.cardinalities == 0)
n_ilhas = sum(1 for v in w.cardinalities.values() if v == 0)
print(f"Municipios sem nenhum vizinho (ilhas): {n_ilhas}")

# IMPORTANTE: alinhar a ordem do y com a ordem da matriz w
# (mesmo ajuste de id_order que corrigiu o erro na etapa 4)
gdf = gdf.reset_index(drop=True)
y = gdf["TAXA_SUAVIZADA_EB_100MIL"].values

# ----------------------------------------------------------------
# 3. Moran Local (LISA)
# ----------------------------------------------------------------
np.random.seed(12345)  # reprodutibilidade das permutacoes
lisa = Moran_Local(y, w, permutations=999)

gdf["LISA_Ii"] = lisa.Is           # estatistica local
gdf["LISA_p"] = lisa.p_sim         # p-valor (pseudo, via permutacao)
gdf["LISA_q"] = lisa.q             # quadrante (1=HH, 2=LH, 3=LL, 4=HL)

# ----------------------------------------------------------------
# 4. Classificar clusters com base na significancia
# ----------------------------------------------------------------
SIGNIF = 0.05

quadrante_nome = {
    1: "High-High",   # taxa alta rodeada de taxa alta
    2: "Low-High",    # taxa baixa rodeada de taxa alta (outlier)
    3: "Low-Low",     # taxa baixa rodeada de taxa baixa
    4: "High-Low",    # taxa alta rodeada de taxa baixa (outlier)
}

def classificar(row):
    if row["LISA_p"] > SIGNIF:
        return "Nao significativo"
    return quadrante_nome[row["LISA_q"]]

gdf["LISA_cluster"] = gdf.apply(classificar, axis=1)

# ----------------------------------------------------------------
# 5. Resumo numerico
# ----------------------------------------------------------------
print("\n" + "=" * 60)
print(f"MORAN LOCAL (LISA) - taxa suavizada, 2015-2022 (p < {SIGNIF})")
print("=" * 60)
resumo = gdf["LISA_cluster"].value_counts()
print(resumo)
print(f"\nTotal de municipios com cluster/outlier significativo: "
      f"{(gdf['LISA_cluster'] != 'Nao significativo').sum()} de {len(gdf)}")

# Listar os municipios High-High (foco prioritario de vigilancia)
print("\n--- Municipios High-High (cluster de taxa alta), ordenados pela taxa ---")
hh = gdf[gdf["LISA_cluster"] == "High-High"].sort_values(
    "TAXA_SUAVIZADA_EB_100MIL", ascending=False
)
print(hh[["name_muni", "TAXA_SUAVIZADA_EB_100MIL", "LISA_p"]].to_string(index=False))

# Listar os outliers (High-Low e Low-High), sao os casos mais interessantes
# de investigar caso a caso (ex.: municipio-polo com centro de referencia)
print("\n--- Outliers espaciais (High-Low / Low-High) ---")
outliers = gdf[gdf["LISA_cluster"].isin(["High-Low", "Low-High"])].sort_values(
    "LISA_cluster"
)
print(outliers[["name_muni", "TAXA_SUAVIZADA_EB_100MIL", "LISA_cluster", "LISA_p"]].to_string(index=False))

# ----------------------------------------------------------------
# 6. Mapa dos clusters LISA
# ----------------------------------------------------------------
cores = {
    "High-High": "#d7191c",       # vermelho forte
    "Low-Low": "#2c7bb6",         # azul forte
    "High-Low": "#fdae61",       # laranja (outlier)
    "Low-High": "#abd9e9",       # azul claro (outlier)
    "Nao significativo": "#f0f0f0",  # cinza claro
}

fig, ax = plt.subplots(1, 1, figsize=(10, 12))
for categoria, cor in cores.items():
    subset = gdf[gdf["LISA_cluster"] == categoria]
    if len(subset) > 0:
        subset.plot(ax=ax, color=cor, edgecolor="white", linewidth=0.2, label=categoria)

ax.set_title(
    "LISA - Clusters espaciais de internacao por Epilepsia/EME\n"
    "Minas Gerais, 2015-2022 (taxa suavizada, p<0.05)",
    fontsize=13,
)
ax.axis("off")

# Legenda customizada (ordem fixa, mais intuitiva que a ordem de plotagem)
legend_ordem = ["High-High", "Low-Low", "High-Low", "Low-High", "Nao significativo"]
handles = [mpatches.Patch(color=cores[c], label=c) for c in legend_ordem]
ax.legend(handles=handles, loc="lower left", fontsize=9, title="Cluster LISA")

plt.tight_layout()
plt.savefig("mapa_lisa_clusters_2015_2022.png", dpi=200, bbox_inches="tight")
print("\nMapa salvo: mapa_lisa_clusters_2015_2022.png")

# ----------------------------------------------------------------
# 7. Salvar resultado para uso posterior (cruzamento com CNES, etc.)
# ----------------------------------------------------------------
gdf.drop(columns="geometry").to_csv("resultado_lisa_2015_2022.csv", index=False)
gdf.to_file("resultado_lisa_2015_2022.gpkg", driver="GPKG")

print("\nArquivos salvos:")
print(" - resultado_lisa_2015_2022.csv (tabela)")
print(" - resultado_lisa_2015_2022.gpkg (com geometria, para mapear/cruzar depois)")
print(" - mapa_lisa_clusters_2015_2022.png (visualizacao)")
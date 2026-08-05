import geopandas as gpd
import libpysal
from libpysal.weights import Queen
from esda.moran import Moran

# ---------------------------------------------------------
# 1) Carrega os dados com a taxa já suavizada
# ---------------------------------------------------------
gdf = gpd.read_file('mg_taxa_suavizada_epilepsia.gpkg')
print("Municípios carregados:", len(gdf))

# ---------------------------------------------------------
# 2) Reconstrói a matriz de vizinhança (mesma lógica do passo anterior)
# ---------------------------------------------------------
w = Queen.from_dataframe(gdf, use_index=False)
w.id_order = list(range(len(gdf)))
w.transform = 'r'  # padronização por linha - necessária para o cálculo do Moran's I

# ---------------------------------------------------------
# 3) Calcula o Índice de Moran Global sobre a taxa suavizada
# ---------------------------------------------------------
y = gdf['taxa_suavizada_100k'].values
moran = Moran(y, w, permutations=999)

print(f"\nÍndice de Moran I: {moran.I:.4f}")
print(f"Valor esperado sob aleatoriedade espacial (E[I]): {moran.EI:.4f}")
print(f"p-valor (baseado em {moran.permutations} permutações): {moran.p_sim:.4f}")
print(f"z-score: {moran.z_sim:.4f}")

# ---------------------------------------------------------
# 4) Interpretação automática do resultado
# ---------------------------------------------------------
if moran.p_sim < 0.05:
    print("\n=> Resultado estatisticamente SIGNIFICATIVO (p < 0.05).")
    if moran.I > moran.EI:
        print("=> Autocorrelação espacial POSITIVA: municípios com taxas parecidas")
        print("   (altas perto de altas, baixas perto de baixas) tendem a se agrupar no espaço.")
    else:
        print("=> Autocorrelação espacial NEGATIVA: municípios com taxas diferentes")
        print("   tendem a ficar vizinhos (padrão tipo 'tabuleiro de xadrez').")
else:
    print("\n=> Resultado NÃO significativo (p >= 0.05).")
    print("=> Não há evidência de autocorrelação espacial - a distribuição da taxa")
    print("   parece ser aleatória no território, sem formação de clusters.")

# ---------------------------------------------------------
# 5) Salva um resumo em texto (útil pra colar direto no Resultados do projeto)
# ---------------------------------------------------------
with open('resultado_moran_global.txt', 'w', encoding='utf-8') as f:
    f.write("ÍNDICE DE MORAN GLOBAL - Taxa suavizada de internação por epilepsia/EME (MG, 2010-2022)\n")
    f.write(f"Moran's I: {moran.I:.4f}\n")
    f.write(f"E[I] (esperado sob aleatoriedade): {moran.EI:.4f}\n")
    f.write(f"p-valor (999 permutações): {moran.p_sim:.4f}\n")
    f.write(f"z-score: {moran.z_sim:.4f}\n")

print("\nArquivo salvo: resultado_moran_global.txt")
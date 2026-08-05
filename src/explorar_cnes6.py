import geopandas as gpd
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# 1) Carrega os dois resultados e junta em uma única tabela
# ---------------------------------------------------------
lisa = gpd.read_file('mg_resultado_lisa.gpkg')
neuro = pd.read_csv('mg_neurologistas.csv')

# junta pelo código do município (6 dígitos, padrão DATASUS)
lisa['munic_res'] = lisa['code_muni'].astype(str).str[:6]
neuro['munic_res'] = neuro['munic_res'].astype(str) if 'munic_res' in neuro.columns else neuro['code_muni'].astype(str).str[:6]

gdf = lisa.merge(
    neuro[['munic_res', 'n_neurologistas', 'neurologistas_100k']],
    on='munic_res', how='left'
)

print("Municípios após junção:", len(gdf))
print("Municípios sem dado de neurologista (verificar!):", gdf['n_neurologistas'].isnull().sum())

# ---------------------------------------------------------
# 2) Comparação descritiva: neurologistas por categoria de cluster
# ---------------------------------------------------------
print("\n=== Neurologistas por 100k habitantes, por categoria de cluster LISA ===")
resumo = gdf.groupby('cluster')['neurologistas_100k'].agg(['count', 'mean', 'median', 'std'])
print(resumo)

print("\n=== % de municípios SEM nenhum neurologista, por categoria de cluster ===")
sem_neuro = gdf.groupby('cluster')['n_neurologistas'].apply(lambda x: (x == 0).mean() * 100)
print(sem_neuro.round(1))

# ---------------------------------------------------------
# 3) Teste estatístico: HH (alta internação) tem MENOS acesso a
#    neurologista do que o resto do estado?
#    Usamos Mann-Whitney U (não-paramétrico) porque a variável
#    tem muitos zeros e distribuição bem assimétrica
# ---------------------------------------------------------
grupo_hh = gdf[gdf['cluster'] == 'Alto-Alto (HH)']['neurologistas_100k'].dropna()
grupo_resto = gdf[gdf['cluster'] != 'Alto-Alto (HH)']['neurologistas_100k'].dropna()

stat, p_valor = stats.mannwhitneyu(grupo_hh, grupo_resto, alternative='less')

print(f"\n=== Teste de Mann-Whitney U ===")
print(f"Mediana neurologistas/100k - Cluster HH: {grupo_hh.median():.2f}")
print(f"Mediana neurologistas/100k - Resto do estado: {grupo_resto.median():.2f}")
print(f"Estatística U: {stat:.1f}")
print(f"p-valor (H1: HH tem MENOS neurologistas que o resto): {p_valor:.4f}")

if p_valor < 0.05:
    print("=> SIGNIFICATIVO: municípios do cluster de alta internação têm,")
    print("   de fato, MENOS acesso a neurologista do que o restante do estado.")
else:
    print("=> NÃO significativo: não há evidência estatística de diferença")
    print("   no acesso a neurologista entre o cluster HH e o resto do estado.")

# ---------------------------------------------------------
# 4) Mapa comparativo: clusters LISA + marcação de municípios sem neurologista
# ---------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(18, 9))

cores = {'Alto-Alto (HH)': '#d73027', 'Baixo-Alto (LH)': '#abd9e9',
         'Baixo-Baixo (LL)': '#4575b4', 'Alto-Baixo (HL)': '#fdae61',
         'Não significativo': '#d9d9d9'}
gdf['cor'] = gdf['cluster'].map(cores)
gdf.plot(ax=axes[0], color=gdf['cor'], edgecolor='white', linewidth=0.2)
axes[0].set_title('Clusters LISA - Taxa de internação')
axes[0].axis('off')

gdf.plot(ax=axes[1], column='neurologistas_100k', cmap='YlGn',
         legend=True, edgecolor='white', linewidth=0.2,
         missing_kwds={'color': 'lightgrey'})
axes[1].set_title('Neurologistas por 100 mil habitantes')
axes[1].axis('off')

plt.tight_layout()
plt.savefig('mapa_comparativo_final.png', dpi=200, bbox_inches='tight')
print("\nMapa salvo: mapa_comparativo_final.png")
plt.close()

# ---------------------------------------------------------
# 5) Salva a base final consolidada
# ---------------------------------------------------------
gdf.drop(columns='cor').to_file('mg_resultado_final.gpkg', driver='GPKG')
gdf.drop(columns=['geometry', 'cor']).to_csv('mg_resultado_final.csv', index=False, encoding='utf-8-sig')
print("Arquivos salvos: mg_resultado_final.gpkg e .csv")
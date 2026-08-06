# Atlas da Epilepsia — Minas Gerais (2010–2023)

## Distribuição espacial das internações por epilepsia e estado de mal epiléptico em Minas Gerais: análise de autocorrelação espacial e sua relação com o acesso a serviços de neurologia

Projeto pessoal de estudo e prática que analisa a distribuição espacial das internações por epilepsia e estado de mal epiléptico (CID-10 G40 e G41) nos municípios de Minas Gerais, relacionando os padrões encontrados com a disponibilidade de neurologistas (CNES) em cada município.

## Objetivo

Identificar clusters espaciais de alta e baixa taxa de internação por epilepsia (análise LISA / Índice de Moran) e investigar sua relação com a distribuição de neurologistas no estado, apontando possíveis vazios assistenciais.

## Fontes de dados

- **SIH-SUS** (Sistema de Informações Hospitalares do SUS) — internações por epilepsia (G40) e estado de mal epiléptico (G41), via biblioteca `pysus`
- **CNES** (Cadastro Nacional de Estabelecimentos de Saúde) — número de neurologistas por município
- **IBGE / geobr** — malha municipal de Minas Gerais e dados populacionais (Censo)

## Métodos

- Cálculo de taxas de internação por 100 mil habitantes
- Suavização bayesiana das taxas (correção para municípios de baixa população)
- Índice de Moran Global (autocorrelação espacial)
- LISA (Local Indicators of Spatial Association) — identificação de clusters Alto-Alto, Baixo-Baixo, Alto-Baixo e Baixo-Alto
- Cruzamento dos clusters com a densidade de neurologistas por município

## Estrutura do repositório

```
├── src/            scripts Python (extração, tratamento, análise espacial)
├── resultados/      tabelas, mapas e resultados finais (arquivos leves)
├── docs/            atlas interativo em HTML
├── requirements.txt
└── .gitignore
```

**Observação:** dados brutos e intermediários (CNES bruto em `.dbf`/`.dbc`, extrações em `.parquet`, malhas e camadas espaciais em `.gpkg`/`.shp`) **não estão neste repositório** por serem grandes e regeneráveis a partir dos scripts em `src/`. Consulte os scripts de extração (`explorar_cnes*.py`, `tabnet.py`, `censo.py`) para reproduzir os dados originais.

## Como reproduzir

```bash

git clone https://github.com/Gabriel-MartinsBR/atlas-epilepsia-mg.git
cd atlas-epilepsia-mg

python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate   # Linux/Mac

pip install -r requirements.txt

# rodar os scripts na ordem: extração -> tratamento -> análise espacial
```

## Atlas interativo

O arquivo `docs/index.html` apresenta os resultados de forma interativa (mapas, gráficos e tabela filtrável por município). Pode ser visualizado localmente abrindo o arquivo no navegador, ou publicado via GitHub Pages.

## Autor

Gabriel, estudante de Medicina, UFTM (Universidade Federal do Triângulo Mineiro)

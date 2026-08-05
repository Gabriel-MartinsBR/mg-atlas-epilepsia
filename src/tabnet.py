import pandas as pd
from pysus.online_data.SIH import download


anos = range(2010, 2023)  
meses = range(1, 13)


registros = []


for ano in anos:
    for mes in meses:
        try:
            parquet_set = download('MG', ano, mes, groups=['RD'])
            df = parquet_set.to_dataframe()
           
            # Filtra epilepsia (G40) e estado de mal epiléptico (G41)
            df_filtrado = df[df['DIAG_PRINC'].str.startswith(('G40', 'G41'), na=False)]
           
            if len(df_filtrado) > 0:
                # Guarda só as colunas que interessam, já reduzindo o volume
                cols_interesse = ['MUNIC_RES', 'DIAG_PRINC', 'IDADE', 'SEXO',
                                   'RACA_COR', 'MORTE', 'ANO_CMPT', 'MES_CMPT']
                registros.append(df_filtrado[cols_interesse])
           
            print(f"{ano}-{mes:02d}: {len(df_filtrado)} internações G40/G41 de {len(df)} totais")
       
        except Exception as e:
            print(f"{ano}-{mes:02d}: ERRO - {e}")


# Junta tudo em um único DataFrame
df_final = pd.concat(registros, ignore_index=True)
print(f"\nTotal geral: {df_final.shape}")


# Salva em CSV
df_final.to_csv('internacoes_epilepsia_mg_2010_2023.csv', index=False)

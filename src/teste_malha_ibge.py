import geobr

mg = geobr.read_municipality(code_muni='MG', year=2020)
print('Número de municípios:', len(mg))
print(mg[['code_muni', 'name_muni']].head())



mg.to_file('mg_municipios.gpkg', driver='GPKG')
print('Malha salva com sucesso em mg_municipios.gpkg')
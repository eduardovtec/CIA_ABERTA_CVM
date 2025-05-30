import requests
import pandas as pd
import os
import zipfile
import re


def caracteres(df):
    def limpar(valor):
        if isinstance(valor, str):
            return re.sub(r'[\x00-\x1F]', '', valor)
        return valor
    for col in df.columns:
        df[col] = df[col].map(limpar)
    return df


pasta = os.getcwd()
os.chdir(f'{pasta}/dados_cvm')

if os.path.exists('dados_cvm.xlsx'):
    os.remove('dados_cvm.xlsx')

anos = range(2024, 2025)

url = 'https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/'

for ano in anos:
    
    download = requests.get(url + f'dfp_cia_aberta_{ano}.zip')

    open(f'dfp_cia_aberta_{ano}.zip', 'wb').write(download.content)


lista = list()

for arquivo in os.listdir(os.getcwd()):
    
    arquivo_zip = zipfile.ZipFile(arquivo)

    for planilha in arquivo_zip.namelist():

        csv = pd.read_csv(arquivo_zip.open(planilha), sep=';', encoding='ISO-8859-1', dtype={'ORDEM_EXERC': "category"})

        lista.append(csv)


dados = pd.concat(lista)

dados[['con_ind', 'tipo_dem']] = dados['GRUPO_DFP'].str.split('-', expand=True)
dados['con_ind'] = dados['con_ind'].str.strip()
dados['tipo_dem'] = dados['tipo_dem'].str.strip()

dados = dados[dados['ORDEM_EXERC'] != 'PENÚLTIMO']


empresas = ['WEG S.A.']
busca = dados[
    (dados['DENOM_CIA'].isin(empresas)) &
    (dados['tipo_dem'].isin([
        'Demonstração do Resultado',
        'Balanço Patrimonial Ativo',
        'Balanço Patrimonial Passivo'
        ])) &
    (dados['DS_CONTA'].isin([
        'Resultado Antes do Resultado Financeiro e dos Tributos',
        'Contas a Receber',
        'Estoques',
        'Ativos Biológicos',
        'Investimentos',
        'Imobilizado',
        'Intangível',
        'Empréstimos e Financiamentos',
        'Caixa e Equivalentes de Caixa'
    ])) &
    (dados['con_ind'] == 'DF Consolidado') 
]

df = caracteres(pd.DataFrame(busca))
df.to_excel('dados_cvm.xlsx', index=False)
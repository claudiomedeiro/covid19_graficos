#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Claudio Jorge Severo Medeiro"
__email__ = "cjinfo@gmail.com"
"""
    Download planilha com casos mundiais por país em https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-AAAA-MM-DD.xlsx
    
    exemplo:
    >>> wget https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-2020-03-28.xlsx

    Salvar planilha como .csv na raiz do diretório do programa e sem a data no nome
    exemplo: COVID-19-geographic-disbtribution-worldwide.xlsx

    Os volumes populacionais, por país, foram obtidos no site (https://www.worldometers.info/world-population/population-by-country/), 
    feito padronização dos nomes dos países com os nomes que o COVID-19-geographic-disbtribution-worldwide-2020-03-28.xlsx 
    traz e salvo na raiz do diretório do programa, apenas com as 02 colunas de interesse, e o nome  

    Seguintes países não consta população então fiz a pesquisa individualmente na internet:

    Palestine (5.073.681): https://www.worldometers.info/world-population/state-of-palestine-population/
    Kosovo (1.793.000): https://en.wikipedia.org/wiki/Demographics_of_Kosovo
    Jersey (107.700): https://www.gov.je/Government/JerseyInFigures/Population/Pages/PopulationProjections.aspx
    Guernsey (67.052): https://www.cia.gov/library/publications/the-world-factbook/geos/print_gk.html
    Bonaire, Saint Eustatius and Saba (25.157): https://www.paho.org/salud-en-las-americas-2017/?page_id=1694

    necessário instalar o tk e fazer o import
    $ sudo apt-get install python3-tk
"""


import tkinter      # precisa importar esta biblioteca senão não apresenta
import matplotlib
matplotlib.use('TkAgg')

# vet_numeros = []    # TODO: apagar depois
dic_paises = {}

int_qtde_casos_considerar = 100     # TODO: atualmente o default é considerar apenas a partir do dia com 100 casos no país,
                                    # mas o objetivo é permitir que o operador escolha também esse número

vet_paises_considerar = []
vet_dias_plotar = []
int_dias_pais_referencia = 0


def plotar_dimensao(int_dimensao=1, str_pais_referencia="Brazil", int_dia_depois_do_100th=0):
    """
    As dimensões possíveis são as seguintes:
    1: "CasosAcumulados"
    2: "MortesAcumuladas"
    3: "Casos acumulados divididos pela população"
    4: "Mortes divididas pelo número de casos acumulados"
    :return:
    """
    
    global dic_paises
    global vet_paises_considerar, vet_dias_plotar, int_dias_pais_referencia # TODO: apagar depois

    vet_simbolos = ['.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', '8', 's', 'p', 'P', '*', 'h', 'H', '+', 'x', 'X', 'D', 'd', '|']
    # vet_estilo = ['-', '--', '-.', ':', 'None', ' ', '', 'solid', 'dashed', 'dashdot', 'dotted']
    #

    mpl_plotar = matplotlib.pyplot

    vet_paises_considerar = []

    int_dias_pais_referencia = len(dic_paises[str_pais_referencia]["valores"])

    if (int_dia_depois_do_100th < int_dias_pais_referencia) and (int_dia_depois_do_100th > 0):
        print("Considerando o dia indicado")
        int_dias_pais_referencia = int_dia_depois_do_100th
    else:
        print("Considerando o último dia apurado para o país '{}'".format(str_pais_referencia))

    vet_dias_plotar = retorna_coluna_matriz(dic_paises[str_pais_referencia]["valores"], 0)[:int_dias_pais_referencia]

    if int_dimensao == 1:
        str_titulo = "Casos acumulados no {}".format(str_pais_referencia)
    elif int_dimensao == 2:
        str_titulo = "Mortes acumuladas no {}".format(str_pais_referencia)
    elif int_dimensao == 3:
        str_titulo = "Casos acumulados ref População no {}".format(str_pais_referencia)
    elif int_dimensao == 4:
        str_titulo = "Mortes ref Casos Acumulados no {}".format(str_pais_referencia)
    else:
        print("Dimensão não prevista")
        return

    mpl_plotar.title(str_titulo)

    int_cont = 0
    # int_cont_estilo = 0
    for str_pais in dic_paises.keys():
        # só vai plotar países que tem mais ou a mesma quantidade de dias indicados no país de referência
        if len(dic_paises[str_pais]["valores"]) >= int_dias_pais_referencia:
            # só vai plotar países que no dia ref ao último da série histórica do dia de referência, tinham a mesma quantidade de casos ou mais
            if dic_paises[str_pais]["valores"][int_dias_pais_referencia - 1] >= dic_paises[str_pais_referencia]["valores"][int_dias_pais_referencia - 1]:
                vet_paises_considerar.append(str_pais)
                vet_valores_plotar = retorna_coluna_matriz(dic_paises[str_pais]["valores"][:int_dias_pais_referencia], int_dimensao)

                if str_pais == str_pais_referencia:
                    # str_simbolo = "v"
                    str_estilo = "solid"
                else:
                    # str_simbolo = ""
                    str_estilo = "dotted"

                mpl_plotar.plot(vet_dias_plotar, vet_valores_plotar, marker=vet_simbolos[int_cont], linestyle=str_estilo)

                int_cont += 1
                if int_cont > len(vet_simbolos):
                    int_cont = 0

                # if int_cont_estilo > len(vet_estilo):
                #     int_cont_estilo = 0

                print("\nstr_pais: {}\nvet_dias_plotar: {}\nvalores: {}\nint_dimensao: {}".format(str_pais, vet_dias_plotar, vet_valores_plotar, int_dimensao))

    mpl_plotar.legend(vet_paises_considerar)  # as legendas devem estar em uma lista
    # mpl_plotar.figure()

    # axes = mpl_plotar.gca()
    # axes.set_xlim(0, 30)
    # axes.set_ylim(0, 1000)
    # axes.set_xticklabels([])
    # axes.set_yticklabels([])


    mpl_plotar.grid()
    mpl_plotar.show()
    return


def retorna_coluna_matriz(vet_matriz, int_coluna):
    """
    Recebe uma matriz e retorna a coluna indicada
    :param vet_matriz:
    :param int_coluna:
    :return:
    >>> retorna_coluna_matriz([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 1)
    [2, 5, 8]
    """
    return([x[int_coluna] for x in vet_matriz])


def abre_arquivo(str_arquivo):
    """
    Recebe o nome do arquivo, abre-o, e coloca em um vetor em que cada
    posição é uma linha.

    Retorna no vetor e o último elemento tem um '\n' que depois precisa ser
    tirado em cada processo específico.
    """

    str_arquivo = str(str_arquivo)
    vet_linhas = []

    try:
        with open(str_arquivo, 'r') as fil_arquivo:
            vet_linhas = fil_arquivo.readlines()
            fil_arquivo.close()

    except IOError:
        # grava_log(("ERRO", "Problemas ao tentar ler o arquivo '" + str_arquivo + "'"))
        print(("ERRO: Problemas ao tentar ler o arquivo '{}'".format(str_arquivo)))

    return vet_linhas


def simbolos_a_esquerda(str_texto, int_tamanho, str_simbolo="0"):
    """
    Recebe um texto, e o devolve no tamanho indicado, preenchido com o símbolo indicado à esquerda
    :param str_texto:
    :param int_tamanho:
    :param str_simbolo:
    :return:

    >>> simbolos_a_esquerda("4", 3)
    '004'
    """
    str_texto_com_simbolos_a_esquerda = ((int_tamanho - len(str_texto)) * str_simbolo) + str_texto
    return(str_texto_com_simbolos_a_esquerda)


def converte_data(str_data_a_converter):
    """
    Data uma data no formato D/M/AAAA, converte em data formato AAAA-MM-DD
    :param str_data_a_converter:
    :return:

    >>> converte_data("18/4/2020")
    '2020-04-18'
    """
    vet_data_convertida = str_data_a_converter.split("/")
    str_dia = simbolos_a_esquerda(vet_data_convertida[0], 2)
    str_mes = simbolos_a_esquerda(vet_data_convertida[1], 2)
    str_ano = vet_data_convertida[2]
    str_data_convertida = str_ano + "-" + str_mes + "-" + str_dia
    return(str_data_convertida)


def importa_csv_numeros(str_nome_arquivo, vet_schema, str_separador=";"):
    """Acrescenta o conteudo de 'vet_arquivo' em uma estrutura de dicionário:

    O leiaute do arquivo de entrada deve ser como segue:

    dateRep;day;month;year;cases;deaths;countriesAndTerritories;geoId;countryterritoryCode;popData2018;DataNumerica;CasosAcumulados;MortesAcumuladas;DiasDesdeCaso100;População;CasosRefPopulacao;MortesRefCasos
    4/4/2020;4;4;2020;32425;1104;United_States_of_America;US;USA;327167434;43925;277965;7157;33;331.002.651;0,08398%;2,57478%
    3/4/2020;3;4;2020;28819;915;United_States_of_America;US;USA;327167434;43924;245540;6053;32;331.002.651;0,07418%;2,46518%
    2/4/2020;2;4;2020;27103;1059;United_States_of_America;US;USA;327167434;43923;216721;5138;31;331.002.651;0,06547%;2,37079%
    """

    vet_arquivo = abre_arquivo(str_nome_arquivo)
    vet_retorno = []

    for int_pos in range(1, len(vet_arquivo), 1):
        vet_campos = vet_arquivo[int_pos].split(str_separador)

        # Exclui o '\n' do ultimo campo
        vet_campos[-1] = vet_campos[-1].replace("\n", "")
        vet_campos[0] = converte_data(vet_campos[0])
        vet_campos[-1] = vet_campos[-1].replace(",", ".").replace("%", "")
        vet_campos[-2] = vet_campos[-2].replace(",", ".").replace("%", "")
        vet_campos[-3] = vet_campos[-3].replace(",", ".")
        vet_retorno.append(vet_campos)

    return(vet_retorno)


def importa_csv_populacao(str_nome_arquivo, vet_schema, str_separador=";"):
    """Acrescenta o conteudo de 'vet_arquivo' em uma estrutura de dicionário:

    O leiaute do arquivo de entrada deve ser como segue:

    countriesAndTerritories;População
    Afghanistan;38928346
    Albania;2877797
    Algeria;43851044
    """

    vet_arquivo = abre_arquivo(str_nome_arquivo)
    dic_retorno = {}

    for int_pos in range(1, len(vet_arquivo), 1):
        vet_campos = vet_arquivo[int_pos].split(str_separador)

        # Exclui o '\n' do ultimo campo
        vet_campos[-1] = vet_campos[-1].replace("\n", "")
        dic_retorno[vet_campos[0]] = int(vet_campos[1])
        # vet_retorno.append(vet_campos)

    return(dic_retorno)



def main():
    """
    TODO: Ordenar os países por maior volume no mesmo dia que o Brazil está
    :return:
    """
    # global vet_numeros  # TODO: apagar depois
    global dic_paises  # TODO: apagar depois
    global int_qtde_casos_considerar

    str_nome_arquivo_populacao = "world_population_20200405.csv"
    vet_schema_populacao = ["countriesAndTerritories", "Populacao"]

    str_nome_arquivo = "COVID-19-geographic-disbtribution-worldwide.csv"
    vet_schema = ["dateRep",
                  "day",
                  "month",
                  "year",
                  "cases",
                  "deaths",
                  "countriesAndTerritories",
                  "geoId",
                  "countryterritoryCode",
                  "popData2018",
                  "DataNumerica",
                  "CasosAcumulados",
                  "MortesAcumuladas",
                  "DiasDesdeCaso100",
                  "Populacao",
                  "CasosRefPopulacao",
                  "MortesRefCasos"]

    # TODO: criar o bloco que importa os dois arquivos originais e trata as relações entre eles para ter população de referência

    # le o arquivo de tamanho da populaçã dos países
    dic_populacao = importa_csv_populacao(str_nome_arquivo_populacao, vet_schema_populacao)
    # print("dic_populacao: {}".format(dic_populacao))

    vet_numeros = importa_csv_numeros(str_nome_arquivo, vet_schema)

    # estrutura do dic_paises
    # dic_paises = {
    #     "Brazil": {
    #                 "populacao": 212559417
    #                 ,"valores": [
    #                     ["DiasDesdeCaso100",
    #                      "CasosAcumulados",
    #                      "MortesAcumuladas",
    #                      "CasosAcumuladosDivididosPelaPopulacao",
    #                      "MortesDivididasPelosCasosAcumulados"],
    #                     [21, 9056, 359, 0.9999, 0.9999],
    #                     [20, 7910, 299, 0.9999, 0.9999]
    #                 ,"valores originais": [
    #                     ["dateRep",
    #                       "cases",
    #                       "deaths"],
                        # ["2020-04-04", 1146, 60]
    #                 ]
    #     }
    # }
    dic_paises = {}
    for vet_numero in vet_numeros:
        # carrega dados brutos de entrada em "valores originais"
        str_data = vet_numero[0]
        int_casos = int(vet_numero[4])
        int_mortes = int(vet_numero[5])
        str_pais = vet_numero[6]
        vet_valores_originais = [str_data, int_casos, int_mortes]

        # garante que o país conste do dicionário e já preenche a população na primeira vez que o país aparece
        if not str_pais in dic_paises.keys():  # se o país ainda não consta do dicionário, acrescenta sua estrutura

            # se a população não é identificada, é carregada como 0
            try:
                int_populacao = dic_populacao[str_pais]
                # int_populacao = int(vet_numero[-3].replace(".", ""))
            except:
                int_populacao = 0

            dic_paises[str_pais] = {"populacao": int_populacao, "valores": [], "valores originais": []}

        dic_paises[str_pais]["valores originais"].append(vet_valores_originais)
        dic_paises[str_pais]["valores originais"].sort()

    # passa à agregação de valores originais, para acumulados
    for str_pais in dic_paises.keys():
        vet_valores_originais = dic_paises[str_pais]["valores originais"]
        int_casos_acumulados = 0
        int_mortes_acumuladas = 0
        int_dias_100th = 0

        for vet_aux in vet_valores_originais:
            int_casos_acumulados += vet_aux[1]
            int_mortes_acumuladas += vet_aux[2]
            if int_casos_acumulados >= int_qtde_casos_considerar:
                int_dias_100th += 1

                # tenta calcular a proporcao entre casos confirmados e a população do país
                try:
                    flo_casos_ref_populacao = int_casos_acumulados / dic_paises[str_pais]["populacao"] * 100
                    print("\nPaís: {}\nint_casos_acumulados: {}\ndic_paises[str_pais][populacao]: {}\ntotaliza: {}".format(str_pais, int_casos_acumulados, dic_paises[str_pais]["populacao"], flo_casos_ref_populacao))
                except:
                    flo_casos_ref_populacao = 0.0
                    print("Erro de divisão de {} casos pela população de {}.\nCarregado valor zero para o país {} no {}º dia.".format(int_casos_acumulados, dic_paises[str_pais]["populacao"], str_pais, int_dias_100th))


                # tenta calcular a proporcao entre mortes e casos confirmados
                try:
                    flo_mortes_ref_casos = int_mortes_acumuladas / int_casos_acumulados * 100
                    print("\nPaís: {}\nint_mortes_acumuladas: {}\nint_casos_acumulados: {}\ntotaliza: {}".format(str_pais, int_mortes_acumuladas, int_casos_acumulados, flo_mortes_ref_casos))
                except:
                    flo_mortes_ref_casos = 0.0
                    print("Erro de divisão de {} mortes por {} casos.\nCarregado valor zero para o país {} no {}º dia.".format(int_mortes_acumuladas, int_casos_acumulados, str_pais, int_dias_100th))


                dic_paises[str_pais]["valores"].append([int_dias_100th, int_casos_acumulados, int_mortes_acumuladas,
                                                        flo_casos_ref_populacao, flo_mortes_ref_casos, vet_aux[0]])

    plotar_dimensao()   # chama o processo de plotagem com os valores padrões ("Brazil" e "casos acumulados")




if __name__ == '__main__':
    main()

"""
Dar uma estudada em séries temporais. A seguir aparentes bons pontos de partida:

01) ler planilhas
    - volumes
    - populações (tvz já deixar até fixa)
    - de-para (tvz já deixar até fixa)
02) fazer conversões e seleções
03) agrupar por países
04) para cada país, chamar uma linha do .plot e add a legenda do país ao .legend

"""


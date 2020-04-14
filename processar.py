#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Claudio Jorge Severo Medeiro"
__email__ = "cjinfo@gmail.com"
"""   
    TODO: importar direto do XLSX
    TODO: Plotar 04 visões na mesma tela
    TODO: Ordenar legenda por números de casos no dia X
    TODO: Criar linhas de tendência global, top-3 e país de foco do estudo
    TODO: Permitir usuário escolher país e dias de corte (inicial e final), inclusive a partir de quantos casos 
    de um mesmo país deseja avaliar
    TODO: Ordenar os países por maior volume no mesmo dia que o país de referência está       
"""

import tkinter      # precisa importar esta biblioteca senão não apresenta
import matplotlib
matplotlib.use('TkAgg')

dic_paises = {}
str_separador = ";"
vet_paises_considerar = []
vet_dias_plotar = []
int_dias_pais_referencia = 0
int_qtde_casos_considerar = 100     # TODO: atualmente o default é considerar apenas a partir do dia com 100 casos no país,
                                    # mas o objetivo é permitir que o operador escolha também esse número


def plotar_graficos(int_dimensao=1, str_pais_referencia="Brazil", int_dia_depois_do_100th=-1):
    """
    Dimensões possíveis:
    1: "CasosAcumulados"
    2: "MortesAcumuladas"
    3: "Casos acumulados divididos pela população"
    4: "Mortes divididas pelo número de casos acumulados"
    """
    
    global dic_paises
    global vet_paises_considerar, vet_dias_plotar, int_dias_pais_referencia # TODO: apagar depois

    vet_simbolos = ['.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', '8', 's', 'p', 'P', '*', 'h', 'H', '+', 'x', 'X', 'D', 'd', '|']

    vet_simbolos_plotar = []        # vai garantir que o país tenha o mesmo símbolo em todos os subplots
    vet_plotar = [[], [], [], []]   # vai armazenar as listas de valores de y de cada país a ser exibido no gráfico
    vet_paises_considerar = []      # relação dos países que serão plotados

    vet_titulos_graficos = []
    vet_titulos_graficos.append("Casos acumulados")
    vet_titulos_graficos.append("Mortes acumuladas")
    vet_titulos_graficos.append("Casos acumulados ref População")
    vet_titulos_graficos.append("Mortes ref Casos Acumulados")

    int_dimensoes = 2   # define quantas dimensões devem ser consideradas/plotadas

    int_dias_pais_referencia = len(dic_paises[str_pais_referencia]["valores"])

    if (int_dia_depois_do_100th < int_dias_pais_referencia) and (int_dia_depois_do_100th > -1):
        print("Considerando o dia indicado")
        int_dias_pais_referencia = int_dia_depois_do_100th
    else:
        print("Considerando o último dia apurado para o país '{}'".format(str_pais_referencia))

    vet_dias_plotar = retorna_coluna_matriz(dic_paises[str_pais_referencia]["valores"], 0)[:int_dias_pais_referencia]

    for str_pais in dic_paises.keys():
        # só vai plotar países que tem mais ou a mesma quantidade de dias indicados no país de referência
        if len(dic_paises[str_pais]["valores"]) >= int_dias_pais_referencia:
            # só vai plotar países que no dia ref ao último da série histórica do dia de referência, tinham a mesma quantidade de casos ou mais
            if dic_paises[str_pais]["valores"][int_dias_pais_referencia - 1] >= dic_paises[str_pais_referencia]["valores"][int_dias_pais_referencia - 1]:
                vet_paises_considerar.append(str_pais)
                vet_valores_plotar = retorna_coluna_matriz(dic_paises[str_pais]["valores"][:int_dias_pais_referencia], int_dimensao)
                vet_simbolos_plotar.append(vet_simbolos[0])
                vet_simbolos.append(vet_simbolos[0])
                vet_simbolos.pop(0)

                for int_cont_plotar in range(int_dimensoes):
                    vet_valores_plotar = retorna_coluna_matriz(
                        dic_paises[str_pais]["valores"][:int_dias_pais_referencia], int_cont_plotar+1)
                    vet_plotar[int_cont_plotar].append(vet_valores_plotar)

                # rotaciona os símbolos
                vet_simbolos.append(vet_simbolos[0])
                vet_simbolos.pop(0)

    fig, axs = matplotlib.pyplot.subplots(int_dimensoes, sharex=True)      # Só o de baixo vai relacionar o eixo X (dias desde marca do Nth)
    matplotlib.pyplot.suptitle("País de Referência: {}".format(str_pais_referencia))

    for int_cont_plotar in range(int_dimensoes):
        axs[int_cont_plotar].set_title(vet_titulos_graficos[int_cont_plotar])
        axs[int_cont_plotar].grid(which='major', linestyle='-', linewidth='0.5', color='red')
        axs[int_cont_plotar].minorticks_on()    # habilita o grid menor
        axs[int_cont_plotar].grid(which='minor', linestyle=':', linewidth='0.5', color='black')

        for int_cont in range(len(vet_plotar[int_cont_plotar])):
            axs[int_cont_plotar].plot(vet_dias_plotar, vet_plotar[int_cont_plotar][int_cont], marker=vet_simbolos_plotar[int_cont])

        axs[int_cont_plotar].legend(labels=vet_paises_considerar)

    matplotlib.pyplot.show()

    return


def retorna_coluna_matriz(vet_matriz, int_coluna):
    """
    Recebe uma matriz bidimensional e retorna a coluna indicada
    :param vet_matriz: uma matriz de 02 dimensões
    :param int_coluna: indicador de que coluna da matriz deve ser extraída

    >>> retorna_coluna_matriz([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 1)
    [2, 5, 8]
    """
    return([x[int_coluna] for x in vet_matriz])


def abre_arquivo(str_arquivo):
    """
    Recebe o nome do arquivo, abre-o, e coloca em um vetor em que cada
    posição é uma linha.

    :param str_arquivo: Nome do .csv que deverá ser importado
    :return vet_linhas: Lista contendo cada linha do arquivo de entrada em uma posição, e o último elemento de cada
    posição tem um '\n' que depois precisa ser tirado em cada processo específico

    TODO: Já retirar o '\n' aqui e devolver só os dados de interesse
    """

    str_arquivo = str(str_arquivo)
    vet_linhas = []

    try:
        with open(str_arquivo, 'r') as fil_arquivo:
            vet_linhas = fil_arquivo.readlines()
            fil_arquivo.close()

    except IOError:
        # TODO: Implementar o método 'grava_log' e transformar todos os prints de controle em entradas de log
        # grava_log(("ERRO", "Problemas ao tentar ler o arquivo '" + str_arquivo + "'"))
        print(("ERRO: Problemas ao tentar ler o arquivo '{}'".format(str_arquivo)))

    return vet_linhas


def simbolos_a_esquerda(str_texto, int_tamanho, str_simbolo="0"):
    """
    Recebe um texto, e o devolve no tamanho indicado, preenchido com o símbolo indicado à esquerda
    :param str_texto: o texto a ser modificado
    :param int_tamanho: o tamanho que o texto a ser modificado deverá ter depois da transformação
    :param str_simbolo: o caracter que deverá compor a esquerda do texto, para garantir que o tamanho será cumprido
    :return str_texto_com_simbolos_a_esquerda: o texto já modificado

    >>> simbolos_a_esquerda("4", 3)
    '004'
    """
    str_texto_com_simbolos_a_esquerda = ((int_tamanho - len(str_texto)) * str_simbolo) + str_texto
    return(str_texto_com_simbolos_a_esquerda)


def converte_data(str_data_a_converter):
    """
    Data uma data no formato D/M/AAAA, converte em data formato AAAA-MM-DD
    :param str_data_a_converter: uma data em algum dos formatos 'D/M/AA', 'D/M/AAAA' ou 'DD/MM/AAAA'
    :return str_data_convertida: Data convertida para o formato 'AAAA-MM-DD'

    >>> converte_data("18/4/2020")
    '2020-04-18'
    """
    vet_data_convertida = str_data_a_converter.split("/")
    str_dia = simbolos_a_esquerda(vet_data_convertida[0], 2)
    str_mes = simbolos_a_esquerda(vet_data_convertida[1], 2)
    str_ano = vet_data_convertida[2]
    str_data_convertida = str_ano + "-" + str_mes + "-" + str_dia
    return(str_data_convertida)


def main():
    """
    Coordena a importação dos arquivos e os coloca em estruturas de dicionários a serem utilizados na plotagem
    """
    # global vet_numeros  # TODO: apagar depois
    global dic_paises  # TODO: apagar depois
    global int_qtde_casos_considerar
    global str_separador

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

    # le o arquivo de tamanho da populaçã dos países
    vet_arquivo = abre_arquivo(str_nome_arquivo)
    dic_populacao = {}
    for int_pos in range(1, len(vet_arquivo), 1):
        vet_campos = vet_arquivo[int_pos].split(str_separador)
        vet_campos[-1] = vet_campos[-1].replace("\n", "")       # Exclui o '\n' do ultimo campo
        dic_populacao[vet_campos[0].replace("_", " ")] = int(vet_campos[1])

    # importa o CSV com os números de casos e de mortes por país
    vet_arquivo = abre_arquivo(str_nome_arquivo)
    vet_numeros = []
    for int_pos in range(1, len(vet_arquivo), 1):
        vet_campos = vet_arquivo[int_pos].split(str_separador)
        vet_campos[-1] = vet_campos[-1].replace("\n", "")  # Exclui o '\n' do ultimo campo
        vet_campos[0] = converte_data(vet_campos[0])  # Converte data no formato 'AAAA-MM-DD' para uso futuro
        vet_numeros.append(vet_campos)

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
    #                     ["2020-04-04", 1146, 60]
    #                 ]
    #     }
    # }
    dic_paises = {}
    for vet_numero in vet_numeros:
        # carrega dados brutos de entrada em "valores originais"
        str_data = vet_numero[0]
        int_casos = int(vet_numero[4])
        int_mortes = int(vet_numero[5])
        str_pais = vet_numero[6].replace("_", " ")
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

    plotar_graficos()   # chama o processo de plotagem com os valores padrões ("Brazil" e "casos acumulados")


if __name__ == '__main__':
    main()
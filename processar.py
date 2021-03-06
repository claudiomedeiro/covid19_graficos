#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Claudio Jorge Severo Medeiro"
__email__ = "cjinfo@gmail.com"
"""   
    TODO: Permitir usuário escolher país e dias de corte (inicial e final), inclusive a partir de quantos casos 
    de um mesmo país deseja avaliar
    TODO: alterar para exibir sempre os 10+ e o país de referência, na ordem em que estão (colocar ordem no nome da legenda)
"""
from requests import get        # precisa instalar o pacote:  >>> pip install requests
from os import listdir
import xlrd         # para manipular planilhas excel
import tkinter      # precisa importar esta biblioteca senão não apresenta
from datetime import datetime

import matplotlib
matplotlib.use('TkAgg')

dic_paises = {}
dic_populacao = {}
str_separador = ";"
vet_paises_considerar = []
vet_dias_plotar = []
int_dias_pais_referencia = 0
int_dias_plotar = 8
str_pais_referencia = "Brazil"
int_periodo = 5                     # períodos padrões para a MME
int_valores_projetar = 7            # valores a serem projetados à frente no país de referência
int_qtde_casos_considerar = 100     # TODO: atualmente o default é considerar apenas a partir do dia com 100 casos no país,
                                    #  mas o objetivo é permitir que o operador escolha também esse número


def download_planilha():
    """
    Faz download da planilha mais recente com os dados
    """
    str_data = datetime.now().strftime("%Y-%m-%d")
    str_url = "https://www.ecdc.europa.eu/sites/default/files/documents/"
    str_arquivo = "COVID-19-geographic-disbtribution-worldwide-{}.xlsx".format(str_data)

    if str_arquivo not in listdir("./"):
        try:
            filedata = get("{}{}".format(str_url, str_arquivo))
            filedata.content
            datatowrite = filedata.content
            with open(str_arquivo, "wb") as f:
                f.write(datatowrite)
        except:
            str_mensagem = "Nao foi possivel baixar o arquivo '{}' e sera necessario baixalo na mao, com o seguinte comando: 'wget {}{}'".format(str_arquivo, str_url, str_arquivo)
            # grava_log(("ERRO", str_mensagem))

    else:
        str_mensagem = "O arquivo '{}' já EXISTE e NÃO será necessário fazer download.".format(str_arquivo)
        # grava_log(("info", str_mensagem))

    return(str_arquivo)


def compara_proporcao(vet_interesse, vet_para_comparar):
    """
    Dados 02 vetores, compara proporção entre eles
    """
    vet_retorno = []
    for int_cont in range(len(vet_interesse)):
        if float(vet_interesse[int_cont]) != 0 and float(vet_para_comparar[int_cont]) != 0:
            vet_retorno.append(float(vet_interesse[int_cont]) / float(vet_para_comparar[int_cont]))
        else:
            vet_retorno.append(0)

    return(vet_retorno)


def somar_vetor(vet_somar):
    """
    Dado um vetor de valores numéricos, retorna a soma desses valores

    :param vet_somar:
    :return:
    """
    flo_soma = 0
    for flo_valor in vet_somar:
        flo_soma += flo_valor

    return(flo_soma)


def calcula_media(vet_calcular):
    """
    Dado um vetor de valores numéricos, calcula a média simples desses valores

    :param vet_calcular:
    :return:
    """
    flo_media = somar_vetor(vet_calcular) / len(vet_calcular)
    return(flo_media)


def calcula_media_movel_exponencial(vet_valores, int_periodo):
    """
    Método para cálculo de Média Móvel Exponencial de 'período' = int_periodo
    """
    vet_mme = []
    if len(vet_valores) > int_periodo:
        # calcula média simples dos valores do primeiro período
        for int_cont in range(1, int_periodo + 1):
            vet_mme.append(calcula_media(vet_valores[:int_cont]))

        # calcula média móvel daqui pra frente
        flo_k = 2 / (int_periodo + 1)
        for int_cont in range(int_periodo, len(vet_valores)):
            flo_mme = vet_mme[int_cont - 1] + (flo_k * (vet_valores[int_cont] - vet_mme[int_cont - 1]))
            vet_mme.append(flo_mme)

    return (vet_mme)


def cria_valores_projetados(vet_valores, in_valores_projetar):
    """
    Dada uma lista de valores e um indicador de quantidade, calcula a tendência dos valores da lista, pela MME e
    adiciona os 'in_valores_projetar' ao final da lista
    """

    global int_periodo
    vet_comparado = [1] + compara_proporcao(vet_valores[1:], vet_valores)
    vet_mme = calcula_media_movel_exponencial(vet_comparado, int_periodo)

    for int_cont in range(in_valores_projetar):
        vet_valores.append(vet_valores[-1] * vet_mme[-1])

    return(vet_valores)


def plotar_graficos(int_dimensao=1, int_dia_depois_do_100th=-1):
    """
    Dimensões possíveis:
    1: "CasosAcumulados"
    2: "MortesAcumuladas"
    3: "Casos acumulados por 100 mil habitantes"
    4: "Mortes divididos por 100 mil habitantes"
    """
    
    global dic_paises
    global int_dias_plotar
    global vet_paises_considerar, vet_dias_plotar, int_dias_pais_referencia
    global str_pais_referencia
    global int_periodo, int_valores_projetar

    vet_simbolos = ['.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', '8', 's', 'p', 'P', '*', 'h', 'H', '+', 'x', 'X', 'D', 'd', '|']

    vet_formato_linha_plotar = []
    vet_simbolos_plotar = []        # vai garantir que o país tenha o mesmo símbolo em todos os subplots
    vet_plotar = [[], [], [], []]   # vai armazenar as listas de valores de y de cada país a ser exibido no gráfico
    vet_paises_considerar = []      # relação dos países que serão plotados

    vet_titulos_graficos = []
    vet_titulos_graficos.append("Casos acumulados (milhares)")      # foi preciso transformar os números de casos em milhares porque Estados Unidos ultrapassou 01 milão e passou a dar erro no plot
    vet_titulos_graficos.append("Mortes acumuladas")
    vet_titulos_graficos.append("Casos em cada 100 mil habitantes")
    vet_titulos_graficos.append("Mortes em cada 100 mil habitantes")

    int_dimensoes = 4   # define quantas dimensões devem ser consideradas/plotadas

    int_dias_pais_referencia = len(dic_paises[str_pais_referencia]["valores"])

    if (int_dia_depois_do_100th < int_dias_pais_referencia) and (int_dia_depois_do_100th > -1):
        print("Considerando o dia indicado")
        int_dias_pais_referencia = int_dia_depois_do_100th
    else:
        print("Considerando o último dia apurado para o país '{}'".format(str_pais_referencia))

    vet_dias_plotar = list(range(1, int_dias_pais_referencia + int_valores_projetar + 1))

    for str_pais in dic_paises.keys():
        # só vai plotar países que tem mais ou a mesma quantidade de dias indicados no país de referência mais os dias a serem projetados, ou o próprio país de referência
        if ((len(dic_paises[str_pais]["valores"]) >= (int_dias_pais_referencia + int_valores_projetar)) and (str_pais != str_pais_referencia)) or (str_pais == str_pais_referencia):

            print("\ndic_paises[{}]['valores'][{}] {}".format(str_pais, int_dias_pais_referencia - 1, dic_paises[str_pais]["valores"][int_dias_pais_referencia - 1]))
            print("dic_paises[{}]['valores'][{}]: {}".format(str_pais_referencia, int_dias_pais_referencia - 1, dic_paises[str_pais_referencia]["valores"][int_dias_pais_referencia - 1]))

            # só vai plotar países que no dia ref ao último da série histórica do dia de referência, pelo menos 1/3 da quantidade de casos
            if 3*dic_paises[str_pais]["valores"][int_dias_pais_referencia - 1][1] >= dic_paises[str_pais_referencia]["valores"][int_dias_pais_referencia - 1][1]:
                print("ESSE VAI")
                vet_paises_considerar.append(str_pais)
                vet_formato_linha_plotar.append("solid")
                vet_simbolos_plotar.append(vet_simbolos[0])
                vet_simbolos.append(vet_simbolos[0])
                vet_simbolos.pop(0)

                # se é o país de referência, acrescenta as características da linha da MME dele
                if str_pais == str_pais_referencia:
                    vet_paises_considerar.append("{} (Projetado {} dias)".format(str_pais, int_valores_projetar))
                    vet_simbolos_plotar.append(vet_simbolos_plotar[-1])
                    vet_formato_linha_plotar.append("dotted")

                for int_cont_dimensao in range(int_dimensoes):
                    vet_valores_plotar = retorna_coluna_matriz(dic_paises[str_pais]["valores"][:int_dias_pais_referencia + int_valores_projetar], int_cont_dimensao + 1)
                    vet_plotar[int_cont_dimensao].append(vet_valores_plotar)

                    # se é o país de referência, acrescenta projeções em relação a ele mesmo
                    if str_pais == str_pais_referencia:
                        # preenche as posições iniciais do projetado com vazios
                        vet_aux = []
                        for int_contagem in range(len(vet_plotar[int_cont_dimensao][0])):
                            vet_aux.append(None)

                        vet_aux += cria_valores_projetados(vet_plotar[int_cont_dimensao][0], int_valores_projetar)[-7:]
                        vet_aux_tira = vet_plotar[int_cont_dimensao][-1]
                        for int_contagem in range(int_valores_projetar-1):
                            vet_aux_tira[-(int_contagem+1)] = None

                        vet_plotar[int_cont_dimensao][-1] = vet_aux_tira
                        vet_plotar[int_cont_dimensao].append(vet_aux)

                # rotaciona os símbolos
                vet_simbolos.append(vet_simbolos[0])
                vet_simbolos.pop(0)

    # TODO: Pensar dinamismo para declarar número de dimensões
    fig, axs = matplotlib.pyplot.subplots(2, 2)
    matplotlib.pyplot.suptitle("País de Referência: {} (últimos {} dias + {} projetados)".format(str_pais_referencia, int_dias_plotar, int_valores_projetar))

    int_qtde_plotar = -(int_dias_plotar + int_valores_projetar)
    int_cont_linhas = 0
    int_cont_colunas = 0

    for int_cont_dimensao in range(int_dimensoes):
        axs[int_cont_linhas, int_cont_colunas].set_title(vet_titulos_graficos[int_cont_dimensao])
        axs[int_cont_linhas, int_cont_colunas].grid(which='major', linestyle='-', linewidth='0.5', color='red')
        axs[int_cont_linhas, int_cont_colunas].minorticks_on()    # habilita o grid menor
        axs[int_cont_linhas, int_cont_colunas].grid(which='minor', linestyle=':', linewidth='0.5', color='black')
        axs[int_cont_linhas, int_cont_colunas].yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))

        vet_dias_plotar_realmente = vet_dias_plotar[int_qtde_plotar:]     # plotando apenas os últimos X (15) dias

        # na dimensão atual, pegar todos os vetores dos países plotáveis
        for int_cont in range(len(vet_plotar[int_cont_dimensao])):
            vet_plotar_realmente = vet_plotar[int_cont_dimensao][int_cont][int_qtde_plotar:]
            axs[int_cont_linhas, int_cont_colunas].plot(vet_dias_plotar_realmente, vet_plotar_realmente, marker=vet_simbolos_plotar[int_cont], linestyle=vet_formato_linha_plotar[int_cont])

        # Só plota legenda no primeiro
        if int_cont_linhas + int_cont_colunas == 0:
            axs[int_cont_linhas, int_cont_colunas].legend(labels=vet_paises_considerar)

        int_cont_colunas += 1
        if int_cont_colunas > 1:
            int_cont_linhas += 1
            int_cont_colunas = 0

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


def abre_planilha():
    """
    Converte os dados da planilha mais atual, em uma lista bidimensional, em que cada
    posição é uma linha.

    :return vet_linhas: Lista contendo cada linha do arquivo de entrada em uma posição
    """
    str_arquivo = download_planilha()
    workbook = xlrd.open_workbook(str_arquivo)
    worksheet = workbook.sheet_by_name("COVID-19-geographic-disbtributi")

    vet_linhas = []
    for int_cont_rows in range(1, worksheet.nrows):
        vet_valores = []
        for int_cont_cols in range(worksheet.ncols):
            if worksheet.row(int_cont_rows)[int_cont_cols].ctype == 3:
                flo_valor = worksheet.row(int_cont_rows)[int_cont_cols].value
                wrongValue = flo_valor
                workbook_datemode = workbook.datemode
                tup_data = xlrd.xldate_as_tuple(wrongValue, workbook_datemode)
                str_valor = datetime(tup_data[0], tup_data[1], tup_data[2])
                str_valor = "{}".format(str_valor)
            else:
                str_valor = worksheet.row(int_cont_rows)[int_cont_cols].value

            vet_valores.append(str_valor)

        vet_linhas.append(vet_valores)

    return(vet_linhas)


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


def main():
    """
    Coordena a importação dos arquivos e os coloca em estruturas de dicionários a serem utilizados na plotagem
    """
    global dic_paises
    global int_qtde_casos_considerar
    global str_separador, str_pais_referencia
    global int_periodo

    # importa o XLS com os números de casos e de mortes por país
    vet_numeros = abre_planilha()

    # carrega dados de população em estrutura específica
    for int_pos in range(len(vet_numeros)):
        str_pais = vet_numeros[int_pos][6].replace("_", " ")

        if str_pais not in dic_populacao.keys():
            if vet_numeros[int_pos][9] == '':
                int_valor = 0
            else:
                int_valor = int(vet_numeros[int_pos][9])

            dic_populacao[str_pais] = int_valor

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
                    flo_casos_ref_populacao = int_casos_acumulados / dic_paises[str_pais]["populacao"] * 100000
                except:
                    flo_casos_ref_populacao = 0.0
                    print("Erro de divisão de {} casos pela população de {}.\nCarregado valor zero para o país {} no {}º dia.".format(int_casos_acumulados, dic_paises[str_pais]["populacao"], str_pais, int_dias_100th))

                # tenta calcular a proporcao entre mortes e população
                try:
                    flo_mortes_ref_populacao = int_mortes_acumuladas / dic_paises[str_pais]["populacao"] * 100000
                except:
                    flo_mortes_ref_populacao = 0.0
                    print("Erro de divisão de {} mortes por {} casos.\nCarregado valor zero para o país {} no {}º dia.".format(int_mortes_acumuladas, int_casos_acumulados, str_pais, int_dias_100th))

                dic_paises[str_pais]["valores"].append([int_dias_100th, int_casos_acumulados / 1000, int_mortes_acumuladas,
                                                        flo_casos_ref_populacao, flo_mortes_ref_populacao, vet_aux[0]])

    plotar_graficos()   # chama o processo de plotagem com os valores padrões ("Brazil" e "casos acumulados")


if __name__ == '__main__':
    main()

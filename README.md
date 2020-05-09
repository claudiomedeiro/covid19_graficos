# covid19_graficos

Estou aprendendo a plotar gráficos com o Python, então estou utilizando o assunto do momento (COVID-19), para apresentar seus dados de modo gráfico.

Em linhas gerais, a ideia é pegar os números de casos acumulados dos países, as mortes acumuladas em cada um, respectivas populações, e plotar alguns gráficos que mostram o desenvolvimento da pandemia em cada nação.

Download planilha com casos mundiais por país em https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-AAAA-MM-DD.xlsx
exemplo:
>>> wget https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-2020-03-28.xlsx

Salvar planilha como .csv na raiz do diretório do programa e sem a data no nome
exemplo: COVID-19-geographic-disbtribution-worldwide.xlsx

Os volumes populacionais, por país, foram obtidos no site (https://www.worldometers.info/world-population/population-by-country/), 
feito padronização dos nomes dos países com os nomes que o COVID-19-geographic-disbtribution-worldwide-2020-03-28.xlsx 
traz e salvo na raiz do diretório do programa, apenas com as 02 colunas de interesse, e o nome  

Os seguintes países não consta população então foi feita uma pesquisa individualmente na internet em 12/04/2020:

- Palestine (5.073.681): https://www.worldometers.info/world-population/state-of-palestine-population/
- Kosovo (1.793.000): https://en.wikipedia.org/wiki/Demographics_of_Kosovo
- Jersey (107.700): https://www.gov.je/Government/JerseyInFigures/Population/Pages/PopulationProjections.aspx
- Guernsey (67.052): https://www.cia.gov/library/publications/the-world-factbook/geos/print_gk.html
- Bonaire, Saint Eustatius and Saba (25.157): https://www.paho.org/salud-en-las-americas-2017/?page_id=1694

necessário instalar o tk e fazer o import
$ sudo apt-get install python3-tk

# "Tecnologias" utilizadas no script
- Download automático de um arquivo, a partir de URL definida
- Plotagem de gráfico de linha usando o MatPlotLib
- Trabalhando com datas utilizando o strftime
- Leitura de arquivos XLS
- Leitura de arquivos CSV
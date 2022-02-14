from selenium import webdriver
from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.chrome.options import Options


def main():
    #Configurações iniciais do navegador
    options = Options()
    #Não abrir o Chrome
    options.add_argument("--headless")
    navegador = webdriver.Chrome(options=options)
    navegador.get("https://cartolafc.globo.com/#!/login")
    sleep(2)

    #Escreve o email no campo dele
    campo_email = navegador.find_element_by_name("login")
    campo_email.send_keys("seu_email@gmail.com")
    sleep(1)

    #Escreve a senha
    campo_senha = navegador.find_element_by_name("password")
    campo_senha.send_keys("suasenha123")
    sleep(1)

    #!!!Apenas clica na caixa de recaptcha
    campo_captcha = navegador.find_element_by_id("hcaptcha")
    campo_captcha.click()
    sleep(1)

    #Clica no botão de Login
    campo_botao = navegador.find_element_by_class_name("actions")
    campo_botao.click()
    sleep(5)

    #Essa parte você deve alterar para qual das suas ligas você quer coletar os dados.
    navegador.get("https://cartolafc.globo.com/#!/liga/3a-la-liga-mamonas")
    sleep(5)

    #Clica no botão para aceitar os cookies da página
    botao_cokie = navegador.find_element_by_class_name("cookie-banner-lgpd_accept-button").click()
    sleep(3)

    #Clica no botão para expandir a quantidade de jogadores exibidos
    #Para a quantidade de participantes da minha liga só foi necessária uma vez
    botao_mais = navegador.find_element_by_class_name("column.cartola__button.cartola__button--branco").click()
    sleep(3)

    #Baixa o html da página para pegar o código de cada membro da liga
    conteudo_pagina = navegador.page_source
    site = BeautifulSoup(conteudo_pagina, "html.parser")

    #Obtem os blocos (div) de todos os jogadores
    geral = site.find_all("div", attrs={"class": "cartola-card-thin"})
    times = []
    #Percorrer o bloco de cada jogador
    for block in geral:
        #Coletar a parte específica que ficam as informações de cada membro
        time = block.find("div", attrs={"class": "cartola-ranking-liga__card__time"})
        #Coletar o link do time que também contem o nome
        link = time.find("a")
        times.append({"link":link.get("href"), "time": link.get("title").strip()})

    print(times)

    #Sera criada uma lista de tuplas das pontuações de cada time durante as rodadas
    resultados = []
    #Percorre os times, pula o primeiro, pois o perfil que foi usado para acessar aparece duas vezes
    #Devido aparecer no topo da página e ná posição de colocação
    for time in times[1:]:
        okay = 0
        time_local = {"time": time["time"]}
        #Percorre as 38 rodadas, que são todas do campeonato
        for i in range(38, 0, -1):
            navegador.get("https://cartolafc.globo.com" + time["link"] + "/" + str(i))
            #Dá um sleep até a página carregar, é importante para esperar o Javascript da página carregar
            sleep(7)
            #É importante o try e o if, pois algumas pessoas podem não ter escalado times nas primeiras rodadas
            try:
                pontuacao = navegador.find_element_by_class_name("cartola-time-adv__pontuacao")
                if(pontuacao):
                    time_local[f"rodada{i}"] = float(pontuacao.text)
                    okay += 1
                else:
                    time_local[f"rodada{i}"] = 0
            except:
                time_local[f"rodada{i}"] = 0
            
        resultados.append(time_local)   
        if okay == 38:
            print(f"\n\033[1;32m{time['time']}: (ok)\033[m")
        else:
            print(f"\n\033[1;31m{time['time']}: (erro)\033[m")


    #Transforma os dados obtidos em um DataFrame para melhor visualização
    df = pd.DataFrame(resultados)
    df.set_index("time", inplace=True)
    print(df)

    #Grava em um arquivo Excel
    df.to_excel("resultados.xlsx")

    #Soma de todas as rodadas por membro, para conferir com o site
    print(df.T.sum())

    #Como eu precisava do ganhador do 1° turno, que é o maior pontuador da rodada 1 até 16, fiz uma filtragem
    result = df.T[22:].sum()
    print(result.sort_values(ascending=False))
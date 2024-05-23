import numpy as np
import pandas as pd
import time
import sklearn

from sklearn.metrics import silhouette_score
from sklearn.metrics import adjusted_rand_score
from sklearn.cluster import KMeans

np.random.seed(113)


def normalizacao_dataset(dataset):
    
    return (dataset - np.mean(dataset, axis = 0))/ np.std(dataset, axis = 0)


def distancia_de_minkowski(vetor1, vetor2, p):
    
    vetor_diferenca = vetor1 - vetor2
    vetor_absoluto = np.abs(vetor_diferenca)
    vetor_potencia = np.power(vetor_absoluto, p)
    
    soma = np.sum(vetor_potencia)
    distancia = np.power(soma, 1/p)
    
    return distancia


def distancias_entre_pontos(matriz, p):
    
    num_vetores = matriz.shape[0]
    
    distancias = np.zeros((num_vetores,num_vetores))
    
    for i in range(num_vetores):
        for j in range(i+1, num_vetores):
            dist = distancia_de_minkowski(matriz[i], matriz[j], p)
            distancias[i][j] = dist
            distancias[j][i] = dist

    return distancias


def ponto_mais_distante(distancias, centros):
    
    distancias_centros = distancias[centros].T
    
    distancias_minimas_indices = np.argmin(distancias_centros, axis = 1)
    distancias_minimas_para_centros = distancias_centros[np.arange(len(distancias_centros)), distancias_minimas_indices]

    distancia_maxima = np.max(distancias_minimas_para_centros)
    indice_mais_distante = np.argmax(distancias_minimas_para_centros)
    
    return indice_mais_distante, distancia_maxima


def k_centros(distancias, k):
    
    primeiro_centro = np.random.randint(0, distancias.shape[0])
    centros = [primeiro_centro]
    
    while(k>1):
        
        indice, _ = ponto_mais_distante(distancias, centros)
        centros.append(indice)
        k-=1
    
    _, raio = ponto_mais_distante(distancias, centros)
    resultados_agrupamento = np.argmin(distancias[centros].T, axis = 1)
    
    return raio, resultados_agrupamento


def raio_maximo_kmeans(centros, dados):
    
    distancias_kmeans = np.zeros((len(dados),len(centros)))
    
    for i in range(len(dados)):
        for j in range(len(centros)):
            dist = distancia_de_minkowski(dados[i], centros[j], 2)
            distancias_kmeans[i][j] = dist
    
    distancias_minimas = np.min(distancias_kmeans, axis = 1)
    distancia_maxima = np.max(distancias_minimas)
    
    return distancia_maxima


def gerar_resultados_dataset(nome_arquivo):
    
    df = pd.read_csv(nome_arquivo)
    dados = df.to_numpy()
    valores_verdadeiros = dados[:,-1]
    k = len(set(valores_verdadeiros))
    
    dados = np.delete(dados, -1, axis=1)
    dados_normalizados = normalizacao_dataset(dados)
    resultados = np.zeros((5,8))
    
    for p in [0,1,2,3]:
        distancias = distancias_entre_pontos(dados_normalizados,p+1)
        raios, tempo, rand, silhuetas = [], [], [], []
        
        for i in range(30):
            tempo_inicio = time.time()
            raio, atribuicoes = k_centros(distancias, k)
            raios.append(raio)
            tempo.append(time.time()-tempo_inicio)
            rand.append(adjusted_rand_score(valores_verdadeiros, atribuicoes))
            silhuetas.append(silhouette_score(dados_normalizados, atribuicoes))
            
        resultados[p] = np.array([np.mean(raios), np.std(raios), np.mean(tempo), np.std(tempo), 
                                  np.mean(rand), np.std(rand), np.mean(silhuetas), np.std(silhuetas)])
    
    raios, tempo, rand, silhuetas = [], [], [], []
    for i in range(30):
        tempo_inicio = time.time()
        kmeans = KMeans(n_clusters = k).fit(dados_normalizados)
        raios.append(raio_maximo_kmeans(kmeans.cluster_centers_, dados_normalizados))
        tempo.append(time.time()-tempo_inicio)
        rand.append(adjusted_rand_score(valores_verdadeiros, atribuicoes))
        silhuetas.append(silhouette_score(dados_normalizados, kmeans.labels_))
        
    resultados[4] = np.array([np.mean(raios), np.std(raios), np.mean(tempo), np.std(tempo), 
                              np.mean(rand), np.std(rand), np.mean(silhuetas), np.std(silhuetas)])
            
    df_resultados = pd.DataFrame(resultados, index=["K-centros (p=1)","K-centros (p=2)","K-centros (p=3)","K-centros (p=4)","KMeans"],
                                 columns=["Raio (media)", "Raio (desvio-padrao","Tempo (media)", "Tempo (desvio-padrao)",
                                          "Indice de Rand ajustado (media)","Indice de Rand ajustado (desvio-padrao)",
                                          "Silhueta (media)","Silhueta (desvio-padrao)"])
    df_resultados.to_csv(nome_arquivo.replace(".csv", "_resultados.csv"))


def main():
    
    arquivos = ["accelerometer.csv", "avila.csv", "credit.csv", "frogs.csv", "images.csv", 
                "plants.csv", "pulsars.csv", "satellite.csv", "vehicles.csv", "waveform.csv"]
    
    for arquivo in arquivos:
        gerar_resultados_dataset(arquivo)


main()


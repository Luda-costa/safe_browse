import urllib.parse
import re
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from lime.lime_tabular import LimeTabularExplainer

# Dados
#https://gist.github.com/bejaneps/ba8d8eed85b0c289a05c750b3d825f61
#https://github.com/ProKn1fe/phishtank-database/blob/master/online-valid.json

#Essa função vai basicamente converter as urls para numeros, para que então a IA analise
def extrair_features(url):
    # Primeiro ela divide a url tipo (https, dominio, path)
    url_dividida = urllib.parse.urlparse(url)

    features = {
        # O comprimento de urls de phising costumam ser longos, então usamos isso como uma "feature"
        "len_url": len(url),
        "len_dominio": len(url_dividida.netloc),
        "len_path": len(url_dividida.path),
        # Quanto mais pontos, traços e até barras, podem ser indicios de sites falsos
        "num_ponto": url.count('.'),
        "num_hifen": url.count('-'),
        "num_barra": url.count('/'),
        "tem_https": 1 if url_dividida.scheme == "https" else 0,
        # Ve com regex se o dominio do site é um ip
        "ip": 1 if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", url_dividida.netloc) else 0,
        "palavras_sus": int(any(
            word in url.lower()
            for word in ["login", "secure", "verify", "update", "bank", "account"]
        ))
    }
    # Retorna os valores(MANTER SEMPRE NA MESMA ORDEM)
    return [
        features["len_url"],
        features["len_dominio"],
        features["len_path"],
        features["num_ponto"],
        features["num_hifen"],
        features["num_barra"],
        features["tem_https"],
        features["ip"],
        features["palavras_sus"],
    ]

FEATURE_NAMES = [
    "len_url",
    "len_dominio",
    "len_path",
    "num_ponto",
    "num_hifen",
    "num_barra",
    "tem_https",
    "ip",
    "palavras_sus",
]
CLASS_NAMES = ["seguro", "malicioso"]


def carregar_dados():

    # Vai abrir ler os arquivos json, e criar um dataframe que vão ser tabelas assim
    # URL / Label
    # https://google.account.secure-update.xyz 1
    # https://paypal-login-verify-421.com 1
    # https://fonts.googleapis.com 0
    # https://facebook.com 0
    # https://twitter.com 0

    # Label 0 = site seguro, label 1 = site malixioso
    with open("sites_verdadeiros.json", "r", encoding="utf-8") as f:
        safe_data = json.load(f)

    safe_urls = set()
    for entrada in safe_data:
        for chave, valor in entrada.items():
            safe_urls.add("https://" + chave)
            safe_urls.add("https://" + valor)

    safe_df = pd.DataFrame({"url": list(safe_urls)})
    safe_df["label"] = 0  # 0 = seguro

    with open("sites_falsos.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    mal_df = pd.DataFrame(data)
    mal_df = mal_df[["url", "verified"]]
    mal_df["label"] = mal_df["verified"].apply(lambda v: 1 if v == "yes" else 0)
    mal_df = mal_df[["url", "label"]]

    return safe_df, mal_df

# Treina a IA com o modelo Random forest
def treina_ia():
    # Pega os dados definidos pela função
    safe_df, mal_df = carregar_dados()
    # Junta para que eles estajam num mesmo dataframe
    df = pd.concat([safe_df, mal_df], ignore_index=True)

    # Printa quantos urls falsos e tem(nessa ordem)
    print("Contagem de rótulos (0=safe, 1=malicioso):")
    print(df["label"].value_counts())

    # Converte as urls para valores numericos
    X = np.array(df["url"].apply(extrair_features).tolist())
    # Define os labels 1 e 0
    y = df["label"].values

    # divide o modelo 80% de treino 20% de teste
    # Random state é como uma seed, na forma em que os dados são divididos
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Cria o modelo random forest
    modelo = RandomForestClassifier(random_state=42)
    modelo.fit(X_train, y_train)

    print("Precisão:", modelo.score(X_test, y_test))

    # Mostra a importância global das features

    #print("\nImportância global das features:")
    # calcula quais variaveis são as mais importantes
    #importances = modelo.feature_importances_
    # Pega os nomes das features e junta com suas importancias
    #for nome, imp in sorted(zip(FEATURE_NAMES, importances),
    #                        key=lambda x: -x[1]):
    #    print(f"{nome}: {imp:.3f}")

    # Cria explainer LIME
    # Explainer é o objeto responsavel por explicar as decisões de uma IA
    explainer = LimeTabularExplainer(
        X_train,
        feature_names=FEATURE_NAMES,
        class_names=CLASS_NAMES,
        discretize_continuous=True,
        mode="classification",
    )

    return modelo, explainer

# Define a explicação da suspeita
def explicar_textualmente(url, pesos_lime):
    partes = []
    for nome, peso in pesos_lime:
        if "palavras_sus" in nome:
            desc = "A URL contém palavras consideradas suspeitas"
        elif "tem_https" in nome:
            desc = "A URL não usa HTTPS"
        elif "ip" in nome:
            desc = "O domínio parece um endereço IP"
        elif "len_url" in nome:
            desc = "A URL é muito longa"
        elif "len_dominio" in nome:
            desc = "O domínio é muito longo"
        elif "len_path" in nome:
            desc = "O caminho da URL é muito longo"
        elif "num_ponto" in nome:
            desc = "a URL tem muitos pontos"
        elif "num_hifen" in nome:
            desc = "a URL tem muitos hífens"
        elif "num_barra" in nome:
            desc = "a URL tem muitas barras"
        else:
            desc = f"feature {nome}"

        partes.append(f"{desc}. ")

        if len(partes) >= 3:
            break

    if not partes:
        return "Não há contribuições fortes detectadas para explicar esta decisão."

    return " ".join(partes)

def verifica_url(modelo, explainer, url):

    feats = np.array([extrair_features(url)])
    prob = modelo.predict_proba(feats)[0]
    resposta = np.argmax(prob)

    if resposta == 1:
        print(f"\nURL: {url}")
        print("Classificação: Site FALSO (malicioso)")
    else:
        print(f"\nURL: {url}")
        print("Classificação: Site CONFIÁVEL (seguro)")

    print(f"Probabilidades -> seguro: {prob[0]:.3f}, malicioso: {prob[1]:.3f}")

    # Explicação local com LIME para essa URL
    exp = explainer.explain_instance(
        feats[0],
        modelo.predict_proba,
        num_features=len(FEATURE_NAMES),
    )


    #print("\nExplicação LIME (feature, contribuição):")
    #for nome, peso in exp.as_list():
    #    print(f"{nome}: {peso:+.3f}")

    # Versão em texto
    if resposta == 1:
        texto = explicar_textualmente(url, exp.as_list())
        print("\nResumo:")
        print(texto)

    return resposta

def main():
    modelo, explainer = treina_ia()

    # URLs para testar
    #Falsos

    verifica_url(modelo, explainer, "http://paypal.secure-login-update4723.com/verify")
    verifica_url(modelo, explainer, "https://pl-kategorie74827479046253.shop/")
    verifica_url(modelo, explainer, "https://paguefreeflow.org/")
    verifica_url(modelo, explainer, "https://produbaanco.com/")
    verifica_url(modelo, explainer, "https://liberacaonline.online/inicio/")

   #Seguros
    verifica_url(modelo, explainer, "https://youtube.com.br")
    verifica_url(modelo, explainer, "https://google.com.br")
    verifica_url(modelo, explainer, "https://youtube.com.br")

if __name__ == "__main__":
    main()

from flask import Flask, request, jsonify
from main import treina_ia, extrair_features, explicar_textualmente
import numpy as np
from flask_cors import CORS

# As funções extrair_features, treina_ia, explicar_textualmente devem ser mantidas

# Treine sua IA antes de iniciar a API (ou carregue modelos já salvos)
modelo, explainer = treina_ia()

app = Flask(__name__)
#Usa o cors para permitir que a extensão se conecte
CORS(app)

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


@app.route("/verifica_url", methods=["POST"])
def verifica_url_api():
    data = request.get_json()
    url = data.get("url", "")

    feats = np.array([extrair_features(url)])
    prob = modelo.predict_proba(feats)[0]
    resposta = int(np.argmax(prob))

    # Explicação LIME para a URL
    exp = explainer.explain_instance(
        feats[0],
        modelo.predict_proba,
        num_features=len(FEATURE_NAMES),
    )

    texto = ""
    if resposta == 1:
        texto = explicar_textualmente(url, exp.as_list())

    response = {
        "url": url,
        "classificacao": "malicioso" if resposta == 1 else "seguro",
        "probabilidades": {
            "seguro": float(prob[0]),
            "malicioso": float(prob[1])
        },
        "explicacao": texto
    }

    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)


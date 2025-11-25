# SafeBrowse
SafeBrowse é um projeto acadêmico desenvolvido como ferramenta de apoio ao aprendizado em segurança digital, com foco em detecção de sites falsos e conscientização sobre phishing.


- [Pré-requisitos](##pré-requisitos)
- [Instalação](##instalação)
- [Como Usar](##como-usar)

## Pré-requisitos
Antes de iniciar, verifique se você possui os seguintes itens instalados:

- Python 3.7 ou superior

- pip (gerenciador de pacotes Python)

## Instalação
**1. Clone o repositório e acesse a pasta do projeto**
```
bash
git clone https://github.com/seu-usuario/safe_browse.git
cd safe_browse
```

**2. Descompacte a data dos sites falsos**
Acesse a pasta safe_browse/PhisingAI e descompacte o arquivo sites_falsos.zip:

```
bash
cd PhisingAI
unzip sites_falsos.zip
cd ..
```

**3. Instale as dependências**
Dentro da pasta PhisingAI, instale os pacotes necessários:

```
bash
pip install -r requirements.txt
```

**4. Execute o servidor Flask**

```
bash
python app.py
```

Se tudo estiver correto, o terminal exibirá uma mensagem indicando que o servidor está rodando:

```
 * Serving Flask app 'api'
 * Debug mode: on
...
 * Running on http://127.0.0.1:5000
```

**5. Instale a extensão no Chrome**
Abra o Chrome e acesse chrome://extensions/.

Ative o “Modo desenvolvedor” no canto superior direito.
<img width="1850" height="931" alt="Design sem nome (3)" src="https://github.com/user-attachments/assets/1e509b0a-1455-44de-91bb-66e45c115e45" />


Clique em Load unpacked e selecione a pasta page_reader.
<img width="1850" height="931" alt="Design sem nome (4)" src="https://github.com/user-attachments/assets/02eaa88d-a5b8-4455-924a-265984dc9471" />

Pronto, a extensão estará pronta para uso!

## Como usar
Com o servidor rodando e a extensão instalada, navegue em qualquer página e utilize a extensão para testar as funcionalidades de detecção de phishing.

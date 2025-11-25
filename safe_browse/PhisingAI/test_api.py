import requests

url = 'http://localhost:5000/verifica_url'
json_data = {
    "url": "http://paypal.secure-login-update4723.com/verify"
}

response = requests.post(url, json=json_data)

print("Status:", response.status_code)
print("Resposta:", response.json())

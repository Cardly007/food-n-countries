import requests
url = "https://openrouter.ai/api/v1/chat/completions"
headers = {"Authorization": "Bearer fake_key"}
data = {"model": "google/gemini-flash-1.5", "messages": [{"role": "user", "content": "hi"}]}
response = requests.post(url, headers=headers, json=data)
print(response.status_code, response.text)

import requests

def test_gemini():
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=invalid"
    response = requests.post(url, json={})
    print("Gemini:", response.status_code, response.text)

def test_openrouter():
    url = "https://openrouter.ai/api/v1/chat/completions"
    response = requests.post(url, json={})
    print("OpenRouter:", response.status_code, response.text)

test_gemini()
test_openrouter()

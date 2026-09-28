import requests

def test_model(model_name):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key=invalid"
    response = requests.post(url, json={})
    print(f"{model_name}:", response.status_code, response.text)

test_model("gemini-3.5-flash")

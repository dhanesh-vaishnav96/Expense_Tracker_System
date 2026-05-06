import requests

url = "http://127.0.0.1:8000/api/login-form"
data = {
    "username": "dhaneshvaishnav123@gmail.com",
    "password": "password123" # I don't know the real password, so this will likely fail
}

try:
    response = requests.post(url, data=data, allow_redirects=False)
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers}")
    print(f"Cookies: {response.cookies.get_dict()}")
    if "location" in response.headers:
        print(f"Redirecting to: {response.headers['location']}")
except Exception as e:
    print(f"Error: {e}")

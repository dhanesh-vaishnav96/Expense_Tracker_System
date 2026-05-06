import requests
import time

ts = int(time.time())
email = f"test_{ts}@example.com"

url = "http://127.0.0.1:8000/api/register-form"
data = {
    "name": "Test User",
    "email": email,
    "password": "testpassword"
}

try:
    print(f"Registering with {email}...")
    response = requests.post(url, data=data, allow_redirects=False)
    print(f"Register Status: {response.status_code}")
    print(f"Register Location: {response.headers.get('Location')}")
    
    print("\nLogging in...")
    login_url = "http://127.0.0.1:8000/api/login-form"
    login_data = {
        "username": email,
        "password": "testpassword"
    }
    response = requests.post(login_url, data=login_data, allow_redirects=False)
    print(f"Login Status: {response.status_code}")
    print(f"Login Location: {response.headers.get('Location')}")
    print(f"Login Cookies: {response.cookies.get_dict()}")
    
    if "token" in response.cookies:
        print("\nToken found!")
    else:
        print("\nToken NOT found!")
        
except Exception as e:
    print(f"Error: {e}")

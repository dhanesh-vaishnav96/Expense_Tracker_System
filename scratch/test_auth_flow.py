import requests

url = "http://127.0.0.1:8000/api/register-form"
data = {
    "name": "Test User",
    "email": "test@example.com",
    "password": "testpassword"
}

try:
    print("Registering...")
    response = requests.post(url, data=data, allow_redirects=False)
    print(f"Register Status: {response.status_code}")
    
    print("\nLogging in...")
    login_url = "http://127.0.0.1:8000/api/login-form"
    login_data = {
        "username": "test@example.com",
        "password": "testpassword"
    }
    response = requests.post(login_url, data=login_data, allow_redirects=False)
    print(f"Login Status: {response.status_code}")
    print(f"Login Headers: {response.headers}")
    print(f"Login Cookies: {response.cookies.get_dict()}")
    
    if "token" in response.cookies:
        token = response.cookies["token"]
        print(f"\nToken found: {token[:20]}...")
        
        print("\nAccessing Dashboard...")
        dash_url = "http://127.0.0.1:8000/dashboard"
        response = requests.get(dash_url, cookies={"token": token}, allow_redirects=False)
        print(f"Dashboard Status: {response.status_code}")
        if response.status_code == 303 or response.status_code == 302:
            print(f"Redirected to: {response.headers.get('Location')}")
        else:
            print(f"Dashboard Content Length: {len(response.text)}")
    else:
        print("\nToken NOT found in cookies!")
        
except Exception as e:
    print(f"Error: {e}")

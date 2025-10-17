import requests

# 🔍 FACE CHECK ID
def query_facecheck(image_path):
    api_key = "HYJVtNmB6VybJ7NSI+GVxhOY+LCBM+KrEuZQlSeoQmvLD3D+sbIdPT37vT7CkiccgHU7eWRFKj0="  # <-- replace with your key
    endpoint = "https://api.facecheck.id/v1/search"
    with open(image_path, "rb") as f:
        files = {"image": f}
        headers = {"X-API-Key": api_key}
        resp = requests.post(endpoint, files=files, headers=headers)
        return resp.json() if resp.status_code == 200 else {"error": resp.text}

# 🔍 FACE++ API
def query_faceplusplus(image_path):
    api_key = "snqEyd7I7kzPRuxq0a9wN5prg69bRisl"  # <-- replace with your key
    api_secret = "TATOD8v04u_N2DFZybyLUIa5NYL1GqEC"  # <-- replace with your secret
    url = "https://api-us.faceplusplus.com/facepp/v3/detect"
    with open(image_path, "rb") as f:
        files = {"image_file": f}
        data = {"api_key": api_key, "api_secret": api_secret}
        resp = requests.post(url, files=files, data=data)
        return resp.json() if resp.status_code == 200 else {"error": resp.text}

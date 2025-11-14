import requests

def get(usss):
    if not isinstance(usss, str) or not usss.strip():
        return {"error": "Username cannot be empty."}

    tan = f'https://api.x7m.site/v1/telid.php?user={usss}'
    try:
        res = requests.get(tan, timeout=10)
        res.raise_for_status()
        data = res.json()
        if data.get("ok") is False:
            return {"error": data.get("description", "An unknown API error occurred.")}

        return data

    except requests.exceptions.RequestException as e:
        return {"error": f"An error occurred during the request: {e}"}
    except ValueError:
        return {"error": "Failed to parse the response from the API."}

import requests

# !! YAHAN APNA PUBLIC SERVER URL DAALEIN (STEP 2 SE) !!
API_URL = "https://proportionable-verdie-unrelinquishing.ngrok-free.dev" 

def generate_code(prompt: str):
    """
    Aura.AI server ko call karta hai aur generated code return karta hai.
    """
    
    # Hum server ko 'multipart/form-data' bhejenge
    # (kyunki server 'request.form' ka istemaal kar raha hai)
    payload = {
        'prompt': (None, prompt) 
    }

    try:
        response = requests.post(API_URL, files=payload)
        
        # Error check karein
        response.raise_for_status() 
        
        # Server se mila response (JSON format mein)
        result = response.json()
        
        # Generated code ko return karein
        return result.get("generated_code", "Error: Server se code nahi mila.")

    except requests.exceptions.HTTPError as errh:
        return f"Http Error: {errh}"
    except requests.exceptions.RequestException as err:
        return f"Oops: Server se connect nahi ho pa raha: {err}"
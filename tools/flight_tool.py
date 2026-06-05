import requests
# create api key
# https://aviationstack.com/ 
# pip install requests
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

def search_flight(query):
    url = "http://api.aviationstack.com/v1/flights"
    param={
       
        "access_key":API_KEY,
    
        "limit": 5
    }
    response=requests.get(url,params=param)
    data=response.json()

    flight=[]

    for flights in data.get("data",[])[:5]:

        flight.append(
            f"Airline: {flights.get('airline', {}).get('name', 'Unknown')}\n"
            f"Departure: {flights.get('departure', {}).get('airport', 'Unknown')}\n"
            f"Arrival: {flights.get('arrival', {}).get('airport', 'Unknown')}\n"
            f"Status: {flights.get('flight_status', 'Unknown')}\n"
        )

    return "\n".join(flight)
        
            
            

        

    




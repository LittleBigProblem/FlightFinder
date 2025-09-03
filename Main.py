import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

def get_access_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": API_KEY,
        "client_secret": API_SECRET
    }

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print("Failed to get token:", response.text)
        return None
    
def get_all_flights(token):
    from datetime import datetime, timedelta
    # Prompt user for a departure date
    user_departure_date = input("Enter your preferred departure date (YYYY-MM-DD): ")
    user_return = input("Will this be a return flight? (Y/N): ")
    flexible_search = input("Do you want to search for the cheapest flights in a ±3 day window? (Y/N): ")
    return_flight = False
    user_return_date_obj = None
    try:
        selected_date = datetime.strptime(user_departure_date, "%Y-%m-%d").date()
        if user_return.upper() == "Y":
            user_return_date = input("Enter your preferred return date (YYYY-MM-DD): ")
            user_return_date_obj = datetime.strptime(user_return_date, "%Y-%m-%d").date()
            return_flight = True
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        return []

    all_flights = []
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    if flexible_search.upper() == "Y":
        if return_flight and user_return_date_obj:
            for dep_offset in range(-3, 4):
                dep_date = selected_date + timedelta(days=dep_offset)
                for ret_offset in range(-3, 4):
                    ret_date = user_return_date_obj + timedelta(days=ret_offset)
                    url = f"https://test.api.amadeus.com/v2/shopping/flight-offers?originLocationCode=DRW&destinationLocationCode=ADL&departureDate={dep_date.isoformat()}&returnDate={ret_date.isoformat()}&adults=1&max=5&currencyCode=AUD"
                    response = requests.get(url, headers=headers)
                    if response.status_code == 200:
                        data = response.json().get('data', [])
                        if data:
                            for flight in data:
                                flight['searched_departure_date'] = dep_date.isoformat()
                                flight['searched_return_date'] = ret_date.isoformat()
                            all_flights.extend(data)
                    else:
                        print(f"Failed to get flights for dep {dep_date.isoformat()} and ret {ret_date.isoformat()}:", response.text)
        else:
            for offset in range(-3, 4):  # 3 days before, selected, 3 days after
                current_date = selected_date + timedelta(days=offset)
                url = f"https://test.api.amadeus.com/v2/shopping/flight-offers?originLocationCode=DRW&destinationLocationCode=ADL&departureDate={current_date.isoformat()}&adults=1&max=5&currencyCode=AUD"
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json().get('data', [])
                    if data:
                        for flight in data:
                            flight['searched_date'] = current_date.isoformat()
                        all_flights.extend(data)
                else:
                    print(f"Failed to get flights for {current_date.isoformat()}:", response.text)
    else:
        if return_flight and user_return_date_obj:
            url = f"https://test.api.amadeus.com/v2/shopping/flight-offers?originLocationCode=DRW&destinationLocationCode=ADL&departureDate={selected_date.isoformat()}&returnDate={user_return_date_obj.isoformat()}&adults=1&max=5&currencyCode=AUD"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json().get('data', [])
                if data:
                    for flight in data:
                        flight['searched_departure_date'] = selected_date.isoformat()
                        flight['searched_return_date'] = user_return_date_obj.isoformat()
                    all_flights.extend(data)
            else:
                print(f"Failed to get flights for dep {selected_date.isoformat()} and ret {user_return_date_obj.isoformat()}:", response.text)
        else:
            url = f"https://test.api.amadeus.com/v2/shopping/flight-offers?originLocationCode=DRW&destinationLocationCode=ADL&departureDate={selected_date.isoformat()}&adults=1&max=5&currencyCode=AUD"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json().get('data', [])
                if data:
                    for flight in data:
                        flight['searched_date'] = selected_date.isoformat()
                    all_flights.extend(data)
            else:
                print(f"Failed to get flights for {selected_date.isoformat()}:", response.text)
    return all_flights, flexible_search.upper() == "Y"

# Example usage:
if __name__ == "__main__":
    token = get_access_token()
    if token:
        print("Access token:", token)
        flights, is_flexible = get_all_flights(token)
        if flights:
            print(f"Found {len(flights)} flights within 3 days either side of your selected date.")
            # Sort by price if flexible search (cheapest flights)
            if is_flexible:
                def get_price(f):
                    try:
                        return float(f.get('price', {}).get('grandTotal', float('inf')))
                    except Exception:
                        return float('inf')
                flights = sorted(flights, key=get_price)
            print("Sample Flight Data (showing all offers):\n")
            for flight in flights:
                # Show searched dates appropriately
                if 'searched_departure_date' in flight or 'searched_return_date' in flight:
                    dep_date = flight.get('searched_departure_date', 'N/A')
                    ret_date = flight.get('searched_return_date', 'N/A')
                    print(f"Departure Date Searched: {dep_date}")
                    print(f"Return Date Searched:    {ret_date}")
                else:
                    print(f"Date Searched: {flight.get('searched_date')}")
                itineraries = flight.get('itineraries', [])
                if itineraries:
                    # Outbound
                    print("  Outbound Flight:")
                    for seg in itineraries[0].get('segments', []):
                        dep = seg['departure']
                        arr = seg['arrival']
                        print(f"    {dep['iataCode']} ({dep.get('at')}) -> {arr['iataCode']} ({arr.get('at')})")
                    # Return (if exists)
                    if len(itineraries) > 1:
                        print("  Return Flight:")
                        for seg in itineraries[1].get('segments', []):
                            dep = seg['departure']
                            arr = seg['arrival']
                            print(f"    {dep['iataCode']} ({dep.get('at')}) -> {arr['iataCode']} ({arr.get('at')})")
                print(f"  Total Price: {flight.get('price', {}).get('grandTotal')} {flight.get('price', {}).get('currency')}")
                print("-" * 50)
        else:
            print("No flights found in the 7-day window.")
    else:
        print("Could not retrieve access token.")

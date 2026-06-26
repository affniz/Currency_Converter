import os
import time
import requests
from datetime import datetime
from pydantic import BaseModel,field_validator
from dotenv import load_dotenv

load_dotenv()

api_key= os.getenv("API_KEY")

def timer(func):
    def wrapper(*args,**kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start: .2f} seconds")
        return result
    return wrapper

class ExchangeRate(BaseModel):
    base_code:str
    rates: dict[str,float]
    time_last_update_utc: datetime

    @field_validator('time_last_update_utc',mode='before')
    def parse_datetime(cls,value):
        return datetime.strptime(value, "%a, %d %b %Y %H:%M:%S %z")

@timer
def fetch_rates(api_key,base_currency):
    url = f"https://open.er-api.com/v6/latest/{base_currency}?apikey={api_key}"
    data=None
    try:
        response=requests.get(url)
        data=response.json()
    except requests.exceptions.ConnectionError:
        print("Network Error: please check your internet connection.")
    except requests.exceptions.JSONDecodeError:
        print(f"{base_currency} is not a valid currency code.")
    if data and data['result'] != 'success':
        print(f"Invalid base currency: '{base_currency}'")
        data=None
    return data

def user_input():
    print("Enter Base Currency: ")
    from_curr = input().strip().upper()
    print("Enter Target Currency: ")
    to_curr = input().strip().upper()
    print("Enter Amount: ")
    try:
        amount = float(input())
        if amount < 0:
            raise ValueError("Amount cannot be negative.")
            return user_input()
    except ValueError:
        print("Invalid amount. Please enter a valid number.")
        return user_input()
    return from_curr, to_curr, amount

from_curr,to_curr,amount = user_input()

rates_data=fetch_rates(api_key,from_curr)

if not rates_data:
    print("Failed to fetch exchange rates. Please try again later.")
    exit()
else:
    validated_data= ExchangeRate(**rates_data)
    if to_curr not in validated_data.rates:
        print(f"Target Currency not found.")
    else:
        print(f"Exchange Rate: 1 {from_curr} = {validated_data.rates[to_curr]:.2f} {to_curr}")
        print(f"{amount} {from_curr} = {amount * validated_data.rates[to_curr]:.2f} {to_curr}")

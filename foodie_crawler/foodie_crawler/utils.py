import sys, os
import requests

API_KEY = "AIzaSyAV6pXUoZU8gP9rWfmTYy-jn-J8Bxgy46A"
api_url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s"

def geocode(address, city, state, zipcode):
    full_address = "%s,+%s,+%s,+%s" % (address, city, state, zipcode)
    url = api_url % (full_address, API_KEY)
    response = requests.get(url)
    if response:
        js = response.json()
        if "OK" == js.get('status'):
            location = js.get("results")[0].get("geometry").get("location")
            return (location["lat"], location["lng"])
        return (None, None)
    return (None, None) 

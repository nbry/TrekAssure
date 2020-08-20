import requests
from uszipcode import SearchEngine

MQAPI_BASE_URL = 'http://www.mapquestapi.com'
HPAPI_BASE_URL = 'https://www.hikingproject.com/data'


# *****************************
# US ZIPCODE FUNCTIONS
# *****************************


def get_geo_info(zip_code):
    """ Using uszipcode package, get geographical info of a user-inputted
    zipcode. Return a dictionary of that information"""

    search = SearchEngine(simple_zipcode=True)
    geo_info = search.by_zipcode(f"{zip_code}")
    geo_info_dict = geo_info.to_dict()

    return geo_info_dict


# *****************************
# MAPQUEST API FUNCTIONS:
# *****************************

def get_route_home(key, to_address, from_address):
    """ Using user inputted address, get routing directions using """

    response = requests.get(f"{MQAPI_BASE_URL}/directions/v2/route",
                            params={'key': key, 'to': to_address, 'from': from_address})

    data = response.json()
    directions = data['route']['legs'][0]['maneuvers']

    return directions


def TEMPORARY(key, zip_code):
    """ Using Zip Code, get some geographical info info """
    response = requests.get(f"{MQAPI_BASE_URL}/geocoding/v1/address",
                            params={'key': key, 'location': zip_code})

    data = response.json()
    lat = data['results'][0]['locations'][0]['latLng']['lat']
    lon = data['results'][0]['locations'][0]['latLng']['lng']
    city = data['results'][0]['locations'][0]['adminArea5']

    results = {
        'lat': lat,
        'lon': lon,
        'city': city
    }

    return results


# *****************************
# HIKING PROJECT API FUNCTIONS:
# *****************************


def search_for_trails(key, lat, lon, radius=None):
    """ Use Hiking Project API to get a list of trails based
    on user search parameters """

    if radius:
        params = {'key': key, 'lat': lat, 'lon': lon, 'sort': 'quality',
                  'maxResults': 500, 'maxDistance': radius}
    else:
        params = {'key': key, 'lat': lat, 'lon': lon,
                  'sort': 'quality', 'maxResults': 500}

    response = requests.get(f"{HPAPI_BASE_URL}/get-trails",
                            params=params)

    data = response.json()
    trails_info = data['trails']
    return trails_info


def get_trail(key, id):
    """ Use Hiking Project API to get get trail info by id """

    response = requests.get(f"{HPAPI_BASE_URL}/get-trails-by-id",
                            params={'key': key, 'ids': id})

    data = response.json()
    trail_info = data['trails'][0]

    return trail_info


def get_conditions(key, id):
    """ Use Hiking Project API to get today's trail conditions  """

    response = requests.get(f"{HPAPI_BASE_URL}/get-conditions",
                            params={'key': key, 'ids': id})

    data = response.json()
    result = data[0]

    return result


def rate_difficulty(color):
    """ Hiking Project API returns difficulty as a color. Translate the
    color to a tangible difficulty rating """

    colors = ['green', 'greenBlue', 'blue',
              'blueBlack', 'black', 'dblack', 'missing']

    ratings = [('Easy', 'No obstacles. Flat.'), ('Easy/Intermediate', 'Mostly flat and even.'), ('Intermediate', 'Uneven Terrain. Small hills'),
               ('Intermediate/Difficult', 'Steep sections, rocks, roots'), ('Difficult', 'Tricky terrain. Steep. Not for beginners'), ('Very Difficult', 'Hazardous. Very steep. Experts only'), (None, None)]

    index = colors.index(color)

    return ratings[index]

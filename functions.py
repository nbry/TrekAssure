import requests
from random import randrange

MQAPI_BASE_URL = 'http://www.mapquestapi.com'
HPAPI_BASE_URL = 'https://www.hikingproject.com/data'


# *****************************
# MAPQUEST API FUNCTIONS:
# *****************************


categories = {
    'gas station': 'sic:554101',
    'pharmacy': 'sic:591205',
    'hospital': 'sic:801105',
    'police station': 'sic:922104'
}


def secure_trip(key, trail, to_address):
    """ Comprehensive function for securing a trip.
    Should accomplish the following:
    1. Gets directions home
    2. Get directions to closest gas station, hospital, pharmacy, and police station """

    lat_lon_trail = f"{trail['latitude']}, {trail['longitude']}"
    lon_lat_trail = f"{trail['longitude']}, {trail['latitude']}"

    results_dict = {}

    # Set result dict categories e.g. dict == {gas: {}, pharmacy: {}, ...etc }
    for destination in categories:
        results_dict[destination] = {}

        new_category_info_value = search_for_nearest(
            key, lon_lat_trail, categories[destination])

        results_dict[destination]['info'] = new_category_info_value

    # Set lat/lon coords for each category
    for category in results_dict:
        category_info = results_dict[category]['info']

        results_dict[category]['lat_lon'] = ", ".join(
            str(item) for item in category_info['place']['geometry']['coordinates'][::-1])

    # Set directions from trail to each category
    for category in results_dict:
        results_dict[category]['route'] = get_directions(
            key, results_dict[category]['lat_lon'], lat_lon_trail)

    # Add route to home to results_dict
    results_dict['home'] = {}
    results_dict['home']['info'] = to_address
    results_dict['home']['route'] = get_directions(
        key, to_address, lat_lon_trail)

    return results_dict


def get_directions(key, to_address, from_address):
    """ Using user inputted address, get routing directions using """

    response = requests.get(f"{MQAPI_BASE_URL}/directions/v2/route",
                            params={'key': key, 'to': to_address, 'from': from_address})

    data = response.json()
    route_info = data['route']
    try:
        directions = data['route']['legs'][0]['maneuvers']
    except:
        directions = []

    return {'directions': directions, 'route_info': route_info}


def search_for_nearest(key, location, category):
    """ Using Mapquest's Place Search API, find nearest {category} from an address.
    For TrekAssure, this function is used primarily to find the closest of the following:
    Gas station, hospital, pharmacy, and police station """

    response = requests.get(f"{MQAPI_BASE_URL}/search/v4/place", params={
                            'key': key, 'location': location, 'category': category, 'sort': 'distance'})

    data = response.json()
    result = data['results'][0]

    return result


def get_geo_info(key, place_search):
    """ Using MapQuest's Place Search SDK and geocoding API, get some geographical info info """

    response = requests.get(f"{MQAPI_BASE_URL}/geocoding/v1/address",
                            params={'key': key, 'location': place_search})

    data = response.json()
    lat = data['results'][0]['locations'][0]['latLng']['lat']
    lng = data['results'][0]['locations'][0]['latLng']['lng']
    city = data['results'][0]['locations'][0]['adminArea5']

    results = {
        'lat': lat,
        'lng': lng,
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
        params = {'key': key, 'lat': lat, 'lon': lon, 'sort': 'distance',
                  'maxResults': 500, 'maxDistance': radius}
    else:
        params = {'key': key, 'lat': lat, 'lon': lon,
                  'sort': 'quality', 'maxResults': 500}

    response = requests.get(f"{HPAPI_BASE_URL}/get-trails",
                            params=params)

    data = response.json()
    trails_info = data['trails']

    for trail in trails_info:
        trail['short_sum'] = trail['summary'][:50] + "..."
        trail['short_name'] = trail['name'][:20] + "..."

    for trail in trails_info:
        if trail['summary'] == "Needs Summary" or trail['summary'] == "":
            trail['short_sum'] = "No Description"

    return trails_info


def get_trail(key, id):
    """ Use Hiking Project API to get get trail info by id """

    response = requests.get(f"{HPAPI_BASE_URL}/get-trails-by-id",
                            params={'key': key, 'ids': id})

    data = response.json()
    trail_info = data['trails'][0]

    # duplicate code from above. May need refactoring
    trail_info['short_sum'] = trail_info['summary'][:50] + "..."
    trail_info['short_name'] = trail_info['name'][:20] + "..."

    if trail_info['summary'] == "Needs Summary" or trail_info['summary'] == "":
        trail_info['short_sum'] = "No Description"

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
               ('Somewhat Difficult', 'Steep sections, rocks, roots'), ('Strenuous/Steep', 'Tricky terrain. Steep. Not for beginners'), ('Very Difficult', 'Hazardous. Very steep. Experts only'), (None, None)]

    index = colors.index(color)

    return ratings[index]

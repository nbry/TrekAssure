const MQAPI_BASE_URL = 'http://www.mapquestapi.com/'
const HPAPI_BASE_URL = 'https://www.hikingproject.com/data'


class SearchTrailList {

    static async getTrails(place, radius) {
        const response = await axios.get('/trails/results',
            {
                params: {
                    'place': place,
                    'radius': radius
                }
            });

        return response;
    }

    static async storeTrailSearch(results, place, radius) {
        axios.post('/trails/store-results', {
            data: {
                'results': results,
                'place': place,
                'radius': radius
            }
        })
    }
}
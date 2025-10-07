import requests as rq
import json

myAPI = "kMsYcNeUFBEnx36W0W3LYhq8g2BZvk8YjLXTziVc" 

headers = {
    "x-api-key": myAPI
}

response = rq.get(
    "https://api-op.grid.gg/live-data-feed/series-state/graphql",
    headers = headers
)

## Alternative:
#response = requests.get(
#    "https://api.grid.gg/file-download/end-state/grid/series/2589176?key={YOUR_API_KEY}"
#)

GRAPHQL_ENDPOINT = "https://api-op.grid.gg/central-data/graphql"
Other_Api_endpoint = " https://api-op.grid.gg"

print(response.text)






graphql_query = """
query Series {
    allSeries (
        first: 50,
        filter: {
            titleId: 1  # Valorant
            types: ESPORTS  # Esports matches only
        }
        orderBy: StartTimeScheduled  # Sort by start time
        orderDirection: DESC  # Sort by most recent first
    ) {
        totalCount
        pageInfo {
            hasPreviousPage
            hasNextPage
            startCursor
            endCursor
        }
        edges {
            node {
                id
                title {
                    id
                }
                tournament {
                    id
                    name
                }
            }
        }
    }
}
"""



payload = {
    "query": graphql_query
}
response = rq.post(GRAPHQL_ENDPOINT, headers=headers) #data=json.dumps(payload))
if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f"Request failed with status code: {response.status_code}")
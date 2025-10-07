import requests as rq
import json

myAPI = "cnE7TzLHIOiOL5iBw2YrdpS7tn8iEbyVya7JtPXA" 

headers = {
    "x-api-key": myAPI,
    "Content-Type": "application/json"
}

GRAPHQL_ENDPOINT = "https://api-op.grid.gg/central-data/graphql"

graphql_query = """
query Series {
    allSeries (
        first: 50,
        filter: {
            titleId: 1
            types: ESPORTS
        }
        orderBy: StartTimeScheduled
        orderDirection: DESC
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

response = rq.post(GRAPHQL_ENDPOINT, headers=headers, data=json.dumps(payload))

if response.status_code == 200:
    data = response.json()
    print(json.dumps(data, indent=2))
else:
    print(f"Request failed with status code: {response.status_code}")
    print(f"Response: {response.text}")
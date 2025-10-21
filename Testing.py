import requests as rq
import json

myAPI = "cnE7TzLHIOiOL5iBw2YrdpS7tn8iEbyVya7JtPXA"

headers = {
    "x-api-key": myAPI,
    "Content-Type": "application/json"
}

SERIES_STATE_ENDPOINT = "https://api-op.grid.gg/live-data-feed/series-state/graphql"

# Check the problematic types
types_to_check = ["Coordinates", "PlayerInventory", "MapState"]

for type_name in types_to_check:
    introspection_query = f"""
    {{
        __type(name: "{type_name}") {{
            name
            fields {{
                name
                type {{
                    name
                    kind
                    ofType {{
                        name
                        kind
                    }}
                }}
            }}
        }}
    }}
    """
    
    payload = {"query": introspection_query}
    response = rq.post(SERIES_STATE_ENDPOINT, headers=headers, json=payload, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        print("\n" + "="*60)
        print(f"FIELDS IN {type_name}")
        print("="*60)
        
        if 'data' in data and '__type' in data['data'] and data['data']['__type']:
            fields = data['data']['__type']['fields']
            if fields:
                for field in fields:
                    field_type = field['type']
                    if field_type.get('name'):
                        type_info = field_type['name']
                    elif field_type.get('ofType'):
                        type_info = field_type['ofType'].get('name', 'Unknown')
                    else:
                        type_info = field_type.get('kind', 'Unknown')
                    print(f"  • {field['name']}: {type_info}")
            else:
                print(f"  No fields (might be a scalar)")
        else:
            print(f"  Type not found or is a scalar")

print("\n" + "="*60)
print("Corrected query for series 28")
print("="*60)

# Corrected query without z coordinate and weapons
graphql_query = """
query GetSeriesStateWithClock($seriesId: ID!) {
    seriesState(id: $seriesId) {
        id
        version
        format
        started
        finished
        valid
        updatedAt
        startedAt
        duration
        title {
            nameShortened
        }
        teams {
            id
            name
        }
        games {
            id
            sequenceNumber
            type
            started
            finished
            paused
            startedAt
            duration
            clock {
                id
                type
                ticking
                ticksBackwards
                currentSeconds
            }
            map {
                name
            }
            teams {
                id
                name
                side
                won
                score
                money
                loadoutValue
                kills
                deaths
                players {
                    id
                    name
                    money
                    loadoutValue
                    kills
                    deaths
                    killAssistsReceived
                    killAssistsGiven
                    position {
                        x
                        y
                    }
                }
            }
            segments {
                id
                type
                sequenceNumber
                started
                finished
                startedAt
                duration
            }
        }
    }
}
"""

variables = {"seriesId": "28"}
payload = {
    "query": graphql_query,
    "variables": variables
}

response = rq.post(SERIES_STATE_ENDPOINT, headers=headers, json=payload, timeout=10)

if response.status_code == 200:
    data = response.json()
    
    if 'errors' in data:
        print("⚠️  Errors occurred:")
        print(json.dumps(data['errors'], indent=2))
    
    if 'data' in data:
        print("\n✅ SUCCESS! Series State Data:")
        print(json.dumps(data, indent=2))
        
        # Print formatted clock information
        series = data['data']['seriesState']
        print("\n" + "="*60)
        print(f"Series {series['id']} - {series['format']}")
        print(f"Status: {'Finished' if series['finished'] else 'Ongoing'}")
        print(f"Duration: {series['duration']}")
        print("="*60)
        
        for game in series.get('games', []):
            print(f"\n🎮 Game {game.get('sequenceNumber', '?')}:")
            print(f"   Status: {'Finished' if game.get('finished') else 'Ongoing'}")
            
            if game.get('clock'):
                clock = game['clock']
                direction = "⬇️ Counting down" if clock['ticksBackwards'] else "⬆️ Counting up"
                status = "🟢 Ticking" if clock['ticking'] else "⏸️  Paused"
                print(f"   ⏰ Clock: {clock['currentSeconds']}s ({direction}, {status})")
                print(f"   Clock Type: {clock['type']}")
            
            for team in game.get('teams', []):
                print(f"\n   Team: {team['name']} ({team.get('side', 'N/A')})")
                print(f"   Score: {team.get('score', 0)} | K/D: {team.get('kills', 0)}/{team.get('deaths', 0)}")
                print(f"   Money: ${team.get('money', 0):,}")
else:
    print(f"❌ Request failed: {response.status_code}")
    print(response.text)
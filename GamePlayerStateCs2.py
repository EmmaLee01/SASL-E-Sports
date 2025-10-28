import requests as rq
import json

myAPI = "cnE7TzLHIOiOL5iBw2YrdpS7tn8iEbyVya7JtPXA"

headers = {
    "x-api-key": myAPI,
    "Content-Type": "application/json"
}

SERIES_STATE_ENDPOINT = "https://api-op.grid.gg/live-data-feed/series-state/graphql"

# Check ItemStack fields
introspection_query = """
{
    __type(name: "ItemStack") {
        name
        fields {
            name
            type {
                name
                kind
                ofType {
                    name
                    kind
                }
            }
        }
    }
}
"""

payload = {"query": introspection_query}
response = rq.post(SERIES_STATE_ENDPOINT, headers=headers, json=payload, timeout=10)

if response.status_code == 200:
    data = response.json()
    print("="*60)
    print("FIELDS IN ItemStack")
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

print("\n" + "="*60)
print("CORRECTED QUERY")
print("="*60)

# Corrected query without 'type' field in items
graphql_query = """
query GetCS2SeriesState($seriesId: ID!) {
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
                netWorth
                kills
                deaths
                killAssistsReceived
                killAssistsGiven
                teamkills
                selfkills
                structuresDestroyed
                structuresCaptured
                firstKill
                players {
                    id
                    name
                    participationStatus
                    money
                    loadoutValue
                    netWorth
                    kills
                    deaths
                    killAssistsReceived
                    killAssistsGiven
                    firstKill
                    teamkills
                    teamkillAssistsReceived
                    teamkillAssistsGiven
                    selfkills
                    structuresDestroyed
                    structuresCaptured
                    position {
                        x
                        y
                    }
                    character {
                        name
                    }
                    inventory {
                        items {
                            name
                        }
                    }
                    weaponKills {
                        id
                        weaponName
                        count
                    }
                    multikills {
                        id
                        numberOfKills
                        count
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
        print("\nWARNING: Errors occurred:")
        for error in data['errors']:
            print(f"  - {error['message']}")
    
    if 'data' in data and data['data'] and data['data']['seriesState']:
        series = data['data']['seriesState']
        
        print("\n" + "="*60)
        print(f"CS2 Series {series['id']} - {series['format']}")
        print(f"Status: {'Finished' if series['finished'] else 'Ongoing'}")
        print(f"Duration: {series['duration']}")
        print("="*60)
        
        for game in series.get('games', []):
            print(f"\nGame {game.get('sequenceNumber', '?')}")
            print(f"   Map: {game.get('map', {}).get('name', 'Unknown')}")
            print(f"   Status: {'Finished' if game.get('finished') else 'Ongoing'}")
            
            if game.get('clock'):
                clock = game['clock']
                mins = clock['currentSeconds'] // 60
                secs = clock['currentSeconds'] % 60
                direction = "DOWN" if clock['ticksBackwards'] else "UP"
                status = "TICKING" if clock['ticking'] else "PAUSED"
                print(f"   Clock: {mins:02d}:{secs:02d} (Counting {direction}, {status})")
            
            for team in game.get('teams', []):
                print(f"\n   {'='*50}")
                print(f"   {team['name']} ({team.get('side', 'N/A').upper()})")
                print(f"   {'='*50}")
                won_status = " [WON]" if team.get('won') else ""
                print(f"   Score: {team.get('score', 0)}{won_status}")
                print(f"   K/D: {team.get('kills', 0)}/{team.get('deaths', 0)}")
                print(f"   Team Money: ${team.get('money', 0):,}")
                print(f"   Team Equipment Value: ${team.get('loadoutValue', 0):,}")
                
                if team.get('players'):
                    print(f"\n   Players:")
                    for player in team['players']:
                        print(f"\n      {player['name']}")
                        print(f"         K/D/A: {player.get('kills', 0)}/{player.get('deaths', 0)}/{player.get('killAssistsReceived', 0)}")
                        print(f"         Money: ${player.get('money', 0):,} | Equipment: ${player.get('loadoutValue', 0):,}")
                        
                        if player.get('position'):
                            pos = player['position']
                            print(f"         Position: ({pos.get('x', 0):.1f}, {pos.get('y', 0):.1f})")
                        
                        # Display inventory
                        if player.get('inventory') and player['inventory'].get('items'):
                            items = player['inventory']['items']
                            if items:
                                item_names = [item.get('name', 'Unknown') for item in items]
                                print(f"         Inventory: {', '.join(item_names)}")
                        
                        # Display weapon kills breakdown
                        if player.get('weaponKills'):
                            weapon_kills = player['weaponKills']
                            if weapon_kills:
                                print(f"         Weapon Kills:")
                                for wk in weapon_kills:
                                    print(f"            {wk.get('weaponName', 'Unknown')}: {wk.get('count', 0)}")
                        
                        # Display multikills
                        if player.get('multikills'):
                            multikills = player['multikills']
                            if multikills:
                                print(f"         Multikills:")
                                for mk in multikills:
                                    kill_type = {2: "Double", 3: "Triple", 4: "Quad", 5: "Ace"}.get(mk.get('numberOfKills', 0), f"{mk.get('numberOfKills', 0)}-kill")
                                    print(f"            {kill_type}: {mk.get('count', 0)}x")
        
        # Save full data to file
        with open('cs2_series_28_full_data.json', 'w') as f:
            json.dump(data, f, indent=2)
        print("\nFull data saved to 'cs2_series_28_full_data.json'")
        
    else:
        print("\nERROR: No data returned")
        print("Full response:")
        print(json.dumps(data, indent=2))
        
else:
    print(f"ERROR: Request failed: {response.status_code}")
    print(response.text)
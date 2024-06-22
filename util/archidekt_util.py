"""
    Module provides utility functions for archidekt
"""
import json
import requests
import os
import sys
import time
#partners would be commanders="p1","p2" not "p1,p2"
#SEARCH_LINK = "https://www.archidekt.com/api/decks/?commanders={}&pageSize=50&size=100&formats=3&orderBy=-createdAt"
#DECK_LINK = "https://www.archidekt.com/api/decks/{}/"

def get_x_ids_helper(link):
    """repeatedly gets the page from archidekt until it responds with the json"""
    delay = 5
    failures = []
    while True:
        time.sleep(delay)
        response = requests.get(link)
        if response.status_code == 429:
            print("\nToo Many Requests")
            sys.exit(0)
        if response.status_code != 200:
            failures.append(response.status_code)
            if len(failures) >= 5:
                print("\nERROR:5 Failures:",failures)
                sys.exit(0)
            else:
                continue
        try:
            json_data = json.loads(response.content)
        except json.decoder.JSONDecodeError as e:
            print("\nERROR: JSON read error,"+str(e))
            continue
        if json_data["results"] == [] and json_data["count"] != 0:
            print("\nERROR: Empty Data. Retrying")
            continue
        return json_data
        
def get_x_ids(commander: str,x: int):
    """Goes through a search of the most recent decks for a given commander and gets the deck ids"""
    page_size = 50
    if x < 50:
        page_size = x 
    commander_name = "\""+commander.replace(' ','+')+"\""
    #TODO: use requests.get(...,parems={"commanders":something,pageSize:100})
    link = "https://www.archidekt.com/api/decks/?commanders={}&pageSize={}&size=100&formats=3&orderBy=-createdAt".format(commander_name,page_size)
    print("Searching for Decks")
    archidekt_decks = get_x_ids_helper(link)
    if archidekt_decks["count"] < x:
        print("WARNING: Archidekt does not have",str(x),"decks for",commander+". They have",archidekt_decks["count"])
        x = archidekt_decks["count"]
    deck_ids = dict()
    for deck in archidekt_decks["results"]:
        deck_ids[deck["id"]] = dict()
        deck_ids[deck["id"]]["MTGD_Commander"] = commander
        deck_ids[deck["id"]]["MTGD_DeckCard"] = deck
    digits = len(str(x))
    print("Getting Deck IDs:{}/{}".format(str(len(deck_ids)).zfill(digits),x),end="\r")
    while archidekt_decks["next"] and len(deck_ids) < x:
        archidekt_decks = get_x_ids_helper(archidekt_decks["next"])
        for deck in archidekt_decks["results"]:
            if len(deck_ids) < x:
                deck_ids[deck["id"]] = dict()
                deck_ids[deck["id"]]["MTGD_Commander"] = commander
                deck_ids[deck["id"]]["MTGD_DeckCard"] = deck
        print("Getting Deck IDs:{}/{}".format(str(len(deck_ids)).zfill(digits),x),end="\r")
    print()
    return deck_ids


def download_decks_helper(link):
    """repeatedly loads the deck until it returns the json"""
    delay = 1
    failures = []
    while True:
        time.sleep(delay)
        response = requests.get(link)
        if response.status_code == 429:
            print()
            print("Too Many Requests")
            sys.exit(0)
        if response.status_code != 200:
            failures.append(response.status_code)
            if len(failures) >= 5:
                print("ERROR:5 Failures:",failures)
                sys.exit(0)
            else:
                continue
        try:
            json_data = json.loads(response.content)
        except json.decoder.JSONDecodeError as e:
            print()
            print("ERROR: JSON read error,"+str(e))
            continue
        return json_data

def download_decks(deck_ids):
    """downloads the json for archidekt decks for a given list of ids"""
    if not os.path.isdir('data'):
        os.mkdir('data')
    if not os.path.isdir('data/archidekt'):
        os.mkdir('data/archidekt')
    digits = len(str(len(deck_ids)))
    counter = 0
    for deck_id in deck_ids.keys():
        counter += 1
        print("Downloading:{}/{}".format(str(counter).zfill(digits),len(deck_ids)),end="\r")
        if not os.path.exists('data/archidekt/'+str(deck_id)+".json"):
            link = "https://www.archidekt.com/api/decks/{}/".format(deck_id)
            deck_data = download_decks_helper(link)
            deck_data["MTGD_Meta"] = deck_ids[deck_id]
            with open('data/archidekt/'+str(deck_id)+".json","w+",encoding='utf-8') as f:
                json.dump(deck_data,f)
    print()

def download_deck(deck_id: int):
    """Downloads a deck for a given deck id"""
    if not os.path.isdir('data'):
        os.mkdir('data')
    if not os.path.isdir('data/archidekt'):
        os.mkdir('data/archidekt')
    if not os.path.exists('data/archidekt/'+str(deck_id)+".json"):
        #getting deck json from api
        link = "https://www.archidekt.com/api/decks/{}/".format(deck_id)
        time.sleep(2)
        deck_data = json.loads(requests.get(link).content)
        with open('data/archidekt/'+str(deck_id)+".json","w+",encoding='utf-8') as f:
            json.dump(deck_data,f)

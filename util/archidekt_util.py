import json
import requests
import os
import sys
import time
class archidekt_util:
    #partners would be commanders="p1","p2" not "p1,p2"
    #SEARCH_LINK = "https://www.archidekt.com/api/decks/?commanders={}&pageSize=50&size=100&formats=3&orderBy=-createdAt"
    #DECK_LINK = "https://www.archidekt.com/api/decks/{}/"

    @staticmethod
    def get_commander(deck):
        for card in deck["cards"]: 
            if "Commander" in card["categories"]:
                return card["card"]["oracleCard"]["name"]
        return "ERROR"

    @staticmethod
    def get_x_ids_helper(link):
        delay = 1
        failures = []
        while True:
            time.sleep(delay)
            response = requests.get(link)
            print("STATUS:",response.status_code)
            if response.status_code == 429:
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
                print("ERROR: JSON read error,"+str(e))
                continue
            if json_data["results"] == [] and json_data["count"] != 0:
                print("ERROR: Empty Data. Retrying")
                continue
            return json_data
            
    @staticmethod
    def get_x_ids(commander: str,x: int):
        page_size = 50
        if x < 50:
            page_size = x 
        commander_name = "\""+commander.replace(' ','+')+"\""
        #TODO: use requests.get(...,parems={"commanders":something,pageSize:100})
        link = "https://www.archidekt.com/api/decks/?commanders={}&pageSize={}&size=100&formats=3&orderBy=-createdAt".format(commander_name,page_size)
        print("Searching for Decks")
        archidekt_decks = archidekt_util.get_x_ids_helper(link)
        if archidekt_decks["count"] < x:
            print("WARNING: Archidekt does not have",str(x),"decks for",commander+". They have",archidekt_decks["count"])
            x = archidekt_decks["count"]
        deck_ids = set()
        for deck in archidekt_decks["results"]:
            deck_ids.add(deck["id"])  
        digits = len(str(x))
        print("Getting Deck IDs:{}/{}".format(str(len(deck_ids)).zfill(digits),x),end="\r")
        while archidekt_decks["next"] and len(deck_ids) < x:
            archidekt_decks = archidekt_util.get_x_ids_helper(archidekt_decks["next"])
            for deck in archidekt_decks["results"]:
                if len(deck_ids) < x:
                    deck_ids.add(deck["id"])  
            print("Getting Deck IDs:{}/{}".format(str(len(deck_ids)).zfill(digits),x),end="\r")
        print()
        return deck_ids


    @staticmethod
    def download_decks_helper(link):
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

    @staticmethod
    def download_decks(deck_ids):
        if not os.path.isdir('data'):
            os.mkdir('data')
        if not os.path.isdir('data/archidekt'):
            os.mkdir('data/archidekt')
        digits = len(str(len(deck_ids)))
        counter = 0
        for deck_id in deck_ids:
            counter += 1
            print("Downloading:{}/{}".format(str(counter).zfill(digits),len(deck_ids)),end="\r")
            if not os.path.exists('data/archidekt/'+str(deck_id)+".json"):
                link = "https://www.archidekt.com/api/decks/{}/".format(deck_id)
                deck_data = archidekt_util.download_decks_helper(link)
                with open('data/archidekt/'+str(deck_id)+".json","w+") as f:
                    json.dump(deck_data,f)
        print()

    @staticmethod
    def download_deck(deck_id: int):
        if not os.path.isdir('data'):
            os.mkdir('data')
        if not os.path.isdir('data/archidekt'):
            os.mkdir('data/archidekt')
        if not os.path.exists('data/archidekt/'+str(deck_id)+".json"):
            #getting deck json from api
            link = "https://www.archidekt.com/api/decks/{}/".format(deck_id)
            time.sleep(2)
            deck_data = json.loads(requests.get(link).content)
            with open('data/archidekt/'+str(deck_id)+".json","w+") as f:
                json.dump(deck_data,f)

    @staticmethod
    def get_deck(deck_id):
        #getting deck json from api
        link = "https://www.archidekt.com/api/decks/{}/".format(deck_id)
        deck_data = json.loads(requests.get(link).content)
        return deck_data
        
    @staticmethod
    def lookup_deck(deck_id):
        #getting deck json from api
        link = "https://www.archidekt.com/api/decks/{}/".format(deck_id)
        deck_data = json.loads(requests.get(link).content)

        #parsing the deck to cards
        in_deck_categories = set()
        for cat in deck_data["categories"]:
            if cat["includedInDeck"]:
                in_deck_categories.add(cat["name"])
        cards_in_deck = dict()
        for card in deck_data["cards"]:
            if card["categories"][0] in in_deck_categories:
                cards_in_deck[card["card"]["oracleCard"]["name"]] = card["quantity"]
        return cards_in_deck 

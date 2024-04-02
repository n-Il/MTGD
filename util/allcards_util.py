import sys
import requests
import json
import os

class allcards_util:
    API_LINK = "https://api.scryfall.com/bulk-data/all_cards"

    def __init__(self):
        return
    
    @staticmethod
    def download():
        #get the link to download all cards
        download_link = json.loads(requests.get("https://api.scryfall.com/bulk-data/all_cards").content)["download_uri"]
       
        #if data and AC directories dont exist we make them
        if not os.path.isdir('data'):
            os.mkdir('data')
            os.mkdir('data/AC')
        if not os.path.isdir('data/AC'):
            os.mkdir('data/AC')
        #Download in chunks
        if os.path.exists("data/AC/all-cards-"+download_link.split('-')[-1]):
            print("NEWEST AC EXISTS")
        else:
            chunk_size = 1024 * 1024 #1MB
            download = requests.get(download_link,stream=True)
            with open("data/AC/all-cards-"+download_link.split('-')[-1],"wb") as f:
                for chunk in download.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
    
    @staticmethod
    def filtered_get(card_filter):
        list_of_files = list(map(lambda x: "data/AC/" + x,os.listdir("data/AC")))
        latest = max(list_of_files, key=os.path.getctime)
        cards = dict()
        with open(latest) as f:
            for line in f:
                line = line.strip()#remove the newlines
                if line == "[" or line == "]":
                    continue
                line = line.strip(',')
                #line = line[:-1]#remove the comma at the end
                try:
                    card = json.loads(line)
                    if card_filter(card):
                        if (card["set"],card["collector_number"],card["lang"]) in cards:
                            print("already exists")
                        else:
                            cards[(card["set"],card["collector_number"],card["lang"])] = card
                except Exception as e:
                    print("error")
                    print(line)
        return cards
        

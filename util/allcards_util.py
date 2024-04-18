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
        if not os.path.isdir('data/allcards'):
            os.mkdir('data/allcards')
        #Download in chunks
        if os.path.exists("data/allcards/all-cards-"+download_link.split('-')[-1]):
            print("ERROR: You already have the latest all cards file.")
        else:
            chunk_size = 1024 * 1024 #1MB
            download = requests.get(download_link,stream=True)
            with open("data/allcards/all-cards-"+download_link.split('-')[-1],"wb") as f:
                for chunk in download.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
    
    @staticmethod
    def filtered_get(card_filter,debug = False):
        list_of_files = list(map(lambda x: "data/allcards/" + x,os.listdir("data/allcards")))
        latest = max(list_of_files, key=os.path.getctime)
        cards = dict()
        num_lines = -2#first and last
        if debug:
            with open(latest,"r",encoding='utf-8') as f:
                for line in f:
                    num_lines += 1
        num_lines = str(num_lines)
        len_num_lines = len(num_lines)
        with open(latest,encoding='utf-8') as f:
            counter = 0
            for line in f:
                line = line.strip()#remove the newlines
                if line == "[" or line == "]":
                    continue
                if debug:
                    counter += 1
                    print("Filtering",str(counter).zfill(len_num_lines)+"/"+num_lines,end='\r')
                line = line.strip(',')
                try:
                    card = json.loads(line)
                    if card_filter(card):
                        if (card["set"],card["collector_number"],card["lang"]) in cards:
                            print("ERROR:Card already exists")
                        else:
                            cards[(card["set"],card["collector_number"],card["lang"])] = card
                except Exception as e:
                    print()
                    print("error")
                    print(line)
        if debug:
            print()#move cursor to next line for progress
        return cards
        

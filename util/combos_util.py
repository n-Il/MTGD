import time
import sys
import requests
import json
import os

class combos_util:
    API_LINK = "https://json.commanderspellbook.com/variants.json.gz"

    def __init__(self):
        return
   
    @staticmethod
    def get():
        #read into dict as key=requiredcards,value=combo
        list_of_files = list(map(lambda x: "data/combos/" + x,os.listdir("data/combos"))) 
        latest = max(list_of_files,key=os.path.getctime)
        combos = dict()
        with open(latest,encoding='utf-8') as f:
            combos_json = json.load(f) 
        for combo in combos_json["variants"]:
            required_cards = set()
            for card in combo["uses"]:
                required_cards.add(card["card"]["name"])
            combos[tuple(required_cards)] = combo
        return combos

    @staticmethod
    def download():
        if not os.path.isdir('data'):
            os.mkdir('data')
        if not os.path.isdir('data/combos'):
            os.mkdir('data/combos')
        API_LINK = "https://json.commanderspellbook.com/variants.json.gz"
        combos_data = json.loads(requests.get(API_LINK).content)
        if os.path.exists("data/combos/combos-"+combos_data["timestamp"].replace(':','_')+".json"):
            print("ERROR: You already have the latest combo data.")
        else:
            with open("data/combos/combos-"+combos_data["timestamp"].replace(':','_')+".json","w+",encoding='utf-8') as f:
                json.dump(combos_data,f)

    @staticmethod
    def pp(combos):
        #print more data
        for reqs,combo in combos.items():
            print("Requires:","   ".join(reqs))
            print("    Description:")
            step = 0
            for line in combo["description"].split('\n'):
                step += 1
                line = str(step)+":"+line
                #grab up to 50 characters at a time
                while line:
                    grab = line[:75]
                    print("    "+grab)
                    line = line[75:]
                #print with tab indent
                print()
            print()


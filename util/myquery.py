import requests
from .mycollection import mycollection
import time
class myquery:
    def __init__(self,col,q,**kwargs):
        self.q = q
        self.collection = dict()
        self.response = None
        self.result_cards = []

        #load collection
        self.load_collection(col)
        #run query
        self.get()
        #filter by collection 
        self.page_and_filter()

        del self.collection

        #request
        #self.q = q
        #rest are optional
        #self.unique = None
        #self.order = None
        #self.direction = None
        #self.include_extras = False
        #self.include_multilingual = False
        #self.include_variations = False
        #self.page = None
        #self.format = None
        #self.pretty = False
       
        ##response object error
        #self.object = None
        #self.code = None
        #self.details = None
        #self.status = None
        ##last 2 can be null or missing
        #self.warnings = None
        #self.type = None
        #
        ##response object list
        #self.object = None
        #self.has_more = None
        #self.data = None
        ##last 3 can be null or missing
        #self.total_cards = None
        #self.next_page = None
        #self.warnings = None

    def load_collection(self,col):
        for card in col.cards:
            if card["name"] in self.collection:
                self.collection[card["name"]].append(card)
            else:
                self.collection[card["name"]] = [card]
    
    def get(self):
        card_names = {}
        r = requests.get("https://api.scryfall.com/cards/search",params={"q":self.q})
        response = r.json()
        if response["object"] == "error":
            print("ERROR:error type "+str(r)+"\n"+str(response))
        elif response["object"] == "list":
            if "warnings" in response:
                print("WARNINGS:",response["warnings"])
            self.response = response
        else:
            print("ERROR:Unkown Response Object",r["object"])


    def page_and_filter(self):
        while True:
            for card in self.response["data"]:
                if card["name"] in self.collection:
                    #remove list from collection, add it to results cards
                    self.result_cards.extend(self.collection.pop(card["name"]))
            if not self.response["has_more"]:
                break
            else: 
                time.sleep(.2)
                self.response = requests.get(self.response["next_page"]).json()


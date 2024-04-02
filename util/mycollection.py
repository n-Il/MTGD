import json
import os
class mycollection:
    def __init__(self):
        self.cards = []

    def load_from_file(self,file = "mycollection.json"):
        with open(file) as f:
            self.cards = json.load(f)

    def count_cards(self):
        sum = 0
        for card in self.cards:
            sum+=card["MTGD_foil_count"]
            sum+=card["MTGD_nonfoil_count"]
        return sum

    #price
    def price_info(self):
        cards_over_1,cards_over_5,cards_over_10,cards_over_25,cards_over_50,cards_over_100 = 0,0,0,0,0,0
        sum_ignore_bulk = 0.0
        sum_price = 0.0
        errors = 0
        errors_foil = 0
        for card in self.cards:
            if card["MTGD_foil_count"] > 0:
                if card["prices"]["usd_foil"] != None:
                    price = float(card["prices"]["usd_foil"])
                    if price >= 100:
                        cards_over_100 += card["MTGD_foil_count"]
                    elif price >= 50:
                        cards_over_50 += card["MTGD_foil_count"]
                    elif price >= 25:
                        cards_over_25 += card["MTGD_foil_count"]
                    elif price >= 10:
                        cards_over_10 += card["MTGD_foil_count"]
                    elif price >= 5:
                        cards_over_5 += card["MTGD_foil_count"]
                    elif price>= 1:
                        cards_over_1 += card["MTGD_foil_count"]
                    sum_price += (price * card["MTGD_foil_count"])
                    if price >= 1:
                        sum_ignore_bulk += (price * card["MTGD_foil_count"])
                else:
                    errors_foil += card["MTGD_foil_count"]
            if card["MTGD_nonfoil_count"] > 0:
                if card["prices"]["usd"] != None:
                    price =  float(card["prices"]["usd"])
                    if price >= 100:
                        cards_over_100 += card["MTGD_nonfoil_count"]
                    elif price >= 50:
                        cards_over_50 += card["MTGD_nonfoil_count"]
                    elif price >= 25:
                        cards_over_25 += card["MTGD_nonfoil_count"]
                    elif price >= 10:
                        cards_over_10 += card["MTGD_nonfoil_count"]
                    elif price >= 5:
                        cards_over_5 += card["MTGD_nonfoil_count"]
                    elif price>= 1:
                        cards_over_1 += card["MTGD_nonfoil_count"]
                    sum_price += (price * card["MTGD_nonfoil_count"])
                    if price >= 1:
                        sum_ignore_bulk += (price * card["MTGD_nonfoil_count"])
                else:
                    errors += card["MTGD_nonfoil_count"]
        print("Price Lookup Errors Non-Foil:",errors)
        print("Price Lookup Errors Foil:",errors_foil)
        print("Cards Over $1:",cards_over_1)
        print("Cards Over $5:",cards_over_5)
        print("Cards Over $10:",cards_over_10)
        print("Cards Over $25:",cards_over_25)
        print("Cards Over $50:",cards_over_50)
        print("Cards Over $100:",cards_over_100)
        print("Estimated Total Value: ${:.2f} USD".format(sum_price))
        print("Estimated Total Value(Ignoring <1$ cards): ${:.2f} USD".format(sum_ignore_bulk))

    def foil_info(self):
        foils = 0
        non_foils = 0
        for card in self.cards:
            foils += card["MTGD_foil_count"]
            non_foils += card["MTGD_nonfoil_count"]
        print("Foils:",foils)
        print("Non-Foils:",non_foils)

    def set_info(self):
        sets = dict()
        for card in self.cards:
            if card["set_name"] in sets:
                sets[card["set_name"]] += card["MTGD_nonfoil_count"]
                sets[card["set_name"]] += card["MTGD_foil_count"]
            else:
                sets[card["set_name"]] = card["MTGD_foil_count"] + card["MTGD_nonfoil_count"]

        #sort descending 
        sorted_sets = {k: v for k, v in sorted(sets.items(), key=lambda item: item[1],reverse=True)}
        print("Top 20 Sets from your collection")
        for s,c in list(sorted_sets.items())[:20]:
            print(c,"cards from",s)

    def topcards_info(self):
        names = dict()
        for card in self.cards:
            if card["name"] in names:
                names[card["name"]] += card["MTGD_foil_count"]
                names[card["name"]] += card["MTGD_nonfoil_count"]
            else:
                names[card["name"]] = card["MTGD_foil_count"] + card["MTGD_nonfoil_count"]

        #sort descending 
        sorted_names = {k: v for k, v in sorted(names.items(), key=lambda item: item[1],reverse=True)}
        print("Top 20 Cards from your collection")
        for s,c in list(sorted_names.items())[:20]:
            print(c,"copies of",s)
    
    def spit_out_sheet(self):
        if os.path.exists("output_sheet.csv"):
            print("output_sheet.csv already exists")
        else:
            with open("output_sheet.csv","w") as f:
                f.write("Count,Name,Price,Set,CN,Foil,Lang,CMC\n")
                for card in self.cards:
                    if card["MTGD_foil_count"] > 0:
                        line = ""
                        #count
                        line += str(card["MTGD_foil_count"]) + ","
                        #name
                        line += "\""+card["name"] + "\","
                        #price
                        line += (str(card["prices"]["usd_foil"]) if card["prices"]["usd_foil"] else "ERROR") + ","
                        #set
                        line += card["set"] + ","
                        #cn
                        line += card["collector_number"] + ","
                        #foil
                        line += "Yes,"
                        #lang
                        line += card["lang"] + ","
                        #CMC
                        line += str(card["cmc"]) + "\n"
                        f.write(line)
                    if card["MTGD_nonfoil_count"] > 0:
                        line = ""
                        #count
                        line += str(card["MTGD_nonfoil_count"]) + ","
                        #name
                        line += "\""+card["name"] + "\","
                        #price
                        line += (str(card["prices"]["usd"]) if card["prices"]["usd"] else "ERROR") + ","
                        #set
                        line += card["set"] + ","
                        #cn
                        line += card["collector_number"] + ","
                        #foil
                        line += ","
                        #lang
                        line += card["lang"] + ","
                        #CMC
                        line += str(card["cmc"]) + "\n"
                        f.write(line)

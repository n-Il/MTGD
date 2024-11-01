"""
    Module provides the mycollection class
"""
import json
import os
import util.sheets_util as sheets_util
import util.combos_util as combos_util
import requests
import time

def delete_collection_file():
    collection_location = "data/collection/mycollection.json"
    if os.path.exists(collection_location):
        os.remove(collection_location) 

class mycollection:
    """
        Represents a card collection
    """
    def __init__(self):
        self.cards = []

    def get_set_of_names(self):
        """returns a set of card names from the collection"""
        result = set()
        for card in self.cards:
            result.add(card["name"])
        return result
    
    def get_names_and_counts(self):
        """returns a set of card names and counts from the collection"""
        result = dict()
        for card in self.cards:
            if card["name"] in result:
                result[card["name"]] += (card["MTGD_foil_count"] + card["MTGD_nonfoil_count"])
            else:
                result[card["name"]] = card["MTGD_foil_count"] + card["MTGD_nonfoil_count"]
        return result

    def load_from_file(self,file = "data/collection/mycollection.json"):
        """Loads the collection from the collection file"""
        if not os.path.exists(file):
            print("ERROR:"+str(file),"doesn't exist, please run '-collect'")
            return False
        else:
            with open(file,encoding='utf-8') as f:
                self.cards = json.load(f)
                return True

    def count_cards(self):
        """Gets a total count of cards within the collection"""
        sum = 0
        for card in self.cards:
            sum+=card["MTGD_foil_count"]
            sum+=card["MTGD_nonfoil_count"]
        return sum
    
    def price_info(self):
        """Prints out summary information about pricing"""
        english_print_lookups = dict()
        for card in self.cards:
            if "MTGD_extra" in card:
                english_print_lookups[(card["set"],card["collector_number"])] = card["prices"]
        cards_over_1,cards_over_5,cards_over_10,cards_over_25,cards_over_50,cards_over_100 = 0,0,0,0,0,0
        sum_ignore_bulk = 0.0
        sum_price = 0.0
        errors = 0
        errors_nonenglish = 0
        errors_english = 0
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
                    if card["lang"] != "en":
                        if english_print_lookups[(card["set"],card["collector_number"])]["usd_foil"] != None:
                            print("Using english price for",card["name"]+". ["+card["set"]+","+card["collector_number"]+","+card["lang"]+"]")
                            price = float(english_print_lookups[(card["set"],card["collector_number"])]["usd_foil"])
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
                            errors_nonenglish += card["MTGD_foil_count"]
                    else:
                        errors_foil += card["MTGD_foil_count"]
                        errors_english += card["MTGD_foil_count"]
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
                    if card["lang"] != "en":
                        if (card["set"],card["collector_number"]) in english_print_lookups and english_print_lookups[(card["set"],card["collector_number"])]["usd"] != None:
                            print("Using english price for",card["name"]+". ["+card["set"]+","+card["collector_number"]+","+card["lang"]+"]")
                            price = float(english_print_lookups[(card["set"],card["collector_number"])]["usd"])
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
                            errors_nonenglish += card["MTGD_nonfoil_count"]
                    else:
                        errors += card["MTGD_nonfoil_count"]
                        errors_english += card["MTGD_nonfoil_count"]

        print("Price Lookup Errors Non-Foil:",errors)
        print("vs Price Lookup Errors Foil:",errors_foil)
        print("Price Lookup Errors Non-English:",errors_nonenglish)
        print("vs Price Lookup Errors English:",errors_english)
        print("Cards Over $1:",cards_over_1)
        print("Cards Over $5:",cards_over_5)
        print("Cards Over $10:",cards_over_10)
        print("Cards Over $25:",cards_over_25)
        print("Cards Over $50:",cards_over_50)
        print("Cards Over $100:",cards_over_100)
        print("Estimated Total Value: ${:.2f} USD".format(sum_price))
        print("Estimated Total Value(Ignoring <1$ cards): ${:.2f} USD".format(sum_ignore_bulk))

    def foil_info(self):
        """Prints out foil and nonfoil counts"""
        foils = 0
        non_foils = 0
        for card in self.cards:
            foils += card["MTGD_foil_count"]
            non_foils += card["MTGD_nonfoil_count"]
        print("Foils:",foils)
        print("Non-Foils:",non_foils)

    def set_info(self):
        """Prints out a summary of sets and how many cards you have from them"""
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
        """Prints out a summary of the cards that you have the most copies of"""
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

    def rarity_info(self):
        """Prints out each rarity and how many cards you have from it"""
        rarities = dict()
        for card in self.cards:
            if card["rarity"] in rarities:
                rarities[card["rarity"]] += card["MTGD_foil_count"]
                rarities[card["rarity"]] += card["MTGD_nonfoil_count"]
            else:
                rarities[card["rarity"]] = card["MTGD_foil_count"] + card["MTGD_nonfoil_count"]
        sorted_rarities = {k: v for k, v in sorted(rarities.items(), key=lambda item: item[1],reverse=True)}
        print("Rarity Counts:")
        for s,c in list(sorted_rarities.items()):
            print(c,str(s)+"s")
                
    
    def spit_out_sheet(self):
        """Creates an output sheet, which is a more human readable form of the collection"""
        if os.path.exists("output_sheet.csv"):
            print("ERROR:output_sheet.csv already exists")
        else:
            if not os.path.isdir('data'):
                os.mkdir('data')
            if not os.path.isdir('data/output'):
                os.mkdir('data/output')
            with open("data/output/output_sheet.csv","w",encoding='utf-8') as f:
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

    def spit_out_create(self):
        """Creates a show create sheet, which is a csv that can be used as a sheet to generate the collection"""
        if os.path.exists("show_create_sheet.csv"):
            print("ERROR:show_create_sheet.csv already exists")
        else:
            if not os.path.isdir('data'):
                os.mkdir('data')
            if not os.path.isdir('data/output'):
                os.mkdir('data/output')
            with open("data/output/show_create_sheet.csv","w",encoding='utf-8') as f:
                f.write("Count,Set,Set# (useme★),Card Name,Foil,List,Language(if not english)\n")
                for card in self.cards:
                    if card["MTGD_foil_count"] > 0:
                        line = ""
                        #count?
                        if card["MTGD_foil_count"] > 1:
                            line += str(card["MTGD_foil_count"])
                        line += ","
                        #set
                        if card["set"] == "plst":
                            split = card["collector_number"].split("-")
                            line += split[0]
                            line += ","
                            #set#
                            line += split[1]
                            line += ","
                            line += ","
                        else:
                            line += card["set"].upper()
                            line += ","
                            #set#
                            line+= card["collector_number"]
                            line += ","
                            line += ","
                        #foil
                        line += "Yes,"
                        #list?
                        if card["set"] == "plst":
                            line+="Yes"
                        line += ","
                        #language?
                        if card["lang"] != "en":
                            line += sheets_util.get_wotc_lang(card["lang"])
                        line += "\n"
                        f.write(line)
                    if card["MTGD_nonfoil_count"] > 0:
                        line = ""
                        #count?
                        if card["MTGD_nonfoil_count"] > 1:
                            line += str(card["MTGD_nonfoil_count"])
                        line += ","
                        #set
                        if card["set"] == "plst":
                            split = card["collector_number"].split("-")
                            line += split[0]
                            line += ","
                            #set#
                            line += split[1]
                            line += ","
                            line += ","
                        else:
                            line += card["set"].upper()
                            line += ","
                            #set#
                            line+= card["collector_number"]
                            line += ","
                            line += ","
                        #foil
                        line += ","
                        #list?
                        if card["set"] == "plst":
                            line+="Yes"
                        line += ","
                        #language?
                        if card["lang"] != "en":
                            line += sheets_util.get_wotc_lang(card["lang"])
                        line += "\n"
                        f.write(line)

    def get_images(self):
        """downloads the images for a collection"""
        if not os.path.isdir('data'):
            os.mkdir('data')
        if not os.path.exists("data/images"):
            os.mkdir("data/images")
        len_cards = str(len(self.cards))
        digits_len_cards = len(len_cards)
        counter = 0
        for card in self.cards:
            counter += 1
            print("Downloading",str(counter).zfill(digits_len_cards)+"/"+len_cards,end='\r')
            if not os.path.exists("data/images/"+str(card["set"])):
                os.mkdir("data/images/"+str(card["set"]))
            #if image already there, skip download
            if not os.path.exists("data/images/"+str(card["set"])+"/"+str(card["collector_number"])+"_"+card["lang"]+".png"):
                #print("Downloading:",str(counter)+"/"+len_cards,"("+card["name"]+")")
                if "image_uris" not in card.keys() and "card_faces" in card.keys():
                    if len(card["card_faces"]) > 2:
                        print("\nERROR:Found a card with more than 2 faces, I dont even....\n")
                    else:
                        #download front image as normal
                        with open("data/images/"+str(card["set"])+"/"+str(card["collector_number"])+"_"+card["lang"]+".png", "wb") as f:
                            f.write(requests.get(card["card_faces"][0]["image_uris"]["png"]).content)
                            time.sleep(0.2)#200 milliseconds
                        #download back image with back
                        with open("data/images/"+str(card["set"])+"/"+str(card["collector_number"])+"_"+card["lang"]+"back.png", "wb") as f:
                            f.write(requests.get(card["card_faces"][1]["image_uris"]["png"]).content)
                            time.sleep(0.2)
                else:
                    with open("data/images/"+str(card["set"])+"/"+str(card["collector_number"])+"_"+card["lang"]+".png", "wb") as f:
                        f.write(requests.get(card["image_uris"]["png"]).content)
                        time.sleep(0.2)#1 seconds = 1000 milliseconds
            else:
                pass
                #print("Skipping:",str(counter)+"/"+len_cards,"("+card["name"]+")")
        print()#move cursor to next line for progress

    def get_combos(self):
        """load the combo data and find combos that are within the collection"""
        combos = combos_util.get()
        if combos:
            my_cards = self.get_set_of_names()
            #remove combos not in collection
            for reqs in list(combos.keys()):
                if sum(map(lambda x: x in my_cards,reqs)) == len(reqs):
                    #print("has combo:",reqs)
                    pass
                else:
                    combos.pop(reqs)
            return combos

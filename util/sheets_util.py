import sys
import requests
import json
import os
from .allcards_util import allcards_util

class sheets_util:
    
    @staticmethod
    def get_sheets():
        sheets = dict()
        if not os.path.isdir('sheets'):
            print("ERROR:No sheets directory")
            sys.exit(0)
        sheet_files = list(map(lambda x: "sheets/" + x,os.listdir("sheets")))
        for sheet_file in sheet_files:
            if os.path.isfile(sheet_file) and sheet_file[-4:] == ".csv":
                sheet = []
                with open(sheet_file,encoding='utf-8') as f:
                    for line in f.readlines()[1:]:
                        card = dict()
                        card_split = line.strip().split(',')
                        card["count"] = 1 if card_split[0] == "" else int(card_split[0])
                        card["set"] = card_split[1].lower()
                        card["cn"] = card_split[2]
                        card["name"] = card_split[3]#almost always empty
                        card["foil"] = False if card_split[4] == "" else True
                        card["list"] = False if card_split[5] == "" else True
                        card["lang"] = "en" if card_split[6] == "" else sheets_util.get_scryfall_lang(card_split[6]) 
                        if card["list"]:
                            card["cn"] = card["set"].upper()+"-"+card["cn"]
                            card["set"] = "plst"
                        sheet.append(card)
                sheets[sheet_file] = sheet
        return sheets
                    
    @staticmethod
    def get_collection():
        sheets = sheets_util.get_sheets()

        collection = dict()
        for sheet_name,sheet in sheets.items():
            for card in sheet:
                if (card["set"],card["cn"],card["lang"],card["foil"]) in collection:
                    collection[(card["set"],card["cn"],card["lang"],card["foil"])]["count"] += card["count"]
                else:
                    collection[(card["set"],card["cn"],card["lang"],card["foil"])] = card
                if card["lang"] != "en":
                    if (card["set"],card["cn"],"en",card["foil"]) not in collection:
                        extra_card = card.copy() 
                        extra_card["lang"] = "en"
                        extra_card["extra"] = True
                        extra_card["count"] = 0
                        collection[(extra_card["set"],extra_card["cn"],extra_card["lang"],extra_card["foil"])] = extra_card
                    else:#assign the extra tag even if we have an english copy, as we want to speed up lookup later
                        collection[(card["set"],card["cn"],"en",card["foil"])]["extra"] = True

        allcards = allcards_util.filtered_get(lambda x: (x["set"],x["collector_number"],x["lang"],True) in collection or (x["set"],x["collector_number"],x["lang"],False) in collection)
        
        sf_collection = list()
        for key in allcards.keys():
            card = allcards[key]
            #if has foil
            if (key[0],key[1],key[2],True) in collection:
                collection_card = collection.pop((key[0],key[1],key[2],True))
                card["MTGD_foil_count"] = collection_card["count"]
                if "extra" in collection_card:
                    card["MTGD_extra"] = True
            else:
                card["MTGD_foil_count"] = 0
            #if non-foil
            if (key[0],key[1],key[2],False) in collection:
                collection_card = collection.pop((key[0],key[1],key[2],False))
                card["MTGD_nonfoil_count"] = collection_card["count"]
                if "extra" in collection_card:
                    card["MTGD_extra"] = True
            else:
                card["MTGD_nonfoil_count"] = 0
            sf_collection.append(card)

        for key in collection.keys():
            if collection[key]["count"] != 0:
                print("ERROR:Scryfall missing ",(key[0],key[1],key[2]))

        return sf_collection
            

    '''
    Scryfall doesn't use 1:1 language codes with MTG, converts the codes typically found on cards to scryfall usable ones
    '''
    @staticmethod
    def get_scryfall_lang(card_lang):
        possible_langs = {"CS","CT","KR","JP","IT","DE","RU","FR","EN","ES","PT","PH"}
        if card_lang not in possible_langs:
            print("ERROR:Invalid Language:[",card_lang,"]")
        card_lang = card_lang.lower()
        match card_lang:
            case "cs":
                return "zhs"
            case "ct":
                return "zht"
            case "kr":
                return "ko"
            case "jp":
                return "ja"
            case "sp":
                return "es"
            case _:
                return card_lang

    @staticmethod
    def get_wotc_lang(card_lang):
        match card_lang:
            case "zhs":
                return "CS"
            case "zht":
                return "CT"
            case "ko":
                return "KR"
            case "ja":
                return "JP"
            case "es":
                return "SP"
            case _:
                return card_lang.upper() 

    @staticmethod
    def create_result_sheet(results):
        with open("result_sheet.csv","w",encoding='utf-8') as f:
            f.write("Count,Name,Price,Set,CN,Foil,Lang,CMC\n")
            for card in results:
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



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
            print("ERROR: no sheets directory")
            sys.exit(0)
        sheet_files = list(map(lambda x: "sheets/" + x,os.listdir("sheets")))
        for sheet_file in sheet_files:
            if os.path.isfile(sheet_file) and sheet_file[-4:] == ".csv":
                print("Loading:",sheet_file)
                sheet = []
                with open(sheet_file) as f:
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


        allcards = allcards_util.filtered_get(lambda x: (x["set"],x["collector_number"],x["lang"],True) in collection or (x["set"],x["collector_number"],x["lang"],False) in collection )
       
        sf_collection = list()
        for key in allcards.keys():
            card = allcards[key]
            #if has foil
            if (key[0],key[1],key[2],True) in collection:
                collection_card = collection.pop((key[0],key[1],key[2],True))
                card["MTGD_foil_count"] = collection_card["count"]
            else:
                card["MTGD_foil_count"] = 0
            #if non-foil
            if (key[0],key[1],key[2],False) in collection:
                collection_card = collection.pop((key[0],key[1],key[2],False))
                card["MTGD_nonfoil_count"] = collection_card["count"]
            else:
                card["MTGD_nonfoil_count"] = 0
            sf_collection.append(card)

        for key in collection.keys():
            print("SCRYFALL MISSING:",(key[0],key[1],key[2]))

        return sf_collection
            

    '''
    Scryfall doesn't use 1:1 language codes with MTG, converts the codes typically found on cards to scryfall usable ones
    '''
    @staticmethod
    def get_scryfall_lang(card_lang):
        possible_langs = {"CS","CT","KR","JP","IT","DE","RU","FR","EN","ES","PT","PH"}
        if card_lang not in possible_langs:
            print("Invalid Language:[",card_lang,"]")
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
            case _:
                return card_lang

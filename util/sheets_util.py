import sys
import requests
import json
import os
import time
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
                        card["proxy"] = False if card_split[7] == "" else True
                        card["commander"] = False if card_split[8] == "" else True
                        card["category"] = card_split[9]
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
    def create_inverse_result_sheet(results):
        with open("result_sheet.csv","w",encoding='utf-8') as f:
            f.write("Count,Name,Price,Set,CN,Foil,Lang,CMC,ILINK\n")
            for card in results:
                line = ""
                #count
                line += "0,"
                #name
                line += card["name"].replace(",","")+","
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
                line += str(card["cmc"]) + ","
                #Image Link
                #multifaced card
                if "image_uris" not in card.keys() and "card_faces" in card.keys():
                    if len(card["card_faces"]) > 2:
                        print("\nERROR:Found a card with more than 2 faces, I dont even....\n")
                    else:
                        #write front normally, put back on it's own line just for simplicity of my code
                        line += str(card["card_faces"][0]["image_uris"]["png"]) + "\n"
                        #write the second one on it's own line
                        line += ",,,"+card["set"]+","+card["collector_number"]+",,"+card["lang"]+"back,,"+card["card_faces"][1]["image_uris"]["png"]+"\n" 
                #only one face
                else:
                    line += str(card["image_uris"]["png"]) + "\n"
                f.write(line)

    @staticmethod
    def get_inverse_sheet_images():
        if not os.path.isdir('data'):
            os.mkdir('data')
        if not os.path.exists("data/images"):
            os.mkdir("data/images")
        to_download = []
        with open("result_sheet.csv",encoding='utf-8') as f:
            lines = f.read().split("\n")
            len_cards = str(len(lines) - 2)
            digits_len_cards = len(len_cards)
            counter = 0
            if lines[0].split(',')[-1] != "ILINK":
                print("\nERROR: You probably didn't generate this result_sheet using the -id flag, use -downloadimages instead")
                return
            for line in lines[1:-1]:
                counter += 1
                print("Downloading",str(counter).zfill(digits_len_cards)+"/"+len_cards,end='\r')
                split_line = line.split(",")
                if not os.path.exists("data/images/"+split_line[3]):
                    os.mkdir("data/images/"+split_line[3])
                if not os.path.exists("data/images/"+split_line[3]+"/"+split_line[4]+"_"+split_line[6]+".png"):
                    with open("data/images/"+split_line[3]+"/"+split_line[4]+"_"+split_line[6]+".png", "wb") as bf: 
                        bf.write(requests.get(",".join(split_line[8:])).content)   
                        time.sleep(0.2)
            print()

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

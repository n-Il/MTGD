"""
    Module provides utility functions for sheets
"""
import sys
import requests
import json
import os
import time
import util.card_util as card_util
import util.scryfall_util as scryfall_util


def parse_sheet_card(line):
    """Takes a line from a sheet and parses the fields into a dictionary"""
    card = dict()
    card_split = line.strip().split(',')
    card["count"] = 1 if card_split[0] == "" else int(card_split[0])
    card["set"] = card_split[1].lower()
    card["cn"] = card_split[2]
    card["name"] = card_split[3]#almost always empty
    card["foil"] = False if card_split[4] == "" else True
    card["list"] = False if card_split[5] == "" else True
    card["lang"] = "en" if card_split[6] == "" else card_util.get_scryfall_lang(card_split[6]) 
    card["proxy"] = False if card_split[7] == "" else True
    if len(card_split) > 8:
        card["commander"] = False if card_split[8] == "" else True
    if len(card_split) > 9:
        card["category"] = card_split[9]
    if card["list"]:
        card["cn"] = card["set"].upper()+"-"+card["cn"]
        card["set"] = "plst"
    return card

def get_sheets():
    """Loads the cards from sheet files into memory"""
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
                    card = parse_sheet_card(line)
                    sheet.append(card)
            sheets[sheet_file] = sheet
    return sheets
                
def get_collection():
    """Loads the collection from sheet files and all card data"""
    sheets = get_sheets()
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

    allcards = scryfall_util.filtered_load_all_cards(lambda x: (x["set"],x["collector_number"],x["lang"],True) in collection or (x["set"],x["collector_number"],x["lang"],False) in collection)
    
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
        

def create_inverse_result_sheet(results):
    """Creates a result sheet from a query against cards NOT in our collection. This requires making the image link available"""
    if not os.path.isdir('data'):
        os.mkdir('data')
    if not os.path.isdir('data/output'):
        os.mkdir('data/output')
    with open("data/output/result_sheet.csv","w",encoding='utf-8') as f:
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

def get_inverse_sheet_images():
    """Loads a invert result sheet, reads the image locations, and downloads them"""
    if not os.path.isdir('data'):
        os.mkdir('data')
    if not os.path.exists("data/images"):
        os.mkdir("data/images")
    to_download = []
    if not os.path.isdir('data/output'):
        os.mkdir('data/output')
    with open("data/output/result_sheet.csv",encoding='utf-8') as f:
        lines = f.read().split("\n")
        len_cards = str(len(lines) - 2)
        digits_len_cards = len(len_cards)
        counter = 0
        if lines[0].split(',')[-1] != "ILINK":
            print("\nERROR: You probably didn't generate this result_sheet using the -iq flag, use -downloadimages instead")
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

def create_result_sheet(results):
    """Creates a result sheet from a query of cards within our collection"""
    if not os.path.isdir('data'):
        os.mkdir('data')
    if not os.path.isdir('data/output'):
        os.mkdir('data/output')
    with open("data/output/result_sheet.csv","w",encoding='utf-8') as f:
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

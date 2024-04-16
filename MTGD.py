import time
import sys
import requests
import json
import os
from util.allcards_util import allcards_util
from util.sheets_util import sheets_util
from util.archidekt_util import archidekt_util 
from util.combos_util import combos_util
from util.mycollection import mycollection
from util.myquery import myquery

def card_lookup_cli():
    print("Loading all cards into memory... This may take a while")
    #actuallyallcards = allcards_util.filtered_get(lambda x: True)
    actuallyallcards = allcards_util.filtered_get(lambda x: x["lang"] == "en")
    x = None
    while True:
        x = input("Enter set and number:")
        if x == "exit":
            break
        if (x.split()[0],x.split()[1],"en") in actuallyallcards:
            card = actuallyallcards[(x.split()[0],x.split()[1],"en")]
            print(card["name"])
        else:
            print("set:{} cn:{} not found".format(x.split()[0],x.split()[1]))


def main():
    collection = mycollection()

    if '-download' in sys.argv:
        allcards_util.download()
        sys.exit(0)

    elif '-downloadimages' in sys.argv:
        collection.load_from_file()
        collection.get_images()

    elif '-downloadcombos' in sys.argv:
        combos_util.download()

    elif '-lookup' in sys.argv:
        card_lookup_cli()

    elif '-collect' in sys.argv:
        if os.path.exists("mycollection.json"):
            print("ERROR:collection file exists")
        else:
            collection = sheets_util.get_collection()
            with open("mycollection.json",'w') as f:
                f.write("[\n")
                i = 1
                total = len(collection) 
                for card in collection: 
                    if i == total:
                        f.write(json.dumps(card)+"\n")
                    else:
                        f.write(json.dumps(card)+",\n")
                        i += 1
                f.write("]")

    elif '-load' in sys.argv:
        collection.load_from_file()
        print("\n******************************************")
        print("Unique Cards in Collection: "+str(len(collection.cards)))
        print("Total Cards in Collection: "+str(collection.count_cards()))
        
        #price
        print("\n******************************************")
        collection.price_info()
        
        #foils vs nonfoils
        print("\n******************************************")
        collection.foil_info()
        
        #sets sorted
        print("\n******************************************")
        collection.set_info()

        #rarities
        print("\n******************************************")
        collection.rarity_info()

        #top cards by count
        print("\n******************************************")
        collection.topcards_info()

    elif '-compile' in sys.argv:
        collection.load_from_file()
        collection.spit_out_sheet()

    elif '-showcreate' in sys.argv:
        collection.load_from_file()
        collection.spit_out_create()

    elif '-q' in sys.argv:
        i = sys.argv.index('-q')
        if len(sys.argv) < (i+2):
            print("ERROR:EMPTY QUERY")
        else:
            q = " ".join(sys.argv[i+1:])
            print("Your Query:["+q+"]")
            collection.load_from_file()
            query = myquery(collection,q)
            del collection#try and allow python to free some memory
            result = query.result_cards
            sheets_util.create_result_sheet(result)
    
    elif '-combos' in sys.argv:
        collection.load_from_file()
        #combos is a dict wiht keys tuple of required cards and combo json value
        combos = collection.get_combos()
        print("Combos in Collection:",len(combos))
        #print more data
        combos_util.pp(combos)
    
    #query combo includes
    elif '-qci' in sys.argv:
        i = sys.argv.index('-qci')
        if len(sys.argv) < (i+2):
            print("ERROR:EMPTY QUERY")
        else:
            q = " ".join(sys.argv[i+1:])
            print("Your Query:["+q+"]")
            collection.load_from_file()
            combos = collection.get_combos()#dict of k,v is reqcards,combojson
            query = myquery(collection,q)
            del collection#try and allow python to free some memory
            results = query.result_cards#list of scryfall card objects
            set_results = set()
            #convert scryfall card objects to set of names
            if len(results) > 100:
                print("qci is intended for checking which combos include a single card from your collection, there are",len(result_cards),"cards you are checking")
            elif len(results) < 1:
                print("No results to query")
                return
            else:
                print("Results to query:",len(results))
            for card in results:
                set_results.add(card["name"])
            #filter combos
            for reqs in list(combos.keys()):
                #if any of the cards in reqs
                if sum(map(lambda x: x in reqs,set_results)) > 0:
                    pass
                    #print("has combo")
                else:
                    combos.pop(reqs)
            #print combos
            print("Combos including the queried card(s):",len(combos))
            combos_util.pp(combos)

    #query combo within
    elif '-qcw' in sys.argv:
        i = sys.argv.index('-qcw')
        if len(sys.argv) < (i+2):
            print("ERROR:EMPTY QUERY")
        else:
            q = " ".join(sys.argv[i+1:])
            print("Your Query:["+q+"]")
            collection.load_from_file()
            combos = collection.get_combos()#dict of k,v is reqcards,combojson
            query = myquery(collection,q)
            del collection#try and allow python to free some memory
            results = query.result_cards#list of scryfall card objects
            set_results = set()
            #convert scryfall card objects to set of names
            if len(results) < 1:
                print("No results to query")
                return
            else:
                print("Results to query:",len(results))
            for card in results:
                set_results.add(card["name"])
            #filter combos
            for reqs in list(combos.keys()):
                #if any of the cards in reqs
                if sum(map(lambda x: x in set_results,reqs)) == len(reqs):
                    pass
                    #print("has combo")
                else:
                    combos.pop(reqs)
            #print combos
            print("Combos including the queried card(s):",len(combos))
            combos_util.pp(combos)

    
    
    elif '-findcommanderdecks' in sys.argv:
        print("WARNING: THIS WILL TAKE A LONG TIME")
        print("Loading Collection")
        collection.load_from_file()
        print("Getting Commanders")
        query = myquery(collection,"is:commander -is:digital")
        del collection
        results = query.result_cards
        card_names = set()
        for card in results:
            card_names.add(card["name"])
        digits = len(str(len(card_names)))
        counter = 0
        for card_name in card_names:
            counter += 1
            print("\n"+str(counter).zfill(digits)+"/"+str(len(card_names))+" Commander:",card_name)       
            ids = archidekt_util.get_x_ids(card_name,50)
            archidekt_util.download_decks(ids)
        del results

    elif '-testcommanderdecks' in sys.argv:
        deck_link = "https://archidekt.com/decks/{}"
        collection.load_from_file()
        my_card_names = collection.get_names_and_counts()
        del collection
        with open("commander_decks.csv","w+") as f:
            f.write("Commander,Link,%InCollection,%NonLandsInCollection,PriceMissing,PriceMissingNonLands\n")
            list_of_deck_files = list(map(lambda x: "data/archidekt/" + x,os.listdir("data/archidekt")))
            for deck_file in list_of_deck_files:
                with open(deck_file) as f2:
                    deck = json.load(f2)                   
                    lands_cards_have = 0
                    nonland_cards_have = 0
                    total_nonlands = 0
                    price_missing_lands = 0.0
                    price_missing_nonlands = 0.0
                    in_deck_categories = set()
                    total_cards = 0#TODO DEBUGGING
                    for cat in deck["categories"]:
                        if cat["includedInDeck"]:
                            in_deck_categories.add(cat["name"])
                    for card in deck["cards"]:
                        #check if in deck(versus maybeboard)
                        if len(card["categories"]) == 0 or card["categories"][0] in in_deck_categories:#TODO make sure this works, empty categories appears to be assumed part of the deck
                            total_cards += card["quantity"] #TODO DEBUGGING
                            #check if we have this card(s)
                            if card["card"]["oracleCard"]["name"] in my_card_names.keys():
                                #check if we have the right number of them
                                if card["quantity"] <= my_card_names[card["card"]["oracleCard"]["name"]]:
                                    #check if land
                                    if "Land" in card["card"]["oracleCard"]["types"]:
                                        lands_cards_have += card["quantity"]
                                    else:
                                        nonland_cards_have += card["quantity"]
                                        total_nonlands += card["quantity"]
                                #we dont have some of them
                                else:
                                    #check if land
                                    if "Land" in card["card"]["oracleCard"]["types"]:
                                        lands_cards_have += my_card_names[card["card"]["oracleCard"]["name"]] 
                                        price_missing_lands += card["card"]["prices"]["tcg"] * (card["quantity"] - my_card_names[card["card"]["oracleCard"]["name"]])
                                    else:
                                        nonland_cards_have += my_card_names[card["card"]["oracleCard"]["name"]] 
                                        price_missing_nonlands += card["card"]["prices"]["tcg"] * (card["quantity"] - my_card_names[card["card"]["oracleCard"]["name"]])
                                        total_nonlands += card["quantity"]
                            #we dont have any
                            else:
                                if "Land" in card["card"]["oracleCard"]["types"]:
                                    price_missing_lands += card["card"]["prices"]["tcg"] * card["quantity"]
                                else:
                                    price_missing_nonlands += card["card"]["prices"]["tcg"] * card["quantity"]
                    #build the csv entry
                    commander_name = archidekt_util.get_commander(deck)
                    link = deck_link.format(deck["id"])
                    percent_in_collection = (lands_cards_have + nonland_cards_have) /  100.0
                    nonland_percent_in_collection = float(nonland_cards_have) / float(total_nonlands)
                    price_missing_total = price_missing_lands + price_missing_nonlands
                    csv = "\""+commander_name+"\","+link+","+str(percent_in_collection)+","+str(nonland_percent_in_collection)+","+str(price_missing_total)+","+str(price_missing_nonlands)+"\n"
                    f.write(csv)
                    if total_cards != 100:
                        #TODO looks like the sideboard may be causing
                        #TODO also is issue of prices for nonland cards not adding up , should be 0 for price nonland when nonland percent is 1
                        print("ERROR:getting wrong number of cards(code mistake somewhere)")
                        debug_total = 0
                        for debug_card in deck["cards"]:
                            debug_total += debug_card["quantity"]
                        print(debug_total)
                        print(link)

    elif '-help' in sys.argv:
        print("\tInput your collection using this spreadsheet:")
        print("\thttps://docs.google.com/spreadsheets/d/1d5eBMMFTuUER844bV1ShyKUCC8U0s6GVq10g9oklSmE/edit?usp=sharing")
        print("\tDownload the Sheet(s) as a CSV and put them in a folder called \"sheets\".")
        print("")
        print("\t[-lookup] lets you test set/cn combinations against scryfall's english entries.(unoptimized).")
        print("\t[-download] downloads the latest scryfall data(~2GB) to your computer.")
        print("\t[-downloadimages] downloads the card images for cards in your collection to your computer.")
        print("\t[-downloadcombos] downloads a combo database from commander spellbook to your computer")
        print("\t[-collect] converts the sheets you created to a local collection file with scryfall data.")
        print("\t[-compile] converts the local collection file into a spreadsheet with card names among other fields.")
        print("\t[-load] loads your collection into memory and provides some simple stats.")
        print("\t[-showcreate] loads your collection into memory and creates a spreadsheet that can be used to create it")
        print("\t[-q] loads your collection into memory, runs the query following -q, and creates result_sheet.csv with the overlapping cards.")
        print("\t[-combos] loads your collection into memory, loads the combo database into memory, then outputs a description and required cards for each combo.")
        print("\t[-qci] Requires a Query. Use this option for finding combos within your collection which include a specific card found by the query.")
        print("\t[-qci] Requires a Query. Use this option to find combos where all cards are contained within a subset of your collection(which is filtered by the query).")
        print("\t[-findcommanderdecks] WARNING_SLOW Download the 50 most recently created decks for each commander card in your collection"
        print("\t[-testcommanderdecks] Using the stored decks, generates a commander_decks.csv file which can be used to find contained or mostly contained decks."
    
    else:
        print("no arguments found, try '-help'")

    
if __name__ == "__main__":
    start_time = time.time()
    main()
    print("[Elapsed Seconds:{elapsed_seconds:0.2f}]".format(elapsed_seconds = (time.time() - start_time)))


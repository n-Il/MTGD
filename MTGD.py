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

def download():
    allcards_util.download()
    #sys.exit(0) speeds up cleanup but probably not great practice
    
def downloadimages():
    collection = mycollection()
    if collection.load_from_file():
        collection.get_images()

def collect():
    collection = mycollection()
    if os.path.exists("mycollection.json"):
        print("ERROR:collection file exists")
    else:
        collection = sheets_util.get_collection()
        with open("mycollection.json",'w',encoding='utf-8') as f:
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
def load():
    collection = mycollection()
    if collection.load_from_file():
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

def dash_compile():
    collection = mycollection()
    if collection.load_from_file():
        collection.spit_out_sheet()

def showcreate():
    collection = mycollection()
    if collection.load_from_file():
        collection.spit_out_create()

def q():
    collection = mycollection()
    i = sys.argv.index('-q')
    if len(sys.argv) < (i+2):
        print("ERROR:EMPTY QUERY")
    else:
        q = " ".join(sys.argv[i+1:])
        print("Your Query:["+q+"]")
        if collection.load_from_file():
            query = myquery(collection,q)
            del collection#try and allow python to free some memory
            result = query.result_cards
            if len(result) == 0:
                print("ERROR: No Cards Found")
                return
            if len(result) < 25:
                for card in result:
                    print((card["MTGD_foil_count"]+card["MTGD_nonfoil_count"]),card["name"])
            sheets_util.create_result_sheet(result)
            #create results.js
            with open("results.js","w+") as f:
                f.write("var results = [\n")
                for card in result:
                    if card["MTGD_foil_count"] > 0 or card["MTGD_nonfoil_count"] > 0:
                        image_src = "data/images/"+str(card["set"])+"/"+str(card["collector_number"])+"_"+card["lang"]+".png"
                        f.write("[\""+image_src+"\""+",\""+card["scryfall_uri"]+"\"],\n")
                f.write("];\n")
 

def combos():
    collection = mycollection()
    if collection.load_from_file():
        #combos is a dict wiht keys tuple of required cards and combo json value
        combos = collection.get_combos()
        if combos:
            print("Combos in Collection:",len(combos))
            #print more data
            combos_util.pp(combos)

def comboforcegraph():
    collection = mycollection()
    if collection.load_from_file():
        combos = collection.get_combos()
        if combos:
            combos_util.force_graph2(combos)

def allcombosforcegraph():
    combos = combos_util.get()
    if combos:
        combos_util.force_graph2(combos)

def querycombosincludes():
    collection = mycollection()
    i = sys.argv.index('-qci')
    if len(sys.argv) < (i+2):
        print("ERROR:EMPTY QUERY")
    else:
        q = " ".join(sys.argv[i+1:])
        print("Your Query:["+q+"]")
        if collection.load_from_file():
            combos = collection.get_combos()#dict of k,v is reqcards,combojson
            query = myquery(collection,q)
            del collection#try and allow python to free some memory
            results = query.result_cards#list of scryfall card objects
            if len(results) == 0:
                print("ERROR: No Cards Found")
                return
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

def querycomboswithin():
    collection = mycollection()
    i = sys.argv.index('-qcw')
    if len(sys.argv) < (i+2):
        print("ERROR:EMPTY QUERY")
    else:
        q = " ".join(sys.argv[i+1:])
        print("Your Query:["+q+"]")
        if collection.load_from_file():
            combos = collection.get_combos()#dict of k,v is reqcards,combojson
            query = myquery(collection,q)
            del collection#try and allow python to free some memory
            results = query.result_cards#list of scryfall card objects
            if len(results) == 0:
                print("ERROR: No Cards Found")
                return
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
            print("Combos within the queried card(s):",len(combos))
            combos_util.pp(combos)

def findcommanderdecks():
    #if we enter a commander, limit to that commander
    i = sys.argv.index('-findcommanderdecks')
    filter_commander = " ".join(sys.argv[i+1:])           
    if len(filter_commander) > 0:
        print("You entered a commander, Searching decks helmed by:",filter_commander)
        print("WARNING: THIS WILL TAKE A LONG TIME")
        ids = archidekt_util.get_x_ids(filter_commander,999999)#lazy hack but prevents code duplication
        archidekt_util.download_decks(ids)
    else:
        collection = mycollection()
        print("WARNING: THIS WILL TAKE A LONG TIME")
        print("Loading Collection")
        if collection.load_from_file():
            print("Getting Commanders")
            query = myquery(collection,"is:commander -is:digital")
            del collection
            results = query.result_cards
            card_names = set()
            for card in results:
                card_names.add(card["name"])
            if len(card_names) == 0:
                print("ERROR: No Commanders found in collection")
            else:
                digits = len(str(len(card_names)))
                counter = 0
                for card_name in card_names:
                    counter += 1
                    print("\n"+str(counter).zfill(digits)+"/"+str(len(card_names))+" Commander:",card_name)       
                    ids = archidekt_util.get_x_ids(card_name,50)
                    archidekt_util.download_decks(ids)
                del results


def testcommanderdecks_helper(deck,my_cards):
    missing_lands = 0
    missing_nonlands = 0
    price_missing_lands = 0 
    price_missing_nonlands = 0
    in_deck_categories = set()
    for cat in deck["categories"]:
        if cat["includedInDeck"] and (cat["name"]!="Sideboard"):
            in_deck_categories.add(cat["name"])
    for card in deck["cards"]:
        #check if in deck(versus maybeboard)
        if len(card["categories"]) == 0 or card["categories"][0] in in_deck_categories:
            in_collection = my_cards[card["card"]["oracleCard"]["name"]] if card["card"]["oracleCard"]["name"] in my_cards else 0
            have = min(card["quantity"],in_collection)
            have_not = card["quantity"] - have
            if "Land" in card["card"]["oracleCard"]["types"]:
                missing_lands += have_not
                price_missing_lands += (have_not * card["card"]["prices"]["tcg"])
            else:
                missing_nonlands += have_not
                price_missing_nonlands += (have_not * card["card"]["prices"]["tcg"])
    #build the csv entry
    commander_name = deck["MTGD_Meta"]["MTGD_Commander"]
    link = "https://archidekt.com/decks/{}".format(deck["id"])
    csv = "\""+commander_name+"\",\""+link+"\","+str((missing_lands+missing_nonlands))+","+str(missing_lands)+","+str(missing_nonlands)+",$"+str((price_missing_lands+price_missing_nonlands))+",$"+str(price_missing_lands)+",$"+str(price_missing_nonlands)+"\n"
    return csv

def testcommanderdecks():
    #if we enter a commander, limit to that commander
    i = sys.argv.index('-testcommanderdecks')
    filter_commander = " ".join(sys.argv[i+1:])           
    if len(filter_commander) > 0:
        print("You entered a commander, Filtering decks helmed by:",filter_commander)

    if not os.path.isdir('data'):
        print("ERROR: missing data folder")
    elif not os.path.isdir('data/archidekt/'):
        print("ERROR: missing data/archidekt folder.(Run -findcommanderdecks)")
    elif len(os.listdir("data/archidekt")) == 0:
        print("ERROR: no decks in data/archidekt, Do you have no viable commanders in your collection?")
    else:
        list_of_files = list(map(lambda x: "data/combos/" + x,os.listdir("data/combos"))) 
        collection = mycollection()
        if collection.load_from_file():
            my_cards = collection.get_names_and_counts()
            del collection
            with open("commander_decks.csv","w+",encoding='utf-8') as f:
                f.write("Commander,Link,Missing,MissingLands,MissingNonLands,PriceMissingCards,PriceMissingLands,PriceMissingNonLands\n")
                list_of_deck_files = list(map(lambda x: "data/archidekt/" + x,os.listdir("data/archidekt")))
                for deck_file in list_of_deck_files:
                    with open(deck_file,encoding='utf-8') as f2:
                        deck = json.load(f2)                   
                        if len(filter_commander) > 0:
                            if deck["MTGD_Meta"]["MTGD_Commander"] != filter_commander:
                                continue#skip the current deck
                        f.write(testcommanderdecks_helper(deck,my_cards))
                        
def help_text():
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
    print("\t[-qcw] Requires a Query. Use this option to find combos where all cards are contained within a subset of your collection(which is filtered by the query).")
    print("\t[-comboforcegraph] Generates a 3d force graph with the combos from your collection. Creates 3d_force_graph_combos.html. The file equires ./util/3d-force-graph/3d-force-graph.js")
    print("\t[-findcommanderdecks] WARNING_SLOW Download the 50 most recently created decks for each commander card in your collection.Follow this with a commander card name to search for all decks with a specific commander.")
    print("\t[-testcommanderdecks] Using the stored decks, generates a commander_decks.csv file which can be used to find contained or mostly contained decks.Follow this with a commander card name to only test decks with a specific commander.")

def main():
    if '-download' in sys.argv:
        download()
    elif '-downloadimages' in sys.argv:
        downloadimages()
    elif '-downloadcombos' in sys.argv:
        combos_util.download()
    elif '-lookup' in sys.argv:
        card_lookup_cli()
    elif '-collect' in sys.argv:
        collect()
    elif '-load' in sys.argv:
        load()
    elif '-compile' in sys.argv:
        dash_compile()
    elif '-showcreate' in sys.argv:
        showcreate()
    elif '-q' in sys.argv:
        q()
    elif '-combos' in sys.argv:
        combos()
    elif '-comboforcegraph' in sys.argv:
        comboforcegraph()
    elif '-allcombosforcegraph' in sys.argv:
        allcombosforcegraph()
    elif '-qci' in sys.argv:
        querycombosincludes()
    elif '-qcw' in sys.argv:
        querycomboswithin()
    elif '-findcommanderdecks' in sys.argv:
        findcommanderdecks()
    elif '-testcommanderdecks' in sys.argv:
        testcommanderdecks()
    elif '-help' in sys.argv:
        help_text()
    else:
        print("no arguments found, try '-help'")
    
if __name__ == "__main__":
    start_time = time.time()
    main()
    print("[Elapsed Seconds:{elapsed_seconds:0.2f}]".format(elapsed_seconds = (time.time() - start_time)))


import time
import sys
import requests
import json
import os
from util.allcards_util import allcards_util
from util.sheets_util import sheets_util
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

    elif '-help' in sys.argv:
        print("\tInput your collection using this spreadsheet:")
        print("\thttps://docs.google.com/spreadsheets/d/1d5eBMMFTuUER844bV1ShyKUCC8U0s6GVq10g9oklSmE/edit?usp=sharing")
        print("\tDownload the Sheet(s) as a CSV and put them in a folder called \"sheets\"")
        print("")
        print("\t[-lookup] lets you test set/cn combinations against scryfall's english entries.(unoptimized)")
        print("\t[-download] downloads the latest scryfall data(~2GB) to your computer")
        print("\t[-downloadimages] downloads the card images for cards in your collection to your computer.")
        print("\t[-collect] converts the sheets you created to a local collection file with scryfall data")
        print("\t[-compile] converts the local collection file into a spreadsheet with card names among other fields")
        print("\t[-load] loads your collection into memory and provides some simple stats")
        print("\t[-showcreate] loads your collection into memory and creates a spreadsheet that can be used to create it")


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
    
    #if '-what' in sys.argv:
    #    collection.load_from_file()
    #    first = collection.cards[0]
    #    for key in first.keys():
    #        print("key:",key,"\nValue:",first[key],"\n")

    #if '-testlinks' in sys.argv:
    #    collection.load_from_file()
    #    first = collection.cards[0]
    #    for key in first["image_uris"]:
    #        print("key:",key,"\nValue:",first["image_uris"][key],"\n")
            
if __name__ == "__main__":
    start_time = time.time()
    main()
    print("[Elapsed Seconds:{elapsed_seconds:0.2f}]".format(elapsed_seconds = (time.time() - start_time)))


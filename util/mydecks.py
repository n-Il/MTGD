class mydecks:
    '''
    Scryfall doesn't use 1:1 language codes with MTG, converts the codes typically found on cards to scryfall usable ones
    '''
    def get_scryfall_lang(self,card_lang):
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

    def get_wotc_lang(self,card_lang):
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

    #function to read in the deck sheets
    def get_decks(self):
        decks = dict()
        if not os.path.isdir('decks'):
            print("ERROR:No decks directory")
            sys.exit(0)
        deck_files = list(map(lambda x: "decks/" + x,os.listdir("decks")))
        for deck_file in deck_files:
            if os.path.isfile(deck_file) and deck_file[-4:] == ".csv":
                deck = []
                with open(deck_file,encoding='utf-8') as f:
                    for line in f.readlines()[1:]:
                        card = dict()
                        card_split = line.strip().split(',')
                        card["count"] = 1 if card_split[0] == "" else int(card_split[0])
                        card["set"] = card_split[1].lower()
                        card["cn"] = card_split[2]
                        card["name"] = card_split[3]#almost always empty
                        card["foil"] = False if card_split[4] == "" else True
                        card["list"] = False if card_split[5] == "" else True
                        card["lang"] = "en" if card_split[6] == "" else self.get_scryfall_lang(card_split[6]) 
                        card["proxy"] = False if card_split[7] == "" else True
                        card["commander"] = False if card_split[8] == "" else True
                        card["category"] = card_split[9]
                        if card["list"]:
                            card["cn"] = card["set"].upper()+"-"+card["cn"]
                            card["set"] = "plst"
                        deck.append(card)
                decks[deck_file] = deck 
        return decks

    #TODO pick up here
    #This function is going to convert the deck lists to dictionaries and then add scryfall data for each card.
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
    #function to grab scryfall data 
    #function to write the deck data to data/decks
    #function to take deck data in data/decks and then write out the sheets
    #functions to do stats on the decks
    #function that checks legality of the decks
    #function to check that all cards in the decks are within our collection
    #function to output decks as archidekt import data

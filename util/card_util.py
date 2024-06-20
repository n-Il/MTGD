"""
    This module provides card utilities
"""
def get_scryfall_lang(card_lang):
    """Scryfall doesn't use 1:1 language codes with MTG, converts the codes typically found on cards to scryfall usable ones"""
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

def get_wotc_lang(card_lang):
    """converts scryfall languages to the language codes on cards."""
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

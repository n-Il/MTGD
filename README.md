# MTGD
MTGD is a collection managment software for Magic the Gathering.

MTGD is tested on both Windows and Linux and should be completely operational on both.

MTGD uses and greatly appreciates the Scryfall API.

MTGD uses and greatly appreciates the Commander Spellbook API. 

MTGD uses and greatly appreciates the Archidekt API.

### Python3 Requirements
requests
json

## How To: Use MTGD

### The Command Structure
- Run MTGD by typing 'python3 MTGD.py {flag}'. Flags can be found by using the '-help' flag.
- MTGD is currently a simple project, and such will only accept a single flag at a time. For Example 'python3 MTGD.py -download -downloadcombos' will only download the card data.
- MTGD may contain bugs with common CLI utilities like piping and redirection of output where these share symbols with the scryfall syntax. For Example 'python3 MTGD.py -q CMC>3'

### Create Spreadsheets for your cards 
Before using this tool, it's important to understand how card data is collected. It is collected by you! I have provided a template for making spreadsheets that the tool can read in.
The spreadsheets require the following fields to be filled out
- SET: The (typically) 3 letter set code at the bottom left of modern cards
- Collector Number: The (typically) 3 or 4 digit collector number at the bottom left of modern cards


ALL OTHER FIELDS HAVE DEFAULTS AND CAN BE EMPTY


- Use the language codes as listed on the card. This means use CS for simplified chinese rather than zhs
- Put a Yes in the Foil column if the card is foil. This currently does not handle foil etched and odd finish cards.
- Put a Yes in the "List" column if the card is considered from "The List". Input the non-list set and collector number from the corner of the card.
- You may duplicate entries rather than use counts, MTGD will handle adding those up when generating a collection.

### Struggling with Set and Collector Numbers? Promos?
- Some cards, mostly promos and double sided cards, have odd set and collector numbers.

- Using the scryfall website is the most sure-fire way to ensure you're using the correct data
    - If you navigate to the card you are unsure of, and look at the URL, the URL will contain the exact set code and collector number as seen in scryfall

- the MTGD '-lookup' flag will read in the entire card database and start a lookup input loop. Enter a set and card number sepperated by a space and it will look if there exists a ENGLISH card with those set and collector number.

### Downloading Card Data
- Run MTGD with the '-download' command flag. This will download the bulk data for all cards from the scryfall API.
- The Scryfall Bulk data is not updated hourly. Please do not generate unnecesary traffic and only download the data when you must.

### Downloading Card Image Data
- You must have a mycollection.json file
- This process may take a SIGNIFICANT amount of time to complete.
- Run MTGD with the '-downloadimages' command flag. This will download the card images of cards in your collection.
- I may find a more efficient method of implementing this that does not use scryfall in the future.
    - For now please try to limit how many images you query and how often in case this leads to significant strain on scryfall infrastructure.
        - These requests are throttled in code to abide by good citizen policy.

### Downloading Combo Data
- Run MTGD with the '-downloadcombos' command flag. This will download the bulk combo database from commanderspellbook.

### Convert your Sheets into a Collection
- Download your spreadsheets as Comma Sepperated Value(CSV) files and place them in the sheets directory.
- Run MTGD with the '-collect' flag, a mycollection.json file will be generated. Theis collection contains cards which are an extension of the scryfall data format. The specific card data includes a number of owned copies in foil and nonfoil.


## Do Something with your Collection File

### Load your collection
- Loading your collection is a good test before using any other features.
- Run MTGD with the '-load' flag. A bunch of information about your collection will be output to the console.

### Convert your collection file back into a spreadsheet
- You must have a mycollection.json file
- Run MTGD with the '-showcreate' flag, a show_create_sheet.csv file will be generated

### Compile your collection file to a human readable spreadsheet
- You must have a mycollection.json file
- Run MTGD with the '-compile' flag, a output_sheet.csv file will be generated
- This sheet does not follow the input requirements, but is more human readable.

### Run A Query on your collection
- You must have a mycollection.json file
- Use the '-q' flag followed by your query
- NOTE: This is realy inefficient if your query is a HUGE subset, for example 't:creature', I will write custom logic for queries that are simple in the future that will speed up this operation.
- NOTE: Queries which include special characters like '>' that redirect output are not currently handled

### Find out what combos are in your collection
- You must have a mycollection.json file 
- You must have downloaded the combo data using '-downloadcombos'
- Run MTGD with the '-combos' flag. You may want to redirect the output as it can be long. Ex. 'python3 MTGD.py -combos > mycombos.txt'

### Find Combos in a filtered version of your collection
- You must have a mycollection.json file 
- You must have downloaded the combo data using '-downloadcombos'
- Run MTGD with the '-qcw' flag followed by your query
- NOTE: This is realy inefficient if your query is a HUGE subset, for example 't:creature', I will write custom logic for queries that are simple in the future that will speed up this operation.
- NOTE: Queries which include special characters like '>' that redirect output are not currently handled
- You may want to redirect the output as it can be long. Ex. 'python3 MTGD.py -qcw id:colorless > mycombos.txt'

### Find Combos in your collection which includes some specific card
- You must have a mycollection.json file 
- You must have downloaded the combo data using '-downloadcombos'
- Run MTGD with the '-qci' flag followed by your query
- This is optimized for the query to be a very small set of cards, for ease of use when unsure of spelling for a card(or for using set and collector number)
- NOTE: Queries which include special characters like '>' that redirect output are not currently handled
- You may want to redirect the output as it can be long. Ex. 'python3 MTGD.py -qci Ashnod's Altar > mycombos.txt'

## Find EDH decks that you may be able to build
- You must have a mycollection.json file
- There are two arguments that are required for this. '-findcommanderdecks' and '-testcommanderdecks'
- '-findcommanderdecks' uses the scryfall API and your collection to figure out which commanders are in you collection
    - After these are determined, the Archidekt API is queried for the most recently created 50 decks for each commander and saving them to data/archidekt
    - THIS WILL TAKE AN EXTREME AMOUNT OF TIME. MULTIPLE HOURS. If your collection is large enough, this may take multiple days.
        - I am working on finding an alternative to some tooling used to accomplish this task so that this does not take as long, but for now it is necessary to minimize the density of traffic towards the archidekt API.
- '-testcommanderdecks' reads in the downloaded decks and calculates the percent of each deck that is contained within your collection.
    - A "commander_decks.csv" file is generated with this data and it is suggested that you put this into spreadsheet software to sort.

## Contact Us
At this point in the project, please feel free to open an issue on github for non-serious matters. The example sheet from the '-help' dialogue also includes an email you are welcome to use.

# MTGD(name not final)
MTGD is a collection managment software for Magic the Gathering.

MTGD is implemented on Linux, and at this time it's probably not functional on Windows.

MTGD uses and greatly appreciates the Scryfall API. 

The future of MTGD is to provide many popular filtering and lookup operations based only on cards you own in paper. 

### Python Requirements
requests
json

## How To: Use MTGD
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

### Convert your Sheets into a Collection
- Download your spreadsheets as Comma Sepperated Value(CSV) files and place them in the sheets directory.
- Run MTGD with the '-collect' flag, a mycollection.json file will be generated. Theis collection contains cards which are an extension of the scryfall data format. The specific card data includes a number of owned copies in foil and nonfoil.


### Do Something with your Collection File
- Run MTGD with the '-load' flag. This will generate some stats. 
- Run MTGD with the '-compile' flag. This will generate a more rich spreadsheet with the entire collection data.
- More features will come with time.

### Convert your collection back into a spreadsheet
- You must have a mycollection.json file
- Run MTGD with the '-showcreate' flag, a show_create_sheet.csv file will be generated

### Run A Query on your collection
- Use the '-q' flag followed by your query
- NOTE: This is realy inefficient if your query is a HUGE subset, for example 't:creature', I will write custom logic for queries that are simple in the future that will speed up this operation.
- NOTE: Queries which include special characters like '>' that redirect output are not currently handled

## Contact Us
At this point in the project, please feel free to open an issue on github for non-serious matters. The example sheet from the '-help' dialogue also includes an email you are welcome to use.

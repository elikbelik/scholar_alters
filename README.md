# scholar_alters
Parse unread emails from Google Scholar alerts and sort publication by relevance

# Workflow
 1. Parse unread emails labeled as Google Scholar
 2. Aggregate papers with the same name and remove papers that was seen on the previous run
 3. Sort the papers according to the number of different alerts it was found in
 4. Ask for each paper whether it is important (require user input)
 5. Open the important papers on a web browser
 6. Save the list of papers and the user input for one-day-i'll-use-some-learning-on-this-data porposes

# Setting for first use
You should need to use [Gmail API Client Library](https://developers.google.com/gmail/api/quickstart/python) and create
credentials.json as explained in the link.

Open connect_to_gmail.py from this repository and update the location of the cridentials in 'CLIENTSECRETS_LOCATION'.
Open parse_gmail_message.py from this repository and create a location for the saved data in 'DATA_FOLDER'
and the name of the label in Gmail which labels the google scholar alerts in 'PAPERS_LABEL'.
You may change the location of your web browser in 'BROWSER_COMMAND'.

# Run
Run from command line: parse_gmail_message.py

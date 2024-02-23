# Welcome to Scrapevine! 🔍🐍

Scrapevine - a simple Python-based web app that scrapes a list of websites for popular, highly recommended instances of a given "phrase".

## HOW TO USE
1) Load and open the Scrapevine web app in any modern web browser.
2) Enter a comma-separated list of websites for Scrapvine to scrape.
3) Enter a text phrase that Scrapevine should search for.
4) Specify the number of "match groups" (unique results) to display.
5) Click "Run"!

## TECH STACK

### Python libraries:
* BeautifulSoup - for webscraping.
* pandas - for sorting thru the scraped data & displaying the results.
* nltk, spaCy, PolyFuzz, TextBlob - for Natural Language Processing (NLP) capabilities.

NOTE: NLP is simply the processing & understanding the text using  methods such as "semantic similarity", "sentiment analysis". By leveraging NLP Python libraries, we can understand how people feel towards certain "instances"  "most popular" & "most recommended" instances of the user-specified "phrase" existing on the list of websites.

NOTE: Streamlit is used for running & interacting with the Python code via web app. For more info on Streamlit, see the developer docs here: https://docs.streamlit.io/
import streamlit as st
import streamlit_debug
from streamlit.logger import get_logger
import requests
from bs4 import BeautifulSoup
from polyfuzz import PolyFuzz
from textblob import TextBlob
from nltk import word_tokenize
from nltk.corpus import stopwords
stopwords_default = stopwords.words('english')
from spacy import load
#from spacy.lang.en import stop_words
import pandas as pd

# TODO: Use NLP libraries that are MUCH better suited for 'multi-word' phrase matching:
#
#       Standford's Stanza: https://stanfordnlp.github.io/stanza/mwt.html
#           GitHub: https://github.com/stanfordnlp/stanza
#
#       -OR-
#
#       Gensim: https://radimrehurek.com/gensim/auto_examples/core/run_similarity_queries.html
#           GitHub: https://github.com/piskvorky/gensim
#
#       -OR-
#
#       SpaCy's PhraseMatcher: https://spacy.io/usage/rule-based-matching#phrasematcher

#region Setup Debugging & Logger

# Enable Remote Debugging in VS Code
streamlit_debug.set(flag=True, wait_for_client=True, host='localhost', port=8765)

LOGGER = get_logger(__name__)

#endregion

#region Init Streamlit App

st.set_page_config(
        page_title="Scrapevine",
        page_icon="🔍",
    )

st.write("# Welcome to Scrapevine! 🔍🐍")

#endregion

#region Constants

# Test Data
SITE_TEST_DATA_INSPIRATIONAL = "https://quotes.toscrape.com/tag/inspirational/"
KEYWORD_MIRACLE = "miracle"

# Kemper Data
SITE_KEMPER_AMPS_MAIN_FORUM = "https://www.kemper-amps.com/forum/board/35-public-forum/"
KEYPHRASE_KEMPER_PROFILE = "kemper profile"
KEYPHRASE_AMP_MODEL = "amp model"
KEYWORD_PRESET = "preset"

# Text Input Fields

# (pre-populate with both test data site & official Kemper Amps forum)
SITES = st.text_input("Enter a list of websites to scrape, separated by commas:",
                      SITE_TEST_DATA_INSPIRATIONAL + ", " + SITE_KEMPER_AMPS_MAIN_FORUM)

# (pre-populate with test data word 'miracle' that should work)
PHRASE = st.text_input("Enter a phrase for Scrapevine to find (e.g. " +
                       "'{}', '{}', '{}'):".format(KEYPHRASE_KEMPER_PROFILE, KEYPHRASE_AMP_MODEL, KEYWORD_PRESET),
                       KEYWORD_MIRACLE)

TOP_NUMBER = st.number_input("Enter the max number of top ranked matches to display in the results:",
                             min_value=1, max_value=10, value=5)

# Constants for NLP
POLYFUZZ_SIMILARITY_THRESHOLD = 0.8 # Define a semantic similarity threshold for fuzzy text matching
CLUSTER_SIMILARITY_THRESHOLD = 0.9 # Define a cluster similarity threshold
SPACY_NLP = load('en_core_web_sm') # Load a pre-trained NLP model for semantic similarity
#SPACY_STOP_WORDS = stop_words.STOP_WORDS # Initialize the stop words for spaCy

#endregion

#region Functions

# TODO: Modify this function to actually 'explore' multiple pages of the website--this currently only scrapes
#       the initial page of each website specified (no further 'crawling' being done at the moment). Works fine
#       
def scrape_data(site):
    """Scrape the text data from a website"""
    response = requests.get(site)
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text().replace("\n", " ")
    return text

def fuzzy_match(data, phrase):
    """Find the fuzzy matches of a phrase in the data using PolyFuzz"""
    matches = []
    # TODO: Update tokenization here to identify 'multi-word' phrases, not just single words!
    tokens = word_tokenize(data)
    # Ignore punctuation or 'stop words' (common words like 'a', 'the', etc)
    clean_text = [token.lower() for token in tokens if token.isalpha() and token not in stopwords_default]
    pf = PolyFuzz("EditDistance")
    pf.match(clean_text, [phrase.lower()])
    df = pf.get_matches()
    df = df[df['Similarity'] > POLYFUZZ_SIMILARITY_THRESHOLD] # Filter out any low similarity matches
    # TODO: Add code to do sentiment analysis & only include 'positive' mentions of found/matched phrase!
    #df = df[df['To'].apply(lambda x: TextBlob(x).sentiment.polarity > 0)] # Filter out negative sentiment matches
    if 'From' in df: # Check that 'From' column exists
        # Only include non-null fuzzy matches
        matches.extend(df['From'].dropna().tolist())
    return matches

# TODO: Remove this previous 'clean' method
#def clean_data(matches):
#    """Clean the matches using nltk"""
#    cleaned = []
#    for match in matches:
#        tokens = word_tokenize(match)
#        # Lowercase
#        tokens = [token.lower() for token in tokens]
#        cleaned.append(' '.join(tokens))
#    return cleaned

def cluster_data(cleaned):
    """Cluster the cleaned matches using spaCy"""
    clusters = {}
    for match in cleaned:
        doc1 = SPACY_NLP(match)
        found = False
        for key, value in clusters.items():
            doc2 = SPACY_NLP(key)
            if doc1.similarity(doc2) > CLUSTER_SIMILARITY_THRESHOLD: # Check if the match is similar to an existing cluster
                clusters[key].append(match)
                found = True
                break
        if not found: # Create a new cluster if no similar one exists
            clusters[match] = [match]
    return clusters

def rank_data(clusters):
    """Rank the clusters based on their popularity and references"""
    rankings = []
    for clusterName, cluster in clusters.items():
        score = len(cluster) # The score is the number of matches found in the cluster
        rankings.append([score, clusterName, cluster])
    rankings.sort(reverse=True) # Sort the rankings by descending score
    return rankings

def display_data(siteRankings):
    """Display the rankings in a table using Streamlit"""
    for site in siteRankings:
        topRankedMatches = siteRankings[site]
        st.write(f"Top #{TOP_NUMBER} matches of '{PHRASE}' " + "on {}:".format(site))
        df = pd.DataFrame(topRankedMatches[:TOP_NUMBER], columns=['Score', 'Phrase', 'Mentions'])
        df.index = df.index + 1 # Add row numbers
        st.table(df)
        st.write("\n")

#endregion

# Execute Main Logic
if st.button("Run"):
    sites = SITES.split(',')
    siteData = {}
    siteRankings = {}
    for site in sites:
        scrapedData = scrape_data(site)
        matchedData = fuzzy_match(scrapedData, PHRASE)
        clusteredData = cluster_data(matchedData)
        rankings = rank_data(clusteredData)
        siteRankings[site] = rankings
    display_data(siteRankings)
import json
import numpy as np
import pandas as pd
import gspread
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity
from oauth2client.service_account import ServiceAccountCredentials

# Load Google Sheets credentials
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('./credentials.json', scope)
client = gspread.authorize(creds)

# Load data from Google Sheets
artists_sheet = client.open('Artists').sheet1
listings_sheet = client.open('Listings').sheet1

artists_df = pd.DataFrame(artists_sheet.get_all_records())
listings_df = pd.DataFrame(listings_sheet.get_all_records())

# Combine artist tags and listing keywords into a single column
artists_df['combined_tags'] = artists_df['tags']
listings_df['combined_tags'] = listings_df['description']

# Tokenize tags
artists_tokens = [tags.split(', ') for tags in artists_df['combined_tags']]
listings_tokens = [tags.split(' ') for tags in listings_df['combined_tags']]

# Train Word2Vec model
model = Word2Vec(sentences=artists_tokens + listings_tokens, vector_size=100, window=5, min_count=1, workers=4)

# Create a dictionary to store the ranked opportunities for each artist
artist_opportunities = {}

# Iterate over each artist
for index, artist_row in artists_df.iterrows():
    # Get the vector representation of artist tags
    artist_tags = artist_row['combined_tags'].split(', ')
    artist_vectors = np.array([model.wv[tag] for tag in artist_tags])

    # Calculate the mean vector for artists
    mean_artist_vector = np.mean(artist_vectors, axis=0)

    # Calculate the cosine similarity between artist and listing vectors
    similarities = []
    for listing_tags in listings_df['combined_tags']:
        listing_tags = listing_tags.split(' ')
        listing_vectors = np.array([model.wv[tag] for tag in listing_tags])

        # Calculate the mean vector for listings
        mean_listing_vector = np.mean(listing_vectors, axis=0)

        # Calculate cosine similarity
        similarity = cosine_similarity([mean_artist_vector], [mean_listing_vector])[0][0]
        similarities.append(similarity)

    # Create a DataFrame with opportunities, their similarity scores and tags + descriptions
    opportunities_df = pd.DataFrame({
        'listing_id': listings_df['title'],
        'similarity': similarities,
        'artist tags': artist_tags,
        'description': listings_df['description']
    })

    # Sort opportunities by similarity score in descending order
    opportunities_df = opportunities_df.sort_values(by='similarity', ascending=False)

    # Store the ranked opportunities for the artist
    artist_opportunities[artist_row['name']] = opportunities_df.to_dict(orient='records')

# Save the results to a JSON file for now
with open('artist_opportunities.json', 'w') as json_file:
    json.dump(artist_opportunities, json_file, indent=4)

# Print the ranked opportunities for each artist
for artist_id, opportunities_df in artist_opportunities.items():
    artist_name = artists_df.loc[artists_df['name'] == artist_id, 'name'].values[0]
    print(f"{len(opportunities_df)} opportunities found for artist {artist_name} (ID: {artist_id})\n")
    print("\n")

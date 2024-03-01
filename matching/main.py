import pandas as pd
from chroma import ChromaDBClient, DataProcessor, FirebaseClient, ResultsExporter


def run_daily_matching(
        firebase_client: FirebaseClient,
        chroma_client: ChromaDBClient,
        collection_name: str,
        artist_collection_name: str,
        input_count: int = 10,
):
    # Retrieve data from Firebase for the first 10 artists
    artists_data = firebase_client.get_collection_data(collection_name=artist_collection_name).limit(input_count)

    # Transform data to get tags of the first 10 artists
    input_tags = DataProcessor.get_tags_from_artists(artists_data)

    # Create Chroma collection
    chroma_collection = chroma_client.create_collection(name=collection_name)

    # Retrieve data from Firebase for listings
    listings_data = firebase_client.get_collection_data(collection_name="listings")

    # Transform data
    listings_ids, listings_documents, listings_metadatas = DataProcessor.transform_artist_data(listings_data)

    # Add documents to Chroma collection
    chroma_client.add_documents_to_collection(
        collection=chroma_collection,
        ids=listings_ids,
        documents=listings_documents,
        metadatas=listings_metadatas
    )

    # Query Chroma collection
    results = chroma_client.query_collection(
        collection=chroma_collection,
        query_texts=input_tags,
        n_results=1
    )
    
    # Create a DataFrame to store the results
    result_df = pd.DataFrame({
        'tags': input_tags,
        'chroma_listing': [result[0] for result in results['documents']],
        'chroma_distance': [result[0] for result in results['distances']],
    })

    # Export results to CSV
    ResultsExporter.export_results_to_csv(result_df, filename='chroma_results.csv')


if __name__ == "__main__":
    run_daily_matching(
        firebase_client=FirebaseClient(),
        chroma_client=ChromaDBClient(),
        collection_name="results",
        artist_collection_name="users",
        input_count=10
    )

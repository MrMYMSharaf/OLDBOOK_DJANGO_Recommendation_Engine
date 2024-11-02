import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Books

def get_recommendations(book_ids):
    if not book_ids:
        return []
    
    # Step 1: Fetch all books from the database
    books = Books.objects.all()
    
    # Convert to a DataFrame
    books_df = pd.DataFrame(list(books.values('id', 'Book_Title', 'Description', 'Publisher', 'Book_Author')))
    
    # Step 2: Handle missing values
    books_df['Book_Title'] = books_df['Book_Title'].fillna('')
    books_df['Description'] = books_df['Description'].fillna('')
    books_df['Publisher'] = books_df['Publisher'].fillna('')
    books_df['Book_Author'] = books_df['Book_Author'].fillna('')
    
    # Step 3: Create combined features for similarity calculation (title + description + publisher + author)
    books_df['combined_features'] = (
        books_df['Book_Title'] + ' ' + books_df['Description'] + ' ' + books_df['Publisher'] + ' ' + books_df['Book_Author']
    )
    
    # Step 4: Initialize the vectorizer (TF-IDF)
    tfidf = TfidfVectorizer(stop_words='english')
    
    # Step 5: Fit the vectorizer on the combined features
    tfidf_matrix = tfidf.fit_transform(books_df['combined_features'])
    
    # Step 6: Compute cosine similarity matrix
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    # Step 7: Get indices of books in the DataFrame that match the provided book_ids
    indices = pd.Series(books_df.index, index=books_df['id']).drop_duplicates()
    
    recommended_books = set()  # To store unique recommendations
    
    # Step 8: Loop through the given book_ids to get recommendations
    for book_id in book_ids:
        if book_id in indices:
            idx = indices[book_id]  # Get index of the book
            sim_scores = list(enumerate(cosine_sim[idx]))  # Get pairwise similarity scores
            
            # Sort books based on similarity score
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            
            # Get top 5 most similar books (excluding the current book itself)
            sim_scores = sim_scores[1:6]  # Ignore the first book (it's the same book)
            
            # Get the recommended book indices
            book_indices = [i[0] for i in sim_scores]
            
            # Append recommended books based on similarity indices
            recommended_books.update(books_df['id'].iloc[book_indices].tolist())

    return list(recommended_books)

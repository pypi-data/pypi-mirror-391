from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

# Create a dataset
data = {
    'movie': [f'movie {i}' for i in range(1, 21)],
    'genre': [
        'Action Adventure', 'Romance Drama', 'Sci-Fi Mystery', 'Crime Thriller',
        'War Action', 'Action Sci-Fi', 'Horror Mystery', 'Comedy Adventure',
        'Fantasy Adventure', 'Drama', 'Family Comedy', 'Sci-Fi Action',
        'Drama Romance', 'Sci-Fi Fantasy', 'Adventure Action', 'Post-Apocalypse',
        'Musical Drama', 'Adventure Fantasy', 'Romance Comedy', 'Action Thriller'
    ],
    'rating': [
        7.5, 8.2, 8.7, 7.9, 6.5, 8.1, 6.8, 7.3, 8.4, 7.0,
        7.6, 8.5, 8.0, 8.9, 7.7, 6.9, 7.2, 8.3, 7.8, 8.0
    ]
}

df = pd.DataFrame(data)

# Combine genre and rating into one feature (treat rating as text for vectorizer)
df['features'] = df['genre'] + ' ' + df['rating'].astype(str)

# Vectorize
vectorizer = CountVectorizer()
count_matrix = vectorizer.fit_transform(df['features'])

# Compute cosine similarity
cosine_sim = cosine_similarity(count_matrix, count_matrix)

# Function to get recommendations
def recommend(movie_name, n=5):
    if movie_name not in df['movie'].values:
        return "Movie not found!"
    
    idx = df.index[df['movie'] == movie_name][0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:n+1]
    movie_indices = [i[0] for i in sim_scores]
    return df.iloc[movie_indices][['movie', 'genre', 'rating']]

# Example: get top 5 similar to movie 5
print("Top 5 similar movies to 'movie 5':\n")
print(recommend('movie 5'))

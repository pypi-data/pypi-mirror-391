import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
import matplotlib.pyplot as plt

# --- Step 1: Create dataset ---
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
df['features'] = df['genre'] + ' ' + df['rating'].astype(str)

# --- Step 2: Compute cosine similarity ---
vectorizer = CountVectorizer()
count_matrix = vectorizer.fit_transform(df['features'])
cosine_sim = cosine_similarity(count_matrix)

# --- Step 3: Create weighted graph ---
G = nx.Graph()

# Add nodes (movies)
for movie in df['movie']:
    G.add_node(movie)

# Add weighted edges (similarity)
for i in range(len(df)):
    for j in range(i + 1, len(df)):
        weight = cosine_sim[i][j]
        if weight > 0:  # only add edges with nonzero similarity
            G.add_edge(df.loc[i, 'movie'], df.loc[j, 'movie'], weight=weight)

# --- Step 4: Visualize network ---
plt.figure(figsize=(10, 8))

# layout for better visuals
pos = nx.spring_layout(G, seed=42, k=0.4)

# draw nodes
nx.draw_networkx_nodes(G, pos, node_size=600, node_color='lightblue')

# draw edges with transparency based on weight
edges = G.edges(data=True)
nx.draw_networkx_edges(
    G, pos,
    edgelist=[(u, v) for u, v, d in edges],
    width=[d['weight'] * 5 for u, v, d in edges],
    alpha=0.6
)

# labels
nx.draw_networkx_labels(G, pos, font_size=9)

plt.title("Movie Similarity Network (Weighted by Cosine Similarity)")
plt.axis('off')
plt.show()

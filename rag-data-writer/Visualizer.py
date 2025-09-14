from collections import Counter
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from DocumentProcessor import load_support_documents, prepare_docs
from IPython.display import Markdown, display


def plot_support_type_distribution():
    
    documents = load_support_documents()
    prepare_docs(documents)
    
    support_types = [doc.metadata.get('support_type', 'unknown') for doc in documents]
    support_type_counts = Counter(support_types)
    plt.bar(support_type_counts.keys(), support_type_counts.values())
    plt.xlabel('Support Type')
    plt.ylabel('Count')
    plt.title('Support Type Distribution')
    plt.xticks(rotation=45)
    plt.show()
    
def plot_document_character_stats():

    documents = load_support_documents()
    prepare_docs(documents)

    # Calculate character counts
    char_counts = [len(doc.page_content) for doc in documents]
    
    # Calculate statistics
    avg_chars = np.mean(char_counts)
    max_chars = np.max(char_counts)
    min_chars = np.min(char_counts)
    median_chars = np.median(char_counts)
    std_chars = np.std(char_counts)
    avg_tokens = avg_chars / 4  # Rough estimate of tokens (1 token ~ 4 characters)
    
    # Create subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot 1: Histogram of character counts
    ax1.hist(char_counts, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
    ax1.axvline(avg_chars, color='red', linestyle='--', linewidth=2, label=f'Average: {avg_chars:.0f}')
    ax1.axvline(median_chars, color='green', linestyle='--', linewidth=2, label=f'Median: {median_chars:.0f}')
    ax1.set_xlabel('Number of Characters')
    ax1.set_ylabel('Number of Documents')
    ax1.set_title('Distribution of Document Character Counts')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Box plot
    ax2.boxplot(char_counts, vert=True)
    ax2.set_ylabel('Number of Characters')
    ax2.set_title('Character Count Statistics')
    ax2.grid(True, alpha=0.3)
    
    plt.figtext(0.02, 0.02, "", fontsize=10, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
    
    plt.tight_layout()
    plt.show()
    
    # Print summary statistics
    print(f"Document Character Count Summary:")
    print(f"Total documents: {len(documents)}")
    print(f"Average characters: {avg_chars:.1f}")
    print(f"Median characters: {median_chars:.1f}")
    print(f"Min characters: {min_chars}")
    print(f"Max characters: {max_chars}")
    print(f"Standard deviation: {std_chars:.1f}")
    print(f"Average tokens: {avg_tokens:.1f}")

def visualize_vector_db(collection):
    result = collection.get(include=['embeddings', 'documents', 'metadatas'])
    vectors = np.array(result['embeddings'])
    
    documents = result['documents']
    metadatas = result['metadatas']
    support_types = [metadata['support_type'] for metadata in metadatas]
    colors = [['blue', 'green', 'red', 'yellow'][['generic_frontend', 'wizard', 'admin', 'generic'].index(t)] for t in support_types]
    
    tsne = TSNE(n_components=2, random_state=42)
    reduced_vectors = tsne.fit_transform(vectors)

    # Create the 2D scatter plot
    fig = go.Figure(data=[go.Scatter(
        x=reduced_vectors[:, 0],
        y=reduced_vectors[:, 1],
        mode='markers',
        marker=dict(size=5, color=colors, opacity=0.8),
        text=[f"Type: {t}<br>Text: {d[:180]}..." for t, d in zip(support_types, documents)],
        hoverinfo='text'
    )])

    fig.update_layout(
        title='2D Chroma Vector Store Visualization',
        scene=dict(xaxis_title='x',yaxis_title='y'),
        width=1024,
        height=768,
        margin=dict(r=20, b=10, l=10, t=40)
    )

    fig.show()

    
def display_document_content(document):
    display(Markdown(document.page_content))
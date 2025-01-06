import re
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Load text file
with open('trainingDataSF.txt', 'r') as file:
    lines = file.readlines()

# Initialize lists for texts and labels
texts = []
labels = []

# Text preprocessing and label extraction
for line in lines:
    parts = line.strip().split('::')
    text = parts[0]
    percentages = list(map(float, parts[1:]))  # Convert to floats
    
    # Clean text
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # Removing non-alphabetic characters
    text = text.lower()  # Convert to lowercase
    text = ' '.join([word for word in word_tokenize(text) if word not in stopwords.words('english')])
    
    texts.append(text)
    labels.append(np.array(percentages) / 100.0)  # Normalize %

# Text vectorization
vectorizer = TfidfVectorizer(max_features=5000)
X = vectorizer.fit_transform(texts).toarray()

# Label conversion to numpy matrix
y = np.array(labels)

print(f'Textos procesados: {X.shape}, Etiquetas: {y.shape}')

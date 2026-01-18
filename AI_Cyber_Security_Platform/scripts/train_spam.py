import os
import joblib
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MODEL_PATH = os.path.join(ROOT, 'models', 'spam', 'spam_best_model.pkl')

# search common locations for spam.csv
possible = [
    os.path.join(ROOT, '..', 'Spam-detection-main', 'Spam-detection-main', 'data', 'spam.csv'),
    os.path.join(ROOT, '..', 'Spam-detection-main', 'Spam-detection-main', 'spam.csv'),
    os.path.join(ROOT, '..', 'Spam-detection-main', 'spam.csv'),
    os.path.join(ROOT, 'models', 'spam', 'spam.csv'),
]

csv_path = None
for p in possible:
    p = os.path.abspath(p)
    if os.path.exists(p):
        csv_path = p
        break

if not csv_path:
    print('Could not find spam.csv in expected locations. Please provide dataset at one of:')
    for p in possible:
        print('  -', os.path.abspath(p))
    raise SystemExit(1)

print('Using dataset:', csv_path)
df = pd.read_csv(csv_path, encoding='latin-1')
if 'v1' in df.columns and 'v2' in df.columns:
    df = df.rename(columns={'v1':'Class','v2':'Text'})
elif 'Label' in df.columns and 'Message' in df.columns:
    df = df.rename(columns={'Label':'Class','Message':'Text'})

df = df[['Class','Text']].dropna()
df['Class'] = df['Class'].map({'ham':0,'spam':1}).astype(int)

X = df['Text'].astype(str)
y = df['Class'].astype(int)

pipeline = Pipeline([
    ('vect', CountVectorizer(min_df=5, ngram_range=(1,2))),
    ('tfidf', TfidfTransformer()),
    ('clf', MultinomialNB())
])

print('Training pipeline...')
pipeline.fit(X, y)
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
joblib.dump(pipeline, MODEL_PATH)
print('Saved fitted pipeline to', MODEL_PATH)

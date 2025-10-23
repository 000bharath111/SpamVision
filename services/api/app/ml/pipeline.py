# app/ml/pipeline.py
"""
Builds and exposes pipeline building utilities.
This is intentionally compact but supports:
- TextCleaner transformer
- numeric feature extractor
- TF-IDF word + char branches
- optional sentence-transformer embeddings via provided transformer wrapper
- classifier choices: logistic, sgd, stacking
"""
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer, HashingVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import FunctionTransformer, StandardScaler
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.compose import ColumnTransformer
from sklearn.utils import resample
import numpy as np
import re
import string
from typing import List, Any, Dict

# reuse STOPWORDS from nltk if available
try:
    import nltk
    from nltk.corpus import stopwords
    _ = stopwords.words('english')
    STOPWORDS = set(stopwords.words('english'))
except Exception:
    STOPWORDS = set()

# simple emoji pattern
_EMOJI_PATTERN = re.compile("[\U0001F600-\U0001F64F" 
                            "\U0001F300-\U0001F5FF"
                            "\U0001F680-\U0001F6FF"
                            "\U0001F1E0-\U0001F1FF]+", flags=re.UNICODE)

PHONE_PATTERN = re.compile(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{2,4}\)?[-.\s]?){1,3}\d{2,4}')
URL_PATTERN = re.compile(r'http[s]?://\S+|www\.\S+')
EMAIL_PATTERN = re.compile(r'\S+@\S+')
HTML_TAG_RE = re.compile(r'<.*?>')

class TextCleaner(BaseEstimator, TransformerMixin):
    def __init__(self, lower=True, remove_stopwords=True, remove_emojis=True, mask_phone=True, mask_email=True, remove_urls=True, remove_html=True, remove_digits=False):
        self.lower = lower
        self.remove_stopwords = remove_stopwords
        self.remove_emojis = remove_emojis
        self.mask_phone = mask_phone
        self.mask_email = mask_email
        self.remove_urls = remove_urls
        self.remove_html = remove_html
        self.remove_digits = remove_digits

    def fit(self, X, y=None):
        return self

    def _mask_pii(self, text: str) -> str:
        if self.remove_urls:
            text = URL_PATTERN.sub(' URL ', text)
        if self.mask_email:
            text = EMAIL_PATTERN.sub(' EMAIL ', text)
        if self.mask_phone:
            text = PHONE_PATTERN.sub(' PHONE ', text)
        if self.remove_html:
            text = HTML_TAG_RE.sub(' ', text)
        return text

    def _clean_text(self, text: str) -> str:
        if not isinstance(text, str):
            text = str(text)
        text = text.replace('\n',' ').replace('\r',' ')
        text = re.sub(r'\s+',' ', text).strip()
        text = self._mask_pii(text)
        if self.remove_emojis:
            text = _EMOJI_PATTERN.sub(' ', text)
        text = text.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))
        if self.lower:
            text = text.lower()
        if self.remove_digits:
            text = re.sub(r'\d+', ' ', text)
        text = re.sub(r'\s+',' ', text).strip()
        if self.remove_stopwords:
            tokens = [t for t in text.split() if t not in STOPWORDS]
            text = " ".join(tokens)
        return text

    def transform(self, X, y=None):
        return np.array([self._clean_text(x) for x in X], dtype=object)

# numeric features extractor
def extract_numeric_features(texts: List[str]):
    lens = [len(t) for t in texts]
    word_counts = [len(t.split()) for t in texts]
    digit_counts = [sum(ch.isdigit() for ch in t) for t in texts]
    exclam = [t.count('!') for t in texts]
    quest = [t.count('?') for t in texts]
    uppercase = [sum(1 for ch in t if ch.isupper()) for t in texts]
    url_token = [t.lower().count('url') for t in texts]
    phone_token = [t.lower().count('phone') for t in texts]
    email_token = [t.lower().count('email') for t in texts]

    feats = np.vstack([
        lens, word_counts, digit_counts, exclam, quest, uppercase, url_token, phone_token, email_token
    ]).T.astype(float)
    return feats

numeric_feature_transformer = FunctionTransformer(lambda X: extract_numeric_features(X), validate=False)

# main builder
def build_pipeline(config: Dict[str, Any] = None):
    if config is None:
        config = {}
    use_hashing = config.get('use_hashing', False)
    include_word = config.get('include_word_tfidf', True)
    include_char = config.get('include_char_tfidf', True)
    include_numeric = config.get('include_numeric_feats', True)
    use_svd = config.get('use_svd', False)
    svd_components = config.get('svd_components', 150)
    classifier_choice = config.get('classifier', 'logreg')
    use_embeddings = config.get('use_embeddings', False)
    embedding_transformer = config.get('embedding_transformer', None)

    transformers = []

    if include_word:
        if use_hashing:
            transformers.append(('word_hash', HashingVectorizer(analyzer='word', ngram_range=(1,2), alternate_sign=False)))
        else:
            transformers.append(('word_tfidf', Pipeline([('vect', TfidfVectorizer(analyzer='word', ngram_range=(1,2), max_df=0.95, min_df=2))])))

    if include_char:
        if use_hashing:
            transformers.append(('char_hash', HashingVectorizer(analyzer='char', ngram_range=(3,5), alternate_sign=False)))
        else:
            transformers.append(('char_tfidf', Pipeline([('vect', TfidfVectorizer(analyzer='char', ngram_range=(3,5), max_df=0.95, min_df=2))])))

    if include_numeric:
        transformers.append(('num_feats', numeric_feature_transformer))

    if use_embeddings and embedding_transformer is not None:
        transformers.append(('embeds', embedding_transformer))

    union = FeatureUnion(transformers, n_jobs=-1)

    steps = [
        ('clean', TextCleaner(lower=True, remove_stopwords=True, remove_emojis=True,
                              mask_phone=True, mask_email=True, remove_urls=True, remove_html=True)),
        ('features', union),
    ]

    if use_svd and (include_word or include_char):
        steps.append(('svd', TruncatedSVD(n_components=svd_components, random_state=42)))

    # classifier selection
    if classifier_choice == 'stacking':
        estimators = [
            ('nb', MultinomialNB(alpha=1.0)),
            ('lr', LogisticRegression(max_iter=1000, solver='liblinear')),
            ('rf', RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=42))
        ]
        final = LogisticRegression(max_iter=1000)
        clf = StackingClassifier(estimators=estimators, final_estimator=final, passthrough=True, n_jobs=-1)
    elif classifier_choice == 'sgd':
        clf = SGDClassifier(loss='log', max_iter=1000, tol=1e-3, random_state=42)
    elif classifier_choice == 'logreg':
        clf = LogisticRegression(max_iter=1000)
    elif classifier_choice == 'rf':
        clf = RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=42)
    elif classifier_choice == 'nb':
        clf = MultinomialNB()
    else:
        clf = LogisticRegression(max_iter=1000)

    steps.append(('clf', clf))
    pipeline = Pipeline(steps)
    return pipeline

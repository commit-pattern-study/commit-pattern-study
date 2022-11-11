import re
import contractions
import nltk
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk import word_tokenize, RegexpTokenizer

nltk.download('punkt', quiet=True, raise_on_error=True)
nltk.download('stopwords', quiet=True, raise_on_error=True)
nltk.download('wordnet', quiet=True, raise_on_error=True)


def stem_tokenize(commit_msg: str) -> list[str]:
    tokenizer = PorterStemmer()
    return [tokenizer.stem(token) for token in word_tokenize(commit_msg)]


def lemma_tokenize(commit_msg: str) -> list[str]:
    tokenizer = WordNetLemmatizer()
    return [tokenizer.lemmatize(token) for token in word_tokenize(commit_msg)]


def regex_tokenize(commit_msg: str) -> list[str]:
    tokenizer = RegexpTokenizer(r'\w+')
    return tokenizer.tokenize(commit_msg)


def remove_stop_words(text: str) -> str:
    """Remove the noisy text in the text """
    stops = stopwords.words('english')
    stop_transformed = word_tokenize(' '.join(stops))
    text = text.lower()

    words = []
    for token in word_tokenize(text):
        if token not in stop_transformed:
            words.append(token)
    text_rm = ' '.join(words)
    return text_rm


def denoise(text: str) -> str:
    """Remove the noisy text in the text """
    text = text.lower()
    # remove html parser
    soup = BeautifulSoup(text, "html.parser")
    text = soup.get_text()
    # replace contractions in string of text
    text = contractions.fix(text)
    # remove the regex \n
    text = re.sub(r'[\n\t\s]', ' ', text)
    # remove punctuation
    text = re.sub(r'[\'\"!”#$%&’()*+,-./:;<=>?@[\]^_`{|}~\\]', ' ', text)
    return text

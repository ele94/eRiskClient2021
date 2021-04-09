import contractions
from nltk import word_tokenize
import nltk
import re
from nltk.corpus import stopwords



# cleans text, creates tokens and applies pos_tags
# only writings, no users
def preprocess_data(writings):
    preproc_writings = []
    for writing in writings:
        preproc_writing = writing.copy()
        preproc_writing["clean_text"] = clean_text(writing["title"] + " ." + writing["content"])
        if len(writing["clean_text"]) == 0:
            print("Text less than 0: ", writing["content"])
        preproc_writing["tokens"] = tokenize_text(writing["clean_text"])
        preproc_writing["pos_tags"] = pos_tag_text(writing["tokens"])
        preproc_writing["stems"] = stemmize_text(writing["tokens"])
        preproc_writings.append(preproc_writing)

    return preproc_writings



def clean_text(old_text):

    text = old_text.strip()
    text = re.sub(r'(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])?', 'URL', text, flags=re.MULTILINE)
    text = re.sub(r' #[0-9]+;', '', text)
    text = re.sub(r"[^\w\d'\s]+", ' ', text)
    text = re.sub('  ', ' ', text)
    text = contractions.fix(text)  # NEW!!!!
    if len(text) <= 0:
        print("Text less than 0", "old text:" , old_text, "new text:",  text)
        text = "0"
    return text

def tokenize_text(text):
    text = text.lower()
    text = remove_stopwords(text)
    text = word_tokenize(text)
    return text

# text tiene que venir en tokens
def pos_tag_text(text):
    text = nltk.pos_tag(text)
    return text

def remove_stopwords(text):
    pattern = re.compile(r'\b(' + r'|'.join(stopwords.words('english')) + r')\b\s*')
    text = pattern.sub('', text)
    return text


def stemmize_text(text):
    from nltk.stem import PorterStemmer
    ps = PorterStemmer()
    stems = [ps.stem(w) for w in text]
    return stems
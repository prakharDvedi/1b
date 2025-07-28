# utils/keywords.py
import re, itertools, collections
STOP = set("""a an the of for with from into and or to in on by at as is are be was were
              this that those these it they them you your his her he she we our us""".split())

def extract_keywords(text: str, top_n=40):
    words = re.findall(r'[A-Za-z]{4,}', text.lower())
    freq  = collections.Counter(w for w in words if w not in STOP)
    return [w for w,_ in freq.most_common(top_n)]

import unicodedata
from importlib.resources import files

_DATA = __package__.rsplit(".", 1)[0] + ".data"

_LANGS = {
"en","es","fr","de","it","pt","ru","tr","ar","zh","ja","ko",
"hi","bn","ta","te","mr","gu","kn","ml","pa"
}

def _norm(w):
    return unicodedata.normalize("NFKC", w).lower().strip()

def languages():
    return sorted(_LANGS)

def _read(fname):
    path = files(_DATA).joinpath(fname)
    return {_norm(x) for x in path.read_text("utf-8").splitlines()
            if x.strip() and not x.startswith("#")}

def get_stopwords(lang, categories=None):
    if categories is None:
        categories = ["base","slang","social"]
    if lang not in _LANGS:
        raise ValueError(f"Unsupported language {lang}. Try: {', '.join(_LANGS)}")
    sw = set()
    if "base" in categories:
        sw |= _read(f"{lang}.txt")
    if "slang" in categories:
        sw |= _read("slang.txt")
    if "social" in categories:
        sw |= _read("social.txt")
    return sw

def is_stopword(token, lang, categories=None):
    return _norm(token) in get_stopwords(lang, categories)

import argparse
from .loader import get_stopwords, languages

def main():
    p = argparse.ArgumentParser(description="Print stopwords for a language.")
    p.add_argument("--lang", "-l", required=True, help="Language code, e.g., en, hi, es")
    p.add_argument("--cats", "-c", default="base,slang,social",
                   help="Comma-separated categories: base, slang, social")
    p.add_argument("--sorted", action="store_true",
                   help="Sort output alphabetically")
    args = p.parse_args()

    cats = [c.strip() for c in args.cats.split(",") if c.strip()]
    sw = get_stopwords(args.lang, categories=cats)
    words = sorted(sw) if args.sorted else sw

    for w in words:
        print(w)

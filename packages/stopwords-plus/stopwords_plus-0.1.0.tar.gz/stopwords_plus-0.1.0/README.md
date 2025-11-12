# stopwords-plus

Stopwords for **20+ languages**, including:
- Modern slang (`lol`, `bruh`, `idk`, `imo`, `ngl`, etc.)
- Social media tokens (`rt`, `@`, `#`, `http`, `https`, etc.)

## Install
```bash
pip install stopwords-plus


from stopwords_plus import get_stopwords, is_stopword, languages
print(languages())
sw = get_stopwords("en", categories=["base","slang","social"])
print("lol" in sw)

exit()

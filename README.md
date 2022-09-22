### Install packages.
Create virtualenv first and then install poetry.

Install poetry
```shell
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```
Now install the packages.

```shell
poetry install poetry.lock
```

### Spacy Models
You need to install the following spacy models(english, italian) before running the code.
```shell
python -m spacy download en_core_web_sm
python -m spacy download it_core_news_sm
```

### The-Entities-Swissknife
TES is a streamlit App devoted to NEL: Named Entities Recognition and Wikification (linking wikipedia/wikidata) to support Semantic Publishing through Schema.org Structured Data Markup (in JSON-LD format).


### Razor api for testing
```text
f0852f0515c92c0686d129f79ff9c5584b87c1b67d503073a4c93ec9
```

Test urls
```text
https://alimentazionebambini.e-coop.it/pedagogia/giochi-di-natale-con-i-numeri-idea-montessori-5-6-anni/
https://alimentazionebambini.e-coop.it/pedagogia/metodo-montessori/ciclo-vitale-di-una-piantina-per-bambini-piccoli/
```
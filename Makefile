PY=python
# Include all NLTK data packages required by the pipeline
# NLTK 3.9 splits tokenizers into the `punkt` model and `punkt_tab` tables,
# so both resources need to be downloaded to avoid LookupError during
# tokenization.
NLTK_PACKAGES=punkt punkt_tab stopwords wordnet vader_lexicon

setup:
	$(PY) -m pip install -r requirements.txt
	$(PY) -m nltk.downloader $(NLTK_PACKAGES)
	$(PY) -m spacy download en_core_web_sm

reorg:
	$(PY) scripts/00_reorg.py

analyze:
	$(PY) scripts/01_clean_normalize.py
	$(PY) scripts/02_metrics.py
	$(PY) scripts/03_entities_topics.py
	$(PY) scripts/04_claims_timeline_geo.py
	$(PY) scripts/05_build_index.py

wiki:
	$(PY) scripts/06_build_wiki.py

all: reorg analyze wiki

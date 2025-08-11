PY=python

setup:
	$(PY) -m pip install -r requirements.txt
	$(PY) -m nltk.downloader punkt
	$(PY) -m nltk.downloader vader_lexicon
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

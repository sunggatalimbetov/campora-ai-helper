import re


_RU_STOP_WORDS = {
	"как",
	"что",
	"где",
	"когда",
	"кто",
	"почему",
	"зачем",
	"какой",
	"какие",
	"какая",
	"какое",
	"каких",
	"какого",
	"какому",
	"для",
	"нужно",
	"нужны",
	"нужна",
	"делать",
	"можно",
	"есть",
	"ли",
	"это",
	"мне",
	"мой",
	"моя",
	"мои",
	"на",
	"в",
	"и",
	"или",
	"с",
	"до",
	"у",
	"а",
	"о",
	"по",
	"не",
	"если",
	"то",
	"бы",
	"же",
	"ещё",
	"еще",
	"уже",
	"так",
	"при",
	"из",
	"за",
	"от",
	"чтобы",
	"все",
	"вы",
	"мы",
	"он",
	"она",
	"они",
	"вам",
	"нас",
	"вас",
	"его",
	"её",
	"их",
	"ты",
	"я",
	"ли",
	"будет",
	"было",
	"быть",
	"был",
	"была",
	"были",
	"очень",
	"тоже",
	"также",
	"только",
	"нет",
	"да",
	"чем",
	"кем",
	"после",
	"перед",
	"через",
	"над",
	"под",
}

_EN_STOP_WORDS = {
	"how",
	"what",
	"where",
	"when",
	"who",
	"why",
	"which",
	"do",
	"does",
	"did",
	"is",
	"are",
	"was",
	"were",
	"can",
	"could",
	"to",
	"the",
	"a",
	"an",
	"for",
	"of",
	"in",
	"on",
	"if",
	"my",
	"i",
	"you",
	"it",
}


def extract_fulltext_terms(query: str) -> str:
	"""
	Extract content words from a query for full-text search.

	Strips question words and stop words so websearch_to_tsquery produces
	a tighter AND condition with only meaningful terms.
	"""
	# Remove punctuation except hyphens (for codes like A-12)
	cleaned = re.sub(r"[^\w\s-]", " ", query)
	words = cleaned.split()

	content_words = []
	for w in words:
		lower = w.lower()
		if lower in _RU_STOP_WORDS or lower in _EN_STOP_WORDS:
			continue
		if len(w) <= 1:
			continue
		content_words.append(w)

	result = " ".join(content_words)
	# If we stripped everything, fall back to original query
	return result if result.strip() else query

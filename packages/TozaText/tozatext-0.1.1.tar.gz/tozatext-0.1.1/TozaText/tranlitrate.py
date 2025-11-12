from .doc_modifier import DocumentModifier  
try:
    from UzTransliterator import UzTransliterator
except ImportError:
    raise ImportError(
        "UzTransliterator is not installed. To use transliteration, run:\n"
        "pip install git+https://github.com/latofatbobojonova/UzTransliterator.git"
    )

class TransliteratorModifier(DocumentModifier):
    def __init__(self, from_: str = "cyr", to: str = "lat"):
        super().__init__()
        self.translit = UzTransliterator.UzTransliterator()
        self.from_ = from_
        self.to = to

    def modify_document(self, text: str,*args,**kwargs) -> str:
        if not isinstance(text, str):
            return text
        return self.translit.transliterate(text, from_=self.from_, to=self.to)



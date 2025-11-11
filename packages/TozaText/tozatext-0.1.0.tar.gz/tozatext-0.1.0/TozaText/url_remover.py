import re

from .doc_modifier import DocumentModifier

URL_REGEX = re.compile(r"https?://\S+|www\.\S+", flags=re.IGNORECASE)


class UrlRemover(DocumentModifier):
    """
    Removes all URLs in a document.
    """

    def __init__(self):
        super().__init__()

    def modify_document(self, text: str, *args, **kwargs) -> str:
        return URL_REGEX.sub("", text)
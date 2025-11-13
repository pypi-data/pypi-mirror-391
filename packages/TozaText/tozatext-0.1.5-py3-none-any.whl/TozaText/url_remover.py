import re
from .doc_modifier import DocumentModifier


class UrlEmojiRemover(DocumentModifier):
    """Remove URLs, Telegram links, and emojis from text."""

    def __init__(self):
        super().__init__()
        self.URL_REGEX = re.compile(r"(https?://\S+|www\.\S+|t\.me/\S+|telegram\.me/\S+|@[\w\.]+)|#\w+", flags=re.IGNORECASE)
        self.MARKDOWN_REGEX = re.compile(r'\[.*?\]\((?:https?://|http://|www\.)[^\s)]+\)', flags=re.IGNORECASE|re.DOTALL)
        self.EXTRA = re.compile(r"[\[\]\(\)\|]+")  
        self.UNDER_URL = re.compile(r'(\[.*?\]|\bhttps?://|\bt\.me/|www\.|vk\.com|youtube\.com|youtu\.be|twitter\.com|instagram\.com|telegram\.me|@[\w.]+|#\w+)')
        self.MARKDOWN_SYMBOLS = re.compile(r"(\*\*|__|~~|\*|`|_)+") 
        self.EXTRA_SYMBOLS = re.compile(r"[…⋯‥•·]+|(\.{3,}|—{2,}|–{2,})")
        self.EMOJI_REGEX = re.compile(
                "[" 
                "\U0001F000-\U0001FAFF"  # all emojis
                "\U00002500-\U00002BEF"  # geometric shapes + bullets (⏺ 🟢 etc.)
                "\U0001FB00-\U0001FBFF"  # symbol extensions
                "\u2000-\u206F"          # general punctuation (includes ZWJ etc.)
                "\u2190-\u21FF"          # arrows
                "\u2300-\u23FF"          # misc technical
                "\u2460-\u24FF"          # enclosed alphanumerics
                "\u2500-\u257F"          # box drawing
                "\u2580-\u259F"          # block elements
                "\u25A0-\u25FF"          # geometric shapes extended
                "\u2600-\u26FF"          # misc symbols
                "\u2700-\u27BF"          # dingbats
                "\u2900-\u297F"          # arrows supplemental
                "\u2B00-\u2BFF"          # arrows & shapes
                "\uFE0F"                 # variation selector
                "\u200D"                 # zero width joiner
                "]+",
                flags=re.UNICODE
            )


    def modify_document(self, text: str, *args, **kwargs) -> str:
        text = self.URL_REGEX.sub("", text)
        text = self.MARKDOWN_REGEX.sub("",text)
        text = self.UNDER_URL.sub("",text)
        text = self.EXTRA.sub("",text)
        text = self.EMOJI_REGEX.sub("", text)
        text = self.MARKDOWN_SYMBOLS.sub("",text)
        text = self.EXTRA_SYMBOLS.sub("",text)
        # lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        # text = "\n".join(lines)
        return text
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
                "\U0001F600-\U0001F64F"  # emoticons
                "\U0001F300-\U0001F5FF"  # symbols & pictographs
                "\U0001F680-\U0001F6FF"  # transport & map symbols
                "\U0001F700-\U0001F77F"  # alchemical symbols
                "\U0001F780-\U0001F7FF"  # geometric shapes
                "\U0001F800-\U0001F8FF"  # arrows etc.
                "\U0001F900-\U0001F9FF"  # supplemental symbols
                "\U0001FA00-\U0001FA6F"  # chess, dice
                "\U0001FA70-\U0001FAFF"  # symbols
                "\U00002700-\U000027BF"  # dingbats
                "\U000024C2-\U0001F251"  # misc symbols
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
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        text = "\n".join(lines)
        return text
import re
from .doc_modifier import DocumentModifier


class UrlEmojiRemover(DocumentModifier):
    """Remove URLs, Telegram links, and emojis from text."""

    def __init__(self):
        super().__init__()
        self.URL_REGEX = re.compile(r"(https?://\S+|www\.\S+|t\.me/\S+|telegram\.me/\S+|@[\w\.]+)|#\w+", flags=re.IGNORECASE)
        self.PLATFORM_NAMES = re.compile(r'\[(telegram|instagram|youtube|facebook|vk|tiktok|x|twitter|tg|kanal|obuna)\]',flags=re.IGNORECASE)
        self.MARKDOWN_LINK_KEEP_TEXT = re.compile(r'\[([^\]]+)\]\(([^)]+)\)',flags=re.IGNORECASE)
        self.BRACKETS_TEXT = re.compile(r'\[([^\]]+)\]')
        self.MARKDOWN_SYMBOLS = re.compile(r"(\*\*|__|~~|\*|`|_)+") 
        self.EXTRA_SYMBOLS = re.compile(r"[…⋯‥•·]+|(\.{3,}|—{2,}|–{2,})")
        self.SEPARATOR_REGEX = re.compile(r"([/\\|<>~=*\-]{2,})")
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
        text = self.MARKDOWN_LINK_KEEP_TEXT.sub(r"\1", text)
        text = self.PLATFORM_NAMES.sub("", text)
        text = self.URL_REGEX.sub("", text)
        text = self.BRACKETS_TEXT.sub(r"\1", text)
        text = self.EMOJI_REGEX.sub("", text)
        text = self.MARKDOWN_SYMBOLS.sub("", text)
        text = self.EXTRA_SYMBOLS.sub("", text)
        text = self.SEPARATOR_REGEX.sub(" ", text)
        # --- ADD NEW BLOCK HERE ---
        text = re.sub(r"[ \t]{2,}", " ", text)
        text = re.sub(r"\s+([.,!?;:])", r"\1", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n[ \t]+", "\n", text)
        # --- END NEW BLOCK ---
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        return "\n".join(lines)

import re
import logging
from .doc_modifier import DocumentModifier

logger = logging.getLogger(__name__)

import re
import logging
from .doc_modifier import DocumentModifier

logger = logging.getLogger(__name__)

class WordRepetitionFilter(DocumentModifier):
    """Remove consecutive repeated words, even if separated by punctuation."""

    def __init__(self, max_repetition=1):
        super().__init__()
        self.max_repetition = max_repetition
        self.change_count = 0

    def modify_document(self, text, *args, **kwargs):
        if not isinstance(text, str) or not text.strip():
            return text

        # Split tokens by space (keep punctuation attached)
        tokens = text.split()
        new_tokens = []

        prev_norm = None
        repetition_count = 0

        for tok in tokens:
            # Normalize token for comparison (remove punctuation + lowercase)
            norm = re.sub(r"[^\w]+$", "", tok).lower()

            if prev_norm == norm and norm != "":
                repetition_count += 1
                if repetition_count <= self.max_repetition:
                    new_tokens.append(tok)
                else:
                    # skip repeated token (collapse)
                    self.change_count += 1
                    logger.info(
                        f"[{self.__class__.__name__}] | skipped repeated '{tok}' (normalized as '{norm}')"
                    )
            else:
                new_tokens.append(tok)
                repetition_count = 1
                prev_norm = norm

        cleaned_text = " ".join(new_tokens)
        return cleaned_text


    

class ParagraphRepetitionFilter(DocumentModifier):
    """Remove texts with too many repeated paragraphs."""
    def __init__(self, max_paragraph_dup_ratio=0.3, max_char_dup_ratio=0.2):
        super().__init__()
        self.max_paragraph_dup_ratio = max_paragraph_dup_ratio
        self.max_char_dup_ratio = max_char_dup_ratio

    def modify_document(self, text: str, *args, **kwargs) -> str:
        paragraphs = re.compile(r"\n{2,}").split(text.strip())
        unique_x = set()
        duplicate_chars = 0
        duplicate_elements = 0
        for p in paragraphs:
            if p in unique_x:
                duplicate_chars += len(p)
                duplicate_elements += 1
            else:
                unique_x.add(p)

        if paragraphs:
            if duplicate_elements / len(paragraphs) > self.max_paragraph_dup_ratio:
                return ""
            if duplicate_chars / len(text) > self.max_char_dup_ratio:
                return ""

        return text

 
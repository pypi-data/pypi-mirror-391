from .doc_modifier import DocumentModifier
import re 
import ftfy
from ftfy import TextFixerConfig 

class UzbekUnicodeCleaner(DocumentModifier):
    """
    Clean up Uzbek texts and fix unicode errors.
    """

    def __init__(self):
        super().__init__()
        self.config = TextFixerConfig(
            normalization='NFC',       
            remove_control_chars=True,
            fix_line_breaks=True,
            explain=False         
        )

        # generic apostrophes
        self.uz_replacements = [
            (r"–", "—"),
            (r"«", "“"),
            (r"»", "”"),
            (r' \\"', " “"),
            (r'\\" ', "” "),
            (r"g['‘’`´]", "gʻ"),
            (r"o['‘’`´]", "oʻ"),
            (r"G['‘’`´]", "Gʻ"),
            (r"O['‘’`´]", "Oʻ"),
            (r"(?<![ogOG])[’'`´ʻ]", "ʼ"),
            (r" {2,}", " "),
        ]

    def modify_document(self, text, *args,**kwargs):
        
        if not isinstance(text, str):
            return text
        
        text = ftfy.fix_text(text, config=self.config)
        for pattern, repl in self.uz_replacements:
            text = re.sub(pattern, repl, text)
        
        return text.strip()



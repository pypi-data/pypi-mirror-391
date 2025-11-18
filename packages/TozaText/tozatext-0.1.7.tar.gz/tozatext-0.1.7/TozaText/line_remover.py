from .doc_modifier import DocumentModifier 

class LineRemover(DocumentModifier):
    """
    Removes lines from a document if the content of the line matches a given string.
    """

    def __init__(self, patterns: list[str]):
        """
        Args:
            patterns (List[str]): The patterns to check
        """
        super().__init__()
        self._patterns = patterns

    def modify_document(self, text: str,*args,**kwargs) -> str:
        lines = text.split("\n")
        new_lines = [line for line in lines if line not in self._patterns]
        return "\n".join(new_lines)
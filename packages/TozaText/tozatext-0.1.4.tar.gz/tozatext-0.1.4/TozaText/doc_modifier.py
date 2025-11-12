from abc import ABC, abstractmethod

class DocumentModifier(ABC):
    """
    Abstract base class for text-based document modifiers.

    Subclasses must implement `modify_document` to transform input value(s)
    and return the modified value. This supports both single-input and
    multi-input usage:
    - Single input: `modify_document(value)`
    - Multiple inputs: `modify_document(**values)` where each input field is
      expanded as a keyword argument (e.g., `modify_document(column_1=..., column_2=...)`).
    """

    def __init__(self) -> None:
        super().__init__()
        self._name = self.__class__.__name__
        self._sentences = None
        self._paragraphs = None
        self._ngrams = None

    @abstractmethod
    def modify_document(self, *args: object, **kwargs: object) -> object:
        """Transform the provided value(s) and return the result."""
        raise NotImplementedError

    @property
    def name(self) -> str:
        return self._name
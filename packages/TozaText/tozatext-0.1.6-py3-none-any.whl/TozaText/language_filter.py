import os
import numpy as np
from .doc_modifier import DocumentModifier
from fasttext import load_model
from datasets import Dataset

class LanguageFilter(DocumentModifier):
    """Detects text language and keeps only those matching the target."""

    def __init__(self, model_path: str = "lid.176.bin", target_lang: str = "uz", threshold: float = 0.4):
        super().__init__()
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model not found at {model_path}. "
                f"Download from: https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"
            )

        self.model = load_model(model_path)
        self.target_lang = target_lang
        self.threshold = threshold

    def modify_document(self, text: str, *args, **kwargs) -> dict | None:
        """Return dict with lang + accuracy; filter out if not target language."""
        doc = {}
        if not text:
            return None
        
        labels, probs = self.model.predict(text.replace("\n", " "))
        try:
            lang = labels[0].replace("__label__", "")
            score = float(probs[0])
        except ValueError:
            # fallback if probs returns weird type due to np.array(copy=False)
            probs = np.asarray(probs)
            score = float(probs[0])
            lang = labels[0].replace("__label__", "")

        # Attach metadata
        doc["lang"] = lang
        doc["lang_score"] = score
        doc["text"] = text

        return doc
    
    def __call__(self,dataset:Dataset,column_name:str) -> "Dataset":

        def _apply(example):
            text = example.get(column_name,"")
            output = self.modify_document(text)
            return {"lan":output['lang'],"lang_score":output['lang_score']}
        
        dataset = dataset.map(
            _apply,
            desc="Cleaning HF dataset",
            load_from_cache_file=False,
        )

        return dataset
        


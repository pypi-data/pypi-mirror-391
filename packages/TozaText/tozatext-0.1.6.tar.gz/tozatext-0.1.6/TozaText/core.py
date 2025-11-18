from datasets import Dataset
from time import perf_counter
from .utils.logging_utils import setup_logging
import json
from datetime import datetime
import os 

class Pipeline:
    """Runs a sequence of text modifiers on text, pandas DataFrame, or HF Dataset."""

    def __init__(self, modifiers:list, debug=False):
        self.modifiers = modifiers
        self.logger = setup_logging("logs/Pipeline.log", debug=debug)
        self.summary = {"texts_processed": 0, "modifiers": {}}

    def process_text(self, text: str) -> str:
        """Apply all modifiers to a single text string."""
        cleaned_text = text
        for modifier in self.modifiers:
            start = perf_counter()
            new_text = modifier.modify_document(cleaned_text)
            elapsed = perf_counter() - start

            changed = int(new_text != cleaned_text)
            name = modifier.__class__.__name__
            stats = self.summary["modifiers"].setdefault(name, {"changed": 0, "time": 0.0})
            stats["changed"] += changed
            stats["time"] += elapsed

            if not isinstance(new_text, str) or not new_text:
                new_text = cleaned_text  # fallback to previous valid text

            cleaned_text = new_text  

        self.summary["texts_processed"] += 1
        return cleaned_text

    def process_hf_dataset(self, dataset, column: str) -> "Dataset":
        """Clean Hugging Face Dataset column in place."""
        self.logger.info(f"Cleaning Hugging Face Dataset with {len(self.modifiers)} modifiers...")

        def _apply(example):
            text = example.get(column, "")
            cleaned_text = self.process_text(text)
            return {"cleaned_text": cleaned_text} 

        dataset = dataset.map(
            _apply,
            desc="Cleaning HF dataset",
            load_from_cache_file=False,
        )

        self._log_summary()
        return dataset

    def process(self, data, column: str = None): # type: ignore
        """Automatically process string or HF Dataset."""
        if isinstance(data, str):
            return self.process_text(data)
        elif isinstance(data, Dataset):
            if not column:
                raise ValueError("Specify `column` for Dataset input.")
            return self.process_hf_dataset(data, column)
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")

    def _log_summary(self):
        """Log and save a structured summary of the cleaning session."""
        total = self.summary["texts_processed"]
        self.logger.info("Cleaning summary:")
        self.logger.info(f"Texts processed: {total}")

        for name, stats in self.summary["modifiers"].items():
            pct = (stats["changed"] / total * 100) if total else 0
            self.logger.info(
                f"  • {name}: changed={stats['changed']} ({pct:.1f}%), time={stats['time']:.2f}s"
            )

        os.makedirs("logs", exist_ok=True)
        with open("logs/summary.json", "a", encoding="utf-8") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    **self.summary
                },
                f,
                ensure_ascii=False,
            )
            f.write("\n")

        self.logger.info("Logs saved to logs/tozatext.log\n")

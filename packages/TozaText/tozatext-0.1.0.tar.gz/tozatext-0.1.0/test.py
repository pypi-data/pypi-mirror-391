from datasets import load_dataset,disable_caching
from TozaText import Pipeline, WordRepetitionFilter, ParagraphRepetitionFilter

data = load_dataset("aktrmai/youtube_transcribe_data", split="train")


disable_caching()
pipeline = Pipeline([
    WordRepetitionFilter()
], debug=False)

cleaned_dataset = pipeline.process_hf_dataset(data, 'text')

# ✅ Save the Hugging Face dataset locally
cleaned_dataset.save_to_disk("cleaned_data")

# ✅ (optional) Push to Hub
cleaned_dataset.push_to_hub("aktrmai/youtube_transcribe_data")

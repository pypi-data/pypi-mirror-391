from TozaText import Pipeline, WordRepetitionFilter
from datasets import Dataset

data = Dataset.from_dict({"text": ["bu. bu. bu. shu shu sekin sekin qila qila"]})
pipeline = Pipeline([WordRepetitionFilter()])
cleaned = pipeline.process_hf_dataset(data, "text")

print("Before:", data["text"][0])
print("After:", cleaned["text"][0])

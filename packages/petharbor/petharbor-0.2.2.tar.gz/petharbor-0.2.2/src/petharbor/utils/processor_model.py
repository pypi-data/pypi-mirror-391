from petharbor.utils.logging_setup import get_logger

logger = get_logger()

from transformers import pipeline
from tqdm.contrib.logging import logging_redirect_tqdm
import pandas as pd
import torch


import os
import torch
import pandas as pd
import shutil
import torch.nn.functional as F
from tqdm.contrib.logging import logging_redirect_tqdm
from transformers import pipeline
from datasets import Dataset, concatenate_datasets
from pettag.utils.logging_setup import get_logger

logger = get_logger()


class ModelProcessor:
    """NER-based anonymisation processor with efficient batched processing and checkpointing."""

    def __init__(
        self,
        model: str,
        tokenizer: str = None,
        tag_map: dict = None,
        replaced: bool = True,
        text_column: str = "text",
        label_column: str = "predictions",
        device: str = None,
        batch_size: int = 256,
    ):
        self.model = model
        self.tokenizer = tokenizer if tokenizer is not None else model
        self.tag_map = tag_map or {}
        self.replaced = replaced
        self.text_column = text_column
        self.label_column = label_column
        self.device = (
            device if device else ("cuda:0" if torch.cuda.is_available() else "cpu")
        )
        self.batch_size = batch_size

        logger.info("Initializing NER pipeline")
        self.ner_pipeline = pipeline(
            "token-classification",
            model=self.model,
            tokenizer=self.tokenizer,
            aggregation_strategy="simple",
            device=0 if "cuda" in self.device else -1,
            torch_dtype=torch.float16 if "cuda" in self.device else torch.float32,
        )
        logger.info(f"Tag map: {self.tag_map}")

    @staticmethod
    def replace_token(text, start, end, replacement):
        """Replace a token in the text with a replacement string."""
        if start < 0 or end > len(text):
            logger.warning(
                f"Start index {start} or end index {end} is out of bounds for text of length {len(text)}"
            )
            raise ValueError("Start and end indices are out of bounds.")
        return text[:start] + replacement + text[end:]

    def _process_batch(self, examples):
        """Apply NER and replace identified entities with tags."""
        original_texts = examples[self.text_column]
        lower_texts = [str(text).lower() for text in original_texts]

        try:
            # Run NER on batch
            ner_results = self.ner_pipeline(lower_texts, batch_size=self.batch_size)
        except Exception as e:
            logger.error(f"Error during NER pipeline processing: {e}")
            raise

        anonymized_texts = []
        for i, entities in enumerate(ner_results):
            text = original_texts[i]
            for entity in sorted(entities, key=lambda x: x["start"], reverse=True):
                tag = self.tag_map.get(entity["entity_group"])
                if tag:
                    text = self.replace_token(text, entity["start"], entity["end"], tag)
            anonymized_texts.append(text)

        if self.replaced is True:
            return {self.text_column: anonymized_texts}
        elif self.replaced is False:
            return {self.label_column: ner_results}
        else:
            return {
                self.label_column: ner_results,
                self.text_column: anonymized_texts,
            }

    def anonymise(self, dataset, replace=True, cache_dir="./cache_predictions"):
        """Apply NER-based anonymisation to a dataset with batch and checkpoint support."""
        self.replaced = replace
        date_time = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        cache_dir = os.path.abspath(cache_dir)
        os.makedirs(cache_dir, exist_ok=True)

        chunk_size = 50_000
        total_records = len(dataset)
        num_chunks = (total_records + chunk_size - 1) // chunk_size
        processed_chunks = []

        logger.info(
            f"Starting anonymisation over {total_records} records in {num_chunks} chunks..."
        )

        with logging_redirect_tqdm():
            for i in range(num_chunks):
                start_idx = i * chunk_size
                end_idx = min((i + 1) * chunk_size, total_records)
                chunk_path = os.path.join(cache_dir, f"chunk_{i}")

                if os.path.exists(chunk_path):
                    logger.info(f"Found checkpoint for chunk {i+1}/{num_chunks}, skipping...")
                    processed_chunk = Dataset.load_from_disk(chunk_path)
                else:
                    logger.info(f"Processing chunk {i+1}/{num_chunks} ({start_idx}:{end_idx})...")
                    subset = dataset.select(range(start_idx, end_idx))
                    processed_chunk = subset.map(
                        self._process_batch,
                        batched=True,
                        batch_size=self.batch_size,
                        desc=f"[{date_time} |   INFO  | PetHarbor-Advance | Chunk {i+1}/{num_chunks}]",
                        load_from_cache_file=False,
                    )
                    processed_chunk.save_to_disk(chunk_path)

                processed_chunks.append(processed_chunk)

        logger.info(f"Concatenating {len(processed_chunks)} chunks...")
        processed_dataset = concatenate_datasets(processed_chunks)

        shutil.rmtree(cache_dir)
        logger.info("All chunks combined. Cache cleared.")

        return processed_dataset

    def single_anonymise(self, dataset):
        """Run anonymisation on a single record."""
        dataset = dataset.select([0])
        processed = self._process_batch(examples=dataset)
        return Dataset.from_dict({
            self.text_column: dataset[self.text_column],
            self.label_column: processed.get(self.label_column),
        })

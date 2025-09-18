import os
import backoff
from tqdm import tqdm
import tiktoken
from enum import Enum
from typing import (
    AbstractSet,
    Any,
    Callable,
    Collection,
    Iterable,
    List,
    Literal,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
)
import re
import logging
logger = logging.getLogger(__name__)
import nltk
nltk.download('punkt_tab')

from typing import List
from pydantic import BaseModel

class SplitResponse(BaseModel):
    split_after: List[int]

# based on https://github.com/brandonstarxel/chunking_evaluation/blob/main/chunking_evaluation/chunking/llm_semantic_chunker.py

class LLMSemanticChunker:
    """
    LLMSemanticChunker is a class designed to split text into thematically consistent sections based on suggestions from a Language Model (LLM).
    Users can choose between OpenAI and Anthropic as the LLM provider.

    Args:
        - llm
        - max_content (int): how many sentences we feed in one go to the LLM model to split
    """
    def __init__(self, llm, max_content: int=100, max_invokation_try: int=3):
        self.llm = llm
        self.max_content = max_content
        self.max_invokation_try = max_invokation_try

    def get_prompt(self, chunked_input, current_chunk=0, invalid_response=None):
        messages = [
            {
                "role": "system", 
                "content": (
                    "You are an assistant specialized in splitting text into thematically consistent sections. "
                    "The text has been divided into chunks, each marked with <|start_chunk_X|> and <|end_chunk_X|> tags, where X is the chunk number. "
                    "Your task is to identify the points where splits should occur, such that consecutive chunks of similar themes stay together. "
                    "Respond with a list of chunk IDs where you believe a split should be made. For example, if chunks 1 and 2 belong together but chunk 3 starts a new topic, you would suggest a split after chunk 2. THE CHUNKS MUST BE IN ASCENDING ORDER."
                    "Your response should be in the form: 'split_after: 3, 5'."
                )
            },
            {
                "role": "user", 
                "content": (
                    "CHUNKED_TEXT: " + chunked_input + "\n\n"
                    "Respond only with the IDs of the chunks where you believe a split should occur. YOU MUST RESPOND WITH AT LEAST ONE SPLIT. THESE SPLITS MUST BE IN ASCENDING ORDER AND EQUAL OR LARGER THAN: " + str(current_chunk)+"." + (f"\n\The previous response of {invalid_response} was invalid. DO NOT REPEAT THIS ARRAY OF NUMBERS. Please try again." if invalid_response else "")
                )
            },
        ]
        return messages

    def split_text(self, text: str, max_invokation_try: int=3):
        """

        Args:
            - text (str): the input text
            - max_invokation_try (int): how many time try an invokation
        """
        import re

        # split to sentence
        chunks = nltk.sent_tokenize(text)

        split_indices = []

        short_cut = len(split_indices) > 0

        from tqdm import tqdm

        current_chunk = 0

        with tqdm(total=len(chunks), desc="Processing chunks") as pbar:
            while True and not short_cut:

                chunked_input = ""

                finishing_chunk = 0
                # collect the sentence shunks for feed to one LLM call
                for i in range(current_chunk, len(chunks)):
                    finishing_chunk = i+1
                    chunked_input += f"<|start_chunk_{finishing_chunk}|>{chunks[i]}<|end_chunk_{finishing_chunk}|>"
                    if i-current_chunk > self.max_content:
                        break

                messages = self.get_prompt(chunked_input, current_chunk)

                invokation_count = 0
                while True:
                    if invokation_count > self.max_invokation_try:
                        print("Tried to many time to invoke the LLM model. Giving up. If you want more try incrase the max_invokation_try!")
                        break
                    try:
                        result_string = self.llm.with_structured_output(SplitResponse).invoke(messages)
                    except:
                        print(f"Error in {messages}")
                        break
                    numbers = result_string.split_after

                    # Check if the numbers are in ascending order and are equal to or larger than current_chunk
                    if not (numbers != sorted(numbers) or any(number < current_chunk for number in numbers)):
                        break
                    else:
                        messages = self.get_prompt(chunked_input, current_chunk, numbers)
                        print("Response: ", result_string)
                        print("Invalid response. Please try again.")
                        invokation_count += 1

                # we went across all of the text
                if finishing_chunk == len(chunks):
                    split_indices.extend(numbers)
                    break
                else:
                    # there is still text which we have not processed
                    # if there is a break in the end we ignore it so we add to the next content
                    if numbers[-1] == finishing_chunk and len(numbers) > 1:
                        split_indices.extend(numbers[:-1])
                    else:
                        split_indices.extend(numbers)
                        
                    current_chunk = split_indices[-1]

                pbar.update(current_chunk - pbar.n)

        pbar.close()

        chunks_to_split_after = [i - 1 for i in split_indices]

        docs = []
        current_chunk = ''
        for i, chunk in enumerate(chunks):
            current_chunk += chunk + ' '
            if i in chunks_to_split_after:
                docs.append(current_chunk.strip())
                current_chunk = ''
        if current_chunk:
            docs.append(current_chunk.strip())

        return docs
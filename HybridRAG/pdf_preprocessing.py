import os
import datetime
from typing import List, Dict, Optional, Type
import re

from crewai.utilities.constants import KNOWLEDGE_DIRECTORY
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from marker.config.parser import ConfigParser
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered


def setup_converter(config: Dict[str, Optional[Type]]) -> PdfConverter:
    """
    Set up the marker PDF converter with the given configuration.

    Args:
        config (Dict[str, Optional[Type]]): Configuration dictionary for the converter.
    Returns:
        PdfConverter: An instance of the PdfConverter configured with the provided settings.
    """
    # Configure the model with Gemini API or any LLM service (if required)
    artifact_dict = create_model_dict()

    converter = PdfConverter(artifact_dict=artifact_dict, config=config)
    return converter


# config for pdf -> Markdown conversion
config = {
    "output_format": "markdown",
    "use_llm": False,
    "paginate_output": False,
    "disable_image_extraction": True
}
config_parser = ConfigParser(config)
# Create the converter with the necessary settings
converter = setup_converter(config_parser.generate_config_dict())

headers_to_split_on = [
    ('#', 'Header_1'),
    ('##', 'Header_2'),
    ('###', 'Header_3'),
    ('####', 'Header_4'),
]
# Create a MarkdownHeaderTextSplitter instance with the specified headers
# This will split the text based on the specified headers and store them in metadata
# as 'Header_1', 'Header_2', etc.
markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)

def search_pdf(ticker: str):
    """
    Collect presentations and QA text from {ticker} company.
    The input to this tool should be a ticker, for example AAPL, NET.

    Args:
        ticker (str): The stock ticker symbol of the company to search for.

    Returns:
        dict: A dictionary where keys are file paths and values are the text content of the files

    """
    onlyfiles = [
        f for f in os.listdir(KNOWLEDGE_DIRECTORY)
        if os.path.isfile(os.path.join(KNOWLEDGE_DIRECTORY, f))
    ]
    company_files = [f for f in onlyfiles if ticker.lower().split('.')[0] == f.split("_")[0]]
    pdf_files = [ os.path.join(KNOWLEDGE_DIRECTORY, f) for f in company_files if f.endswith(".pdf")]

    content = {}
    for pdf_file in pdf_files:
        markdown_file = pdf_file.replace('.pdf', '.md')
        # convert pdf to markdown
        if not os.path.isfile(markdown_file):
            print(f'Converting {pdf_file} to Markdown')
            # Process the PDF file and convert to the specified output format
            rendered = converter(pdf_file)
            # Extract the text (Markdown, JSON, or HTML) from the rendered object
            text, _, _ = text_from_rendered(rendered)

            # save result
            output_dir = os.path.dirname(pdf_file)
            filename = os.path.basename(pdf_file).replace('.pdf', '.md')
            new_file = os.path.join(output_dir, filename)
            with open(new_file, 'w+') as file:
                file.write(text)

        # read Markdown file
        with open(markdown_file, 'r') as file:
            text = file.read()
        content[pdf_file] = text

    return content

def datetime_to_quarter(date_time: datetime.datetime) -> tuple:
    """
    Converts a given datetime object to the quarter of the year it falls into.
    Args:
        date_time (datetime): A datetime object representing the date to be converted.
    Returns:
        tuple: A tuple containing the year and the quarter in the format (YYYY, Qx),
               where x is the quarter number (1 to 4).
    Raises:
        ValueError: If the month in the datetime object is invalid (not between 1 and
    """
    # Extract the month and year from the datetime object
    month = date_time.month
    year = date_time.year

    # Determine the quarter based on the month
    if 1 <= month <= 3:
        quarter = "Q1"
    elif 4 <= month <= 6:
        quarter = "Q2"
    elif 7 <= month <= 9:
        quarter = "Q3"
    elif 10 <= month <= 12:
        quarter = "Q4"
    else:
        raise ValueError("Invalid month in datetime object.")

    # Return the result in 'Qx YYYY' format
    return year, quarter

def get_paragraphs(
    ticker: str, 
    max_lenght: int = 5000, 
    splitter: str = "Semantic", 
    **kwargs
) -> List[Document]:
    """
    Collects paragraphs from the PDF files of a given company ticker.

    Args:
        ticker (str): The stock ticker symbol of the company to search for.
        max_lenght (int): The maximum characters length of one paragraph
        splitter (str): how we split the paragraphs if they too long, default: "Semantic", Valid: "Semantic"
        **kwargs: Additional arguments for the SemanticChunker, such as:
            - model_name (str): The name of the model to use for embeddings.
            - breakpoint_threshold_type (str): The type of breakpoint threshold. Valid: "standard_deviation", "percentile".
            - breakpoint_threshold_amount (float): The amount for the breakpoint threshold.

    Returns:
        list: A list of Document objects, each containing a paragraph from the PDF files.
    """
    valid_splitters = ["Semantic", "RecursiveCharacter"]
    if splitter not in valid_splitters:
        raise ValueError(f"{splitter} is not a valid splitter! Valid values are: {valid_splitters.strip('[]')}")
    
    if splitter == "Semantic":
        # Extract kwargs with defaults
        model_name = kwargs.get("model_name", "FinLang/finance-embeddings-investopedia")
        breakpoint_threshold_type = kwargs.get("breakpoint_threshold_type", "percentile")
        breakpoint_threshold_amount = kwargs.get("breakpoint_threshold_amount", 70.0)

        # check settings
        valid_breakpoint_threshold_type = ["standard_deviation", "percentile", "interquartile"]
        if breakpoint_threshold_type not in valid_breakpoint_threshold_type:
            raise ValueError(
                f"{breakpoint_threshold_type} is not a valid splitter! Valid values are: {valid_breakpoint_threshold_type.strip('[]')}"
            )
        if breakpoint_threshold_type == "percentile":
            if breakpoint_threshold_amount < 1 or breakpoint_threshold_amount > 99:
                raise ValueError(f"The breakpoint_threshold_amount should be between 1 and 99! Current value: {breakpoint_threshold_amount}")
            breakpoint_threshold_amount = int(breakpoint_threshold_amount)
        elif breakpoint_threshold_type == "standard_deviation":
            if breakpoint_threshold_amount < 0:
                raise ValueError(f"The breakpoint_threshold_amount should be possitive! Current value: {breakpoint_threshold_amount}")
        elif breakpoint_threshold_type == "interquartile":
            if breakpoint_threshold_amount < 0:
                raise ValueError(f"The breakpoint_threshold_amount should be possitive! Current value: {breakpoint_threshold_amount}")

        # Initialize a semantic chunk splitter using OpenAI embeddings.
        text_splitter = SemanticChunker(
            HuggingFaceEmbeddings(
                model_name=model_name
            ),
            # Set the split breakpoint type to percentile
            breakpoint_threshold_type=breakpoint_threshold_type,
            breakpoint_threshold_amount=breakpoint_threshold_amount,
        )
    elif splitter == "RecursiveCharacter":
        chunk_size = kwargs.get("chunk_size", 2000)
        chunk_overlap = kwargs.get("chunk_overlap", 250)
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            # Specifies a function to calculate the length of the string.
            length_function=len,
            # Sets whether to use regular expressions as delimiters.
            is_separator_regex=False,
        )
    
    pdf_texts = search_pdf(ticker=ticker)

    paragraphs = []

    for k, text in pdf_texts.items():
        print(f'Processing: {k} file')
        report_start_time = datetime.datetime.strptime(k.split('_')[1], '%Y%m%d')
        reporting_start_year, reporting_start_quarter = datetime_to_quarter(report_start_time)
        report_end_time = datetime.datetime.strptime(k.split('_')[2], '%Y%m%d')
        reporting_end_year, reporting_end_quarter = datetime_to_quarter(report_end_time)
        text_type = k.split('_')[3]

        md_header_splits = markdown_splitter.split_text(text)

        for result in md_header_splits:
            this_paragraph = []
            if len(result.page_content) > max_lenght:
                # too long paragraph so we split them
                this_paragraph = text_splitter.split_text(result.page_content)
            else:
                this_paragraph.append(result.page_content)
            for this_split in this_paragraph:
                headers = ''
                for i in range(1, 5):
                    if f'Header_{i}' in result.metadata:
                        headers = '# ' + f" {result.metadata[f'Header_{i}']}\n\n"
                this_document = Document(
                    page_content=headers + this_split,
                    metadata={
                        'filename': k,
                        'reporting_year_start': reporting_start_year,
                        'reporting_quarter_start': reporting_start_quarter,
                        'reporting_year_end': reporting_end_year,
                        'reporting_quarter_end': reporting_end_quarter,
                        'document_type': text_type,
                        'source': ticker,
                        **result.metadata
                    }
                )
                paragraphs.append(this_document)

    return paragraphs
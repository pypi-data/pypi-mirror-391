import os
import logging
from pathlib import Path
from ..parser import BaseParser

class LlamaParser(BaseParser, name="llamaparser"):
    def __init__(self, result_type: str,
                 model: str,
                 parse_mode: str,
                 provider_and_model: str,
                 merge_tables_across_pages_in_markdown: bool,
                 preserve_layout_alignment_across_pages: bool,
                 hide_footers: bool,
                 hide_headers: bool
                 ) -> None:
        logging.info("Initializing LlamaParser...")
        self.result_type = result_type
        self.model = model
        self.parse_mode = parse_mode
        self.provider_and_model = provider_and_model
        self.merge_tables_across_pages_in_markdown = merge_tables_across_pages_in_markdown
        self.preserve_layout_alignment_across_pages = preserve_layout_alignment_across_pages
        self.hide_footers=hide_footers
        self.hide_headers=hide_headers

        from llama_parse import LlamaParse, ResultType
        if result_type.lower() in ("md", "markdown"):
            result_type = ResultType.MD
        api_key = os.getenv("LLAMA-PARSER-API-TOKEN")
        if not api_key:
            raise EnvironmentError("Missing LLAMA-PARSER-API-TOKEN in .env file.")
        self._parser = LlamaParse(api_key=api_key,
                                  result_type=result_type,
                                  model=self.model,
                                  parse_mode=self.parse_mode,
                                  merge_tables_across_pages_in_markdown=self.merge_tables_across_pages_in_markdown,
                                  preserve_layout_alignment_across_pages=self.preserve_layout_alignment_across_pages,
                                  hide_footers=self.hide_footers,
                                  hide_headers=self.hide_headers)

    def parse(self, file_path: Path, include_pagenumbers: bool=False) -> str:
        """
        Parse the document at file_path. 
        Args:
            file_path (Path): Path to the document to be parsed.
            include_pagenumbers (bool): Whether to include page numbers in the output. If True, page numbers will be wrapped around each page's content, like so: <PAGE_NUMBER 1>...content...</PAGE_NUMBER 1>
        """

        if not include_pagenumbers:
            documents = self._parser.load_data(str(file_path))

            result = "\n".join(doc.text for doc in documents)
        else:
            documents = self._parser.parse(file_path)

            if self.result_type.lower() in ("md", "markdown"):
                result = "\n".join(f"<PAGE_NUMBER {idx}>{page.md}</PAGE_NUMBER {idx}>" for idx, page in enumerate(documents.pages, start=1))
            else: 
                result = "\n".join(f"<PAGE_NUMBER {idx}>{page.text}</PAGE_NUMBER {idx}>" for idx, page in enumerate(documents.pages, start=1))

        return result

    def __call__(self, file_path: Path) -> str:
        return self.parse(file_path)
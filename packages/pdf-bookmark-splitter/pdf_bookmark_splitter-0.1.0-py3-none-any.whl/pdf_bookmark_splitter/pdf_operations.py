import os
from typing import List, Tuple
from pypdf import PdfReader, PdfWriter


class PdfSplitter:
    def __init__(self, file_path: str ):
        self.file_path = file_path
        self.reader = PdfReader(file_path)

    def _extract_outline_recursive(self, outline_items: list, titles: List[Tuple[str, int]]) -> None:
        """
        Recursively extracts all bookmark entries from nested outline structure.
        
        Args:
            outline_items: List of outline items (can contain nested lists)
            titles: Accumulator list to store extracted (title, page_number) tuples
        """
        for item in outline_items:
            if isinstance(item, list):
                # Recursively process nested outline
                self._extract_outline_recursive(item, titles)
            else:
                # Extract title and page number from bookmark
                title = item.get("/Title", "No Title")
                page_number = self.reader.get_destination_page_number(item)
                titles.append((title, page_number))

    def get_chapter_info(self) -> List[Tuple[str, int]]:
        """
        Extracts chapter information from the PDF document's outline.

        This method processes the PDF outline/bookmarks to find chapters and their corresponding page numbers.
        Processes ALL outline entries including nested sub-outlines recursively.

        Returns:
            List[Tuple[str, int]]: A list of tuples containing:
                - str: Chapter title
                - int: Corresponding page number in the PDF
            
            The list is sorted by page number in ascending order.

        Returns empty list if outline is empty or invalid.

        Example:
            >>> pdf.get_chapter_info()
            [('Chapter 1', 1), ('Chapter 1.1', 3), ('Chapter 2', 15), ('Chapter 2.1', 17)]
        """
        outline = self.reader.outline
        titles: List[Tuple[str, int]] = []

        if not outline or not isinstance(outline, list):
            # fail to get outline. return empty list
            return titles

        # Recursively extract all bookmarks
        self._extract_outline_recursive(outline, titles)
        
        # Sort by page number to ensure correct splitting order
        titles.sort(key=lambda x: x[1])

        return titles

    def split_chapters(self, output_dir: str) -> None:
        """
        Splits a PDF file into separate chapters based on bookmarks and saves them to the specified output directory.
        Args:
            output_dir (str): The directory path where the split PDF chapters will be saved.
                             If the directory doesn't exist, it will be created.
        Returns:
            None

        The method will:
        1. Create the output directory if it doesn't exist
        2. Get chapter information from bookmarks
        3. Split the PDF into chapters based on bookmark page numbers
        4. Save each chapter as a separate PDF file named after the chapter title
        If no chapters (bookmarks) are found, it will print a message and return without splitting.
        Example:
            pdf_splitter.split_chapters("output/chapters/")
            # Creates PDFs like: output/chapters/Chapter1.pdf, output/chapters/Chapter2.pdf, etc.
        """
        os.makedirs(output_dir, exist_ok=True)
        chapters = self.get_chapter_info()

        if not chapters:
            print("No chapters found")
            return

        total_pages = len(self.reader.pages)

        for i, (current_chapter, current_page) in enumerate(chapters):
            end_page = chapters[i + 1][1] if i < len(chapters) - 1 else total_pages
            writer = PdfWriter()

            for page_num in range(current_page, end_page):
                writer.add_page(self.reader.pages[page_num])

            output_file = os.path.join(output_dir, f"{current_chapter}.pdf")
            with open(output_file, "wb") as output:
                writer.write(output)

import os
import xml.etree.ElementTree as ET


class Books:

   # On one server all the 1-chapter books are missing. We provide a list for simplification
    # They should not need to care about case, so we provide both upper and lower case names
    _a_one_chapter_books = ['OB', 'PHIM', '2JOH', '3JOH', 'JUD', 'ob', 'phim', '2joh', '3joh', 'jud']

    # There are Psalms with a heading. MT includes the heading in v 1, some translations don't
    # This is the list of affected psalms
    _a_psalms_with_heading = [3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22, 30, 31, 34, 36, 39, 40,
                              41, 42, 44, 45, 46, 47, 48, 49, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
                              64, 65, 66, 67, 68, 69, 70, 75, 76, 77, 80, 81, 83, 84, 85, 88, 89, 102, 108, 140, 142]

    def __init__(self):

        # List of valid abbreviations. It will be filled in parse_books()
        self._a_valid_abbrevs = []

        # Read the books data from the xml file. As this is a package, we need to use the absolute path
        cwd = os.path.dirname(os.path.abspath(__file__))
        self._ad_books = self.parse_books(os.path.join(cwd, 'books.xml'))

    def parse_books(self, xml_file):
        # Parse the XML file
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Initialize an empty list to store dictionaries
        book_data = []

        # Iterate over each book in the XML
        for book in root.findall('book'):
            # Initialize a dictionary to store book data
            book_info = {
                'abbrev': book.get('abbrev'),
                'maxchapter': int(book.get('maxchapter')),
                'testament': book.get('testament'),
                'latex_abbrev': book.get('latex_abbrev'),
                'chapters': {}
            }

            # Remember this abbrev as a valid one
            self._a_valid_abbrevs.append(book.get('abbrev'))

            # Iterate over each chapter in the book
            for chapter in book.findall('chapter'):
                chapter_num = int(chapter.get('number'))
                verses = int(chapter.get('verses'))
                book_info['chapters'][chapter_num] = verses

            # Add book_info to the book_data list
            book_data.append(book_info)

        return book_data

    def get_valid_abbreviations(self):
        return self._a_valid_abbrevs


    # python
    def get_valid_abbreviations_readable(self):
        """Return readable abbreviations: first alphabetic char uppercase, all other letters lowercase.
        If an abbreviation starts with a digit, keep the digit and capitalize the first following letter.
        Non-letter characters before the first letter are preserved.
        """
        readable = []
        for abbr in self._a_valid_abbrevs:
            if not isinstance(abbr, str) or abbr == "":
                readable.append(abbr)
                continue

            # find index of first alphabetic character
            first_alpha_idx = None
            for i, ch in enumerate(abbr):
                if ch.isalpha():
                    first_alpha_idx = i
                    break

            if first_alpha_idx is None:
                # no letters at all -> keep as is
                readable.append(abbr)
                continue

            prefix = abbr[:first_alpha_idx]  # keep any leading digits/symbols
            first_char = abbr[first_alpha_idx].upper()  # capitalize first letter
            rest = abbr[first_alpha_idx + 1:].lower()  # lowercase remaining chars
            readable.append(prefix + first_char + rest)

        return readable

    def is_valid_abbreviation(self, abbrev):
        return abbrev.upper() in self._a_valid_abbrevs

    @classmethod
    def get_one_chapter_books(cls):
        return cls._a_one_chapter_books

    def get_sort_value(self, abbrev):
        try:
            return self._a_valid_abbrevs.index(abbrev.upper())
        except ValueError:
            return -1  # or any other value to indicate that the abbrev was not found

    # Get the highest chapter of a book
    def get_max_chapter(self, abbr):
        for book in self._ad_books:
            if book.get('abbrev') == abbr.upper():
                return int(book.get('maxchapter'))

    # Get the highest verse in a chapter of a book
    def get_max_verse(self, abbr, ch):

        # Convert chapter to integer if it is a string
        if isinstance(ch, str):
            try:
                ch = int(ch)
            except ValueError:
                return None  # Return None if conversion fails

        # Iterate through the list of book dictionaries
        for book in self._ad_books:
            if book['abbrev'] == abbr.upper():
                # Retrieve the verse count for the specified chapter dictionary
                return book['chapters'].get(ch, None)  # Return None if the chapter is not found
        return None  # Return None if the book abbreviation is not found

    @classmethod
    def get_psalms_with_heading(cls):
        return cls._a_psalms_with_heading

    @classmethod
    # Determine if a given Psalm has a heading. There are versions that do not consider the heading part of v 1
    def is_psalm_with_heading(cls, ch):
        # The chapter might come as an integer or as a string - but we need an integer
        if isinstance(ch, str):
            ch = int(ch)
        return ch in cls._a_psalms_with_heading

    # Determine if a book is in OT or NT
    def get_testament(self, book):
        for b in self._ad_books:
            if b['abbrev'] == book.upper():
                return b['testament']
        return None

    def get_latex_abbrev(self, book):
        for b in self._ad_books:
            if b['abbrev'] == book.upper():
                return b['latex_abbrev']
        return None

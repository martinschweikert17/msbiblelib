import re

from msbiblelib.mblbooks import Books



class References:

    def __init__(self):
        self._biblebooks = Books()

    def parse_reference(self, reference):
        """
        Analyses a given reference
        Splits it into its components
        Plausibility checks (book name, chapter and verse numbers, formal checks)
        Corrects references from one-chapter books: inserts chapter "1"
        Returns the reference in normalized form; messages if checks failed
        """
        parsed_info = {
            # Result of the analysis: True if a pattern could be identified and all values are within the limits;
            # False otherwise
            'passed': True,
            # One or more error descriptions
            'messages': '',
            # The reference in normalized form
            'reference': reference.translate(str.maketrans({',': '.', ':': '.'})),
            # Type of the reference; see patterns[] below
            'type': '',
            # Components of the reference
            'frombook': '',
            'tobook': '',
            'fromchapter': 0,
            'tochapter': 0,
            'fromverse': 0,
            'toverse': 0
        }

        # Patterns of references. From complex to simple, otherwise wrong matches!
        # The regex for the book names must also include 'ö' for "Kön", "Röm"
        patterns = [
            # gen1.1-2.6
            (r'^(\d?[a-zöA-ZÖ]+)(\d+)\.(\d+)-(\d+)\.(\d+)$', 'FBFCFVTCTV',
             ['frombook', 'fromchapter', 'fromverse', 'tochapter', 'toverse']),

            # gen1.1-6
            (r'^(\d?[a-zöA-ZÖ]+)(\d+)\.(\d+)-(\d+)$', 'FBFCFVTV', ['frombook', 'fromchapter', 'fromverse', 'toverse']),

            # gen1.1
            (r'^(\d?[a-zöA-ZÖ]+)(\d+)\.(\d+)$', 'FBFCFV', ['frombook', 'fromchapter', 'fromverse']),

            # gen1-2
            (r'^(\d?[a-zöA-ZÖ]+)(\d+)-(\d+)$', 'FBFCTC', ['frombook', 'fromchapter', 'tochapter']),

            # gen1
            (r'^(\d?[a-zöA-ZÖ]+)(\d+)$', 'FBFC', ['frombook', 'fromchapter']),

            # gen-ex
            (r'^(\d?[a-zöA-ZÖ]+)-(\d?[a-zA-Z]+)$', 'FBTB', ['frombook', 'tobook']),

            # gen
            (r'^(\d?[a-zöA-ZÖ]+)$', 'FB', ['frombook'])
        ]

        for pattern, pattern_type, keys in patterns:
            match = re.match(pattern, parsed_info['reference'])
            if match:
                parsed_info['type'] = pattern_type
                for i, key in enumerate(keys):
                    value = match.group(i + 1) if i + 1 <= len(match.groups()) else 0
                    # Convert to integers for the relevant keys
                    if key in ['fromchapter', 'tochapter', 'fromverse', 'toverse']:
                        parsed_info[key] = int(value)
                    else:
                        parsed_info[key] = value

                # For 1-chapter books, a little correction might be necessary:
                # They might have given us "2joh3", "3" looking like a chapter. In this case the plausibility checks
                # will not work, so we insert "1" as the chapter
                if parsed_info['type'] in ['FBFC', 'FBFCTC'] \
                    and parsed_info['frombook'] in Books.get_one_chapter_books():

                    # In reality, what looks like the chapter is the verse
                    parsed_info['fromverse'] = int(parsed_info['fromchapter'])

                    # Same if there is a to-verse
                    if parsed_info['type'] == 'FBFCTC':
                        parsed_info['toverse'] = int(parsed_info['tochapter'])

                        # Of course the type needs to be changed, for the return and for internal use
                        pattern_type = 'FBFCFVTV'
                        parsed_info['type'] = pattern_type

                        # The reference must be corrected
                        parsed_info['reference'] = parsed_info['frombook'] + '1.' + str(parsed_info['fromverse']) + '-' + \
                                                   str(parsed_info['toverse'])

                        # There is no more tochapter anymore
                        parsed_info['tochapter'] = 0

                    else:
                        pattern_type = 'FBFCFV'
                        parsed_info['type'] = pattern_type
                        parsed_info['reference'] = parsed_info['frombook'] + '1.' + str(parsed_info['fromverse'])

                    # In both cases, the chapter is 1
                    parsed_info['fromchapter'] = 1


                # Validation checks
                errors = []

                # Hopefully the abbreviation(s) is/are valid. If one of them is not, no further checks make sense
                if not self._biblebooks.is_valid_abbreviation(parsed_info['frombook']):
                    # This makes the reference invalid
                    parsed_info['passed'] = False
                    # Add this information
                    s = f'Ungültige Abkürzung "{parsed_info["frombook"]}".'
                    if not parsed_info['messages']:
                        # There is no other message yet
                        parsed_info['messages'] = s
                    else:
                        # There is a message, we attach ours
                        parsed_info['messages'] = f"{parsed_info['messages']}\n{s}"

                if parsed_info['tobook'] != '':
                    if not Books.is_valid_abbreviation(parsed_info['tobook']):
                        # This makes the reference invalid
                        parsed_info['passed'] = False
                        # Add this information
                        s = f'Ungültige Abkürzung "{parsed_info["tobook"]}".'
                        if not parsed_info['messages']:
                            # There is no other message yet
                            parsed_info['messages'] = s
                        else:
                            # There is a message, we attach ours
                            parsed_info['messages'] = f"{parsed_info['messages']}\n{s}"

                # We can stop here
                if parsed_info['passed'] is False:
                    return parsed_info


                if pattern_type == 'FBFCTC' and int(parsed_info['tochapter']) <= int(parsed_info['fromchapter']):
                    errors.append('Bis-Kapitel muss grösser sein als Von-Kapitel.')
                if pattern_type == 'FBFCFVTCTV' and (int(parsed_info['tochapter']) < int(parsed_info['fromchapter']) or
                                                     (int(parsed_info['tochapter']) == int(
                                                         parsed_info['fromchapter']) and
                                                      int(parsed_info['toverse']) <= int(parsed_info['fromverse']))):
                    errors.append('To chapter and verse must be greater than from chapter and verse.')
                if pattern_type == 'FBFCFVTV' and int(parsed_info['toverse']) <= int(parsed_info['fromverse']):
                    errors.append('Bis-Vers muss grösser sein als Von-Vers.')

                if errors:
                    parsed_info['messages'] = '\n'.join(errors)
                    parsed_info['passed'] = False





                # In a book span the books might be in the wrong order ("ex-gen")
                if pattern_type == 'FBTB':
                    # We made already clear that both abbreviations are valid
                    if Books.get_sort_value(parsed_info['tobook']) <= Books.get_sort_value(parsed_info['frombook']):
                        # This makes the reference invalid
                        parsed_info['passed'] = False

                        s = 'Reihenfolge der Bücher stimmt nicht.'
                        parsed_info['messages'] += f'\n{s}' if parsed_info['messages'] else s

                        # if not parsed_info['messages']:
                        #     # There is no other message yet
                        #     parsed_info['messages'] = s
                        # else:
                        #     # There is a message, we attach ours
                        #     parsed_info['messages'] = f"{parsed_info['messages']}\n{s}"

                # Check if the from-chapter is valid. This is sufficient - a reference of the form
                # gen1-ex7 will hardly ever occur
                c = parsed_info['fromchapter']
                if c != '':
                    ch = self._biblebooks.get_max_chapter(parsed_info['frombook'])
                    if int(c) > ch:
                        parsed_info['passed'] = False
                        s = f'{parsed_info["frombook"]} hat nur {ch} Kapitel'
                        parsed_info['messages'] += f'\n{s}' if parsed_info['messages'] else s


                # See if we have a from-verse
                fv = parsed_info['fromverse']
                if fv != '':
                    # It must not be bigger than the max verse of the chapter
                    maxv = self._biblebooks.get_max_verse(parsed_info['frombook'], parsed_info['fromchapter'])
                    if int(maxv) > maxv:
                        parsed_info['passed'] = False
                        s = f'{parsed_info["frombook"]}{parsed_info["fromchapter"]} hat nur {maxv} Verse'
                        parsed_info['messages'] += f'\n{s}' if parsed_info['messages'] else s

                return parsed_info

        parsed_info['passed'] = False
        parsed_info['messages'] = 'Ungültiges Muster in der Stellenangabe.'
        return parsed_info

import pygments.lexers

import core

class EditorData:
    codehilite_lexers: list[tuple[str, str]]

    def __init__(self):
        self.get_lexer_list()

    def get_lexer_list(self):
        self.codehilite_lexers = [
            ("None", "")
        ]
        for lexer in pygments.lexers.get_all_lexers():
            if (len(lexer[1]) > 0):
                 self.codehilite_lexers.append((lexer[0], lexer[1][0]))
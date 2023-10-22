import pyparsing

from ._ast import Calc, Parentheses
from .mapper import CHAR_TO_AC, PROG_TYPES


def flatten(lists):
    return sum(map(flatten, lists), []) if isinstance(lists, list) else [lists]


class JsonFuck:
    def __init__(self, json_fk: str):
        self.json_fk = json_fk
        self.is_cleaned = False

    def reconstruct_chars(self) -> None:
        for key in sorted(CHAR_TO_AC, key=lambda k: len(CHAR_TO_AC[k]), reverse=True):
            found_result = CHAR_TO_AC.get(key)
            if found_result and found_result in self.json_fk:
                self.json_fk = self.json_fk.replace(found_result, f'"{key}"')

        for key in sorted(PROG_TYPES, key=lambda k: len(PROG_TYPES[k]), reverse=True):
            found_result = PROG_TYPES.get(key)
            if found_result and found_result in self.json_fk:
                self.json_fk = self.json_fk.replace(found_result, key)

        # for key in sorted(CONSTRUCTORS, key=lambda k: len(CONSTRUCTORS[k]), reverse=True):
        #    if CONSTRUCTORS.get(key) in self.json_fk:
        #        self.json_fk = self.json_fk.replace(CONSTRUCTORS.get(key), '{}'.format(key))

    def cleanup(self) -> None:
        if not self.is_cleaned:
            self.json_fk = self.json_fk.replace("!+[]", "1").replace("!![]", "1").replace("[]", "0")
            self.json_fk = self.json_fk.lstrip("+").replace("(+", "(").replace(" ", "")
            self.json_fk = Parentheses().fix(self.json_fk)[0]
        self.is_cleaned = True

    def to_number(self) -> int:
        self.cleanup()

        # Hackery Parser for Math
        stack = []
        bstack = []

        for i in flatten(pyparsing.nestedExpr().parseString(self.json_fk).asList()):
            if i == "+":
                stack.append(bstack)
                bstack = []
                continue
            bstack.append(i)
        stack.append(bstack)

        return int("".join([str(Calc.doMath("".join(i))) for i in stack]))

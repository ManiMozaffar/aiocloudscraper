import operator as op
import re

from aiocloudscraper.interpreters.base import JavaScriptInterpreter

from .fuck.handler import JsonFuck


class NativeInterpreter(JavaScriptInterpreter):
    def eval(self, body, domain):
        self.operators = {"+": op.add, "-": op.sub, "*": op.mul, "/": op.truediv}
        return self._solve_challenge(body, domain)

    def divisor_math(self, payload: str, needle, domain) -> float:
        js_fuck_match = payload.split("/")
        if needle in js_fuck_match[1]:
            expression = re.findall(r"^(.*?)(.)\(function", js_fuck_match[1])[0]

            expression_value = self.operators[expression[1]](
                float(JsonFuck(expression[0]).to_number()),
                float(
                    ord(
                        domain[
                            JsonFuck(
                                js_fuck_match[1][js_fuck_match[1].find('"("+p+")")}') + len('"("+p+")")}') : -2]
                            ).to_number()
                        ]
                    )
                ),
            )
        else:
            expression_value = JsonFuck(js_fuck_match[1]).to_number()

        expression_value = JsonFuck(js_fuck_match[0]).to_number() / float(expression_value)

        return expression_value

    @staticmethod
    def get_kid(body: str):
        k_id_search = re.search(r"\s*k\s*=\s*'(?P<kID>\S+)';", body)
        if not k_id_search:
            raise Exception('There was an issue extracting "kid" from the Cloudflare challenge.')
        try:
            return k_id_search.group("kID")
        except KeyError:
            raise Exception('There was an issue extracting "kID" from the Cloudflare challenge.')

    @staticmethod
    def get_kjs_int(kjs_fuck: re.Match) -> int:
        try:
            kjs_fuck_int = JsonFuck(kjs_fuck.group("kJSFUCK")).to_number()
            return kjs_fuck_int
        except IndexError:
            raise Exception('There was an issue extracting "kJSFUCK" from the Cloudflare challenge.')

    def _solve_challenge(self, body, domain):
        jschl_answer = 0

        jsfuck_challenge = re.search(
            r"setTimeout\(function\(\){\s+var.*?f,\s*(?P<variable>\w+).*?:(?P<init>\S+)};"
            r".*?\('challenge-form'\);.*?;(?P<challenge>.*?a\.value)\s*=\s*\S+\.toFixed\(10\);",
            body,
            re.DOTALL | re.MULTILINE,
        )
        if jsfuck_challenge is None:
            raise Exception('There was an issue extracting "jsfuckChallenge" from the Cloudflare challenge.')

        challenge = jsfuck_challenge.groupdict()
        challenge_str = challenge.get("challenge")
        if challenge_str is None:
            raise Exception('There was an issue extracting "jsfuckChallenge" from the Cloudflare challenge.')

        kjs_fuck = re.search(r"(;|)\s*k.=(?P<kJSFUCK>\S+);", challenge_str, re.S | re.M)
        if kjs_fuck:
            get_kjs_int = self.get_kjs_int(kjs_fuck)
            k_id = self.get_kid(body)
            try:
                r = re.compile(rf'<div id="{k_id}(?P<id>\d+)">\s*(?P<jsfuck>[^<>]*)</div>')
                key_values = {}
                for m in r.finditer(body):
                    key_values[int(m.group("id"))] = m.group("jsfuck")
                challenge["k"] = key_values[get_kjs_int]
            except (AttributeError, IndexError):
                raise Exception('There was an issue extracting "kValues" from the Cloudflare challenge.')

        challenge["challenge"] = re.finditer(
            r"{}.*?([+\-*/])=(.*?);(?=a\.value|{})".format(challenge["variable"], challenge["variable"]),
            challenge["challenge"],
        )

        if "/" in challenge["init"]:
            val = challenge["init"].split("/")
            num1 = JsonFuck(val[0]).to_number()
            num2 = JsonFuck(val[1]).to_number()
            jschl_answer = num1 / float(num2)
        else:
            jschl_answer = JsonFuck(challenge["init"]).to_number()

        for expressionMatch in challenge["challenge"]:
            oper, expression = expressionMatch.groups()

            if "/" in expression:
                expression_value = self.divisor_math(expression, "function(p)", domain)
            else:
                if "Element" in expression:
                    expression_value = self.divisor_math(challenge["k"], '"("+p+")")}', domain)
                else:
                    expression_value = JsonFuck(expression).to_number()

            jschl_answer = self.operators[oper](jschl_answer, expression_value)

        # if not jsfuckChallenge['k'] and '+ t.length' in body:
        #    jschl_answer += len(domain)

        return f"{jschl_answer:.10f}"

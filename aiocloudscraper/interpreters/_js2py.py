# NOTE: this is legacy code, idk what it does lol


import base64
import logging

import js2py

from .base import JavaScriptInterpreter
from .fuck.handler import JsonFuck
from .utilty import template


def atob(s):
    return base64.b64decode(f"{s}").decode("utf-8")


class Js2PyInterpreter(JavaScriptInterpreter):
    def eval(self, body, domain):
        js_payload = template(body, domain)

        if js2py.eval_js("(+(+!+[]+[+!+[]]+(!![]+[])[!+[]+!+[]+!+[]]+[!+[]+!+[]]+[+[]])+[])[+!+[]]") == "1":
            logging.warning(
                "WARNING - Please upgrade your js2py https://github.com/PiotrDabkowski/Js2Py, applying work around for"
                " the meantime."
            )
            js_payload = JsonFuck(js_payload).reconstruct_chars()

        js2py.disable_pyimport()
        context = js2py.EvalJs({"atob": atob})
        result = context.eval(js_payload)
        return result

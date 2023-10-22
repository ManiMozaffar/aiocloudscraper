import ctypes.util
import os
import sys
from ctypes import CDLL, byref, c_size_t, c_void_p, create_string_buffer

from .base import JavaScriptInterpreter
from .utilty import template


class ChackraInterpreter(JavaScriptInterpreter):
    @staticmethod
    def get_chackra_core() -> CDLL:
        chakra_core_lib = None

        # check current working directory.
        for _libraryFile in ["libchackra_core.so", "libchackra_core.dylib", "chackra_core.dll"]:
            if os.path.isfile(os.path.join(os.getcwd(), _libraryFile)):
                chakra_core_lib = os.path.join(os.getcwd(), _libraryFile)
                continue

        if chakra_core_lib is None:
            chakra_core_lib = ctypes.util.find_library("ChakraCore")

            if chakra_core_lib is None:
                raise Exception(
                    "ChakraCore library not found in current path or any of your system library paths, "
                    "please download from https://www.github.com/VeNoMouS/cloudscraper/tree/ChakraCore/, "
                    "or https://github.com/Microsoft/ChakraCore/"
                )

        try:
            chackra_core = CDLL(chakra_core_lib)
        except OSError:
            raise Exception(f"There was an error loading the ChakraCore library {chakra_core_lib}")

        return chackra_core

    def eval(self, body, domain):
        chackra_core = self.get_chackra_core()

        if sys.platform != "win32":
            chackra_core.DllMain(0, 1, 0)
            chackra_core.DllMain(0, 2, 0)

        script = create_string_buffer(template(body, domain).encode("utf-16"))

        runtime = c_void_p()
        chackra_core.JsCreateRuntime(0, 0, byref(runtime))

        context = c_void_p()
        chackra_core.JsCreateContext(runtime, byref(context))
        chackra_core.JsSetCurrentContext(context)

        fname = c_void_p()
        chackra_core.JsCreateString("iuam-challenge.js", len("iuam-challenge.js"), byref(fname))

        scriptSource = c_void_p()
        chackra_core.JsCreateExternalArrayBuffer(script, len(script), 0, 0, byref(scriptSource))

        jsResult = c_void_p()
        chackra_core.JsRun(scriptSource, 0, fname, 0x02, byref(jsResult))

        resultJSString = c_void_p()
        chackra_core.JsConvertValueToString(jsResult, byref(resultJSString))

        stringLength = c_size_t()
        chackra_core.JsCopyString(resultJSString, 0, 0, byref(stringLength))

        resultSTR = create_string_buffer(stringLength.value + 1)
        chackra_core.JsCopyString(resultJSString, byref(resultSTR), stringLength.value + 1, 0)

        chackra_core.JsDisposeRuntime(runtime)

        return float(resultSTR.value)

import abc
from abc import ABC


class JavaScriptInterpreter(ABC):
    @abc.abstractmethod
    def eval(self, js_env, js) -> float:
        ...

    def solve_challenge(self, body, domain):
        try:
            return f"{self.eval(body, domain):.10f}"
        except Exception:
            raise Exception("Error trying to solve Cloudflare IUAM Javascript, they may have changed their technique.")

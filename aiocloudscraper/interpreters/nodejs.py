import base64
import subprocess

from .base import JavaScriptInterpreter
from .utilty import template


class NodeJsInterpreter(JavaScriptInterpreter):
    def eval(self, body, domain):
        try:
            js = (
                'var atob = function(str) {return Buffer.from(str, "base64").toString("binary");};'
                'var challenge = atob("%s");'
                "var context = {atob: atob};"
                'var options = {filename: "iuam-challenge.js", timeout: 4000};'
                'var answer = require("vm").runInNewContext(challenge, context, options);'
                "process.stdout.write(String(answer));"
                % base64.b64encode(template(body, domain).encode("UTF-8")).decode("ascii")
            )

            return subprocess.check_output(["node", "-e", js])

        except OSError as e:
            if e.errno == 2:
                raise OSError(
                    "Missing Node.js runtime. Node is required and must be in the PATH (check with `node -v`).\n\nYour"
                    " Node binary may be called `nodejs` rather than `node`, in which case you may need to run `apt-get"
                    " install nodejs-legacy` on some Debian-based systems.\n\n(Please read the cloudscraper README's"
                    " Dependencies section: https://github.com/VeNoMouS/cloudscraper#dependencies.)"
                )
            raise
        except Exception:
            raise Exception("Error executing Cloudflare IUAM Javascript in nodejs")

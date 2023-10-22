import logging
import re


def template(body, domain) -> str:
    BUG_REPORT = "Cloudflare may have changed their technique, or there may be a bug in the script."

    get_iuam_js = re.search(r"setTimeout\(function\(\){\s+(.*?a\.value\s*=\s*\S+toFixed\(10\);)", body, re.M | re.S)
    if not get_iuam_js:
        raise ValueError(f"Unable to identify Cloudflare IUAM Javascript on website. {BUG_REPORT}")

    js = get_iuam_js.group(1)

    js_env = """String.prototype.italics=function(str) {{return "<i>" + this + "</i>";}};
        var subVars= {{{sub_vars}}};
        var document = {{
            createElement: function () {{
                return {{ firstChild: {{ href: "https://{domain}/" }} }}
            }},
            getElementById: function (str) {{
                return {{"innerHTML": subVars[str]}};
            }}
        }};
    """

    try:
        js = js.replace(r"(setInterval(function(){}, 100),t.match(/https?:\/\//)[0]);", r"t.match(/https?:\/\//)[0];")

        key = re.search(r" k\s*=\s*'(?P<k>\S+)';", body)
        if not key:
            raise Exception("WTF?")
        k = key.group("k")

        r = re.compile(rf'<div id="{k}(?P<id>\d+)">\s*(?P<jsfuck>[^<>]*)</div>')

        sub_vars = ""
        for m in r.finditer(body):
            sub_vars = "{}\n\t\t{}{}: {},\n".format(sub_vars, k, m.group("id"), m.group("jsfuck"))
        sub_vars = sub_vars[:-2]

    except Exception as error:
        logging.error(f"Error extracting Cloudflare IUAM Javascript. {BUG_REPORT}")
        raise Exception from error

    return "{}{}".format(
        re.sub(r"\s{2,}", " ", js_env.format(domain=domain, sub_vars=sub_vars), re.MULTILINE | re.DOTALL), js
    )

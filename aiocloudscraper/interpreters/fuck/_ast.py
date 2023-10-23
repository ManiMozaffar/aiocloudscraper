import ast
import operator as op

_OP_MAP = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Invert: op.neg,
}


class Calc(ast.NodeVisitor):
    def visit_BinOp(self, node):
        return _OP_MAP[type(node.op)](self.visit(node.left), self.visit(node.right))  # type: ignore

    def visit_Num(self, node):
        return node.n

    def visit_Expr(self, node):
        return self.visit(node.value)

    @classmethod
    def doMath(cls, expression):
        tree = ast.parse(expression)
        calc = cls()
        return calc.visit(tree.body[0])


class Parentheses:
    def fix(self, s):
        res = []
        self.visited = {s}
        self.dfs(s, self.invalid(s), res)
        return res

    def dfs(self, s, n, res):
        if n == 0:
            res.append(s)
            return
        for i in range(len(s)):
            if s[i] in ["(", ")"]:
                s_new = s[:i] + s[i + 1 :]
                if s_new not in self.visited and self.invalid(s_new) < n:
                    self.visited.add(s_new)
                    self.dfs(s_new, self.invalid(s_new), res)

    def invalid(self, s):
        plus = minus = 0
        memo = {"(": 1, ")": -1}
        for c in s:
            plus += memo.get(c, 0)
            minus += 1 if plus < 0 else 0
            plus = max(0, plus)
        return plus + minus

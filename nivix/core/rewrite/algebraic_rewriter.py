# Nivix Algebraic Rewriter v6.3
# Expression rewrite engine for symbolic transformations

from typing import Any, List, Optional, Dict
from dataclasses import dataclass, field
from enum import Enum

class ExprType(Enum):
    """Expression node types."""
    LITERAL = "literal"
    VARIABLE = "variable"
    BINARY_OP = "binary_op"
    POWER = "power"

@dataclass
class RewriteRule:
    """Single algebraic rewrite rule."""
    name: str
    pattern: str
    template: str
    
    def matches(self, node_type: str, value: Any) -> bool:
        return node_type == self.pattern

class AlgebraicRewriter:
    """
    Rewrite engine for symbolic transformations.
    
    Transforms expressions for animation:
        (a+b)^2 → a^2 + 2ab + b^2
        a^2 - b^2 → (a+b)(a-b)
        (a+b)c → ac + bc
    
    Enables animated derivation sequences.
    """
    
    def __init__(self):
        self.rules: List[RewriteRule] = []
        self._register_rules()
    
    def _register_rules(self):
        """Register algebraic transformation rules."""
        self.rules = [
            RewriteRule("square_of_sum", "power_with_add", "expand"),
            RewriteRule("square_of_diff", "power_with_sub", "expand"),
            RewriteRule("diff_of_squares", "binary_sub_power", "factor"),
            RewriteRule("distribute", "binary_mul_add", "distribute"),
        ]
    
    def rewrite(self, ast: dict) -> dict:
        """
        Apply rewrite rules to AST.
        
        Returns transformed expression ready for animation planning.
        """
        node_type = ast.get("type", "")
        value = ast.get("value", "")
        children = ast.get("children", [])
        
        if node_type == "power" and value == "^":
            return self._rewrite_power(ast, children)
        
        elif node_type == "binary_op":
            return self._rewrite_binary(ast, value, children)
        
        return ast
    
    def _rewrite_power(self, ast: dict, children: List[dict]) -> dict:
        """Rewrite power expressions."""
        if len(children) < 2:
            return ast
        
        base = children[0]
        exponent = children[1]
        
        if exponent.get("value") == "2" and base.get("type") == "binary_op":
            base_op = base.get("value", "")
            
            if base_op == "+":
                return self._expand_square_of_sum(base, "a^2 + 2ab + b^2")
            elif base_op == "-":
                return self._expand_square_of_diff(base, "a^2 - 2ab + b^2")
        
        return ast
    
    def _expand_square_of_sum(self, base: dict, formula: str) -> dict:
        """Expand (a+b)^2 = a^2 + 2ab + b^2"""
        children = base.get("children", [])
        if len(children) < 2:
            return {}
        
        a = children[0]
        b = children[1]
        
        a_val = a.get("value", "a")
        b_val = b.get("value", "b")
        
        return {
            "type": "expanded",
            "formula": formula,
            "terms": [
                {"type": "power", "value": "^", "children": [a, {"type": "literal", "value": "2"}]},
                {"type": "binary_op", "value": "*", "children": [
                    {"type": "literal", "value": "2"},
                    a,
                    b
                ]},
                {"type": "power", "value": "^", "children": [b, {"type": "literal", "value": "2"}]}
            ],
            "animation_steps": [
                {"step": 1, "action": "show", "target": f"{a_val}^2"},
                {"step": 2, "action": "show", "target": f"2{a_val}{b_val}"},
                {"step": 3, "action": "show", "target": f"{b_val}^2"},
                {"step": 4, "action": "combine", "target": f"{a_val}^2 + 2{a_val}{b_val} + {b_val}^2"}
            ]
        }
    
    def _expand_square_of_diff(self, base: dict, formula: str) -> dict:
        """Expand (a-b)^2 = a^2 - 2ab + b^2"""
        children = base.get("children", [])
        if len(children) < 2:
            return {}
        
        a = children[0]
        b = children[1]
        
        a_val = a.get("value", "a")
        b_val = b.get("value", "b")
        
        return {
            "type": "expanded",
            "formula": formula,
            "terms": [
                {"type": "power", "value": "^", "children": [a, {"type": "literal", "value": "2"}]},
                {"type": "binary_op", "value": "*", "children": [
                    {"type": "literal", "value": "2"},
                    a,
                    b
                ]},
                {"type": "power", "value": "^", "children": [b, {"type": "literal", "value": "2"}]}
            ],
            "animation_steps": [
                {"step": 1, "action": "show", "target": f"{a_val}^2"},
                {"step": 2, "action": "fade_out", "target": f"2{a_val}{b_val}"},
                {"step": 3, "action": "show", "target": f"{b_val}^2"}
            ]
        }
    
    def _rewrite_binary(self, ast: dict, op: str, children: List[dict]) -> dict:
        """Rewrite binary operations."""
        if op == "*":
            return self._rewrite_multiplication(ast, children)
        return ast
    
    def _rewrite_multiplication(self, ast: dict, children: List[dict]) -> dict:
        """Rewrite multiplication (distribution)."""
        if len(children) != 2:
            return ast
        
        left = children[0]
        right = children[1]
        
        left_type = left.get("type", "")
        right_type = right.get("type", "")
        
        if left_type == "binary_op" and right_type != "binary_op":
            return self._distribute(left, right)
        
        return ast
    
    def _distribute(self, sum_expr: dict, factor: dict) -> dict:
        """a(b+c) = ab + ac"""
        terms = sum_expr.get("children", [])
        if len(terms) != 2:
            return {}
        
        a = factor
        b = terms[0]
        c = terms[1]
        
        return {
            "type": "distributed",
            "formula": f"{a.get('value', 'a')}({b.get('value', 'b')}+{c.get('value', 'c')})",
            "terms": [
                {"type": "binary_op", "value": "*", "children": [a, b]},
                {"type": "binary_op", "value": "*", "children": [a, c]},
            ],
            "animation_steps": [
                {"step": 1, "action": "show", "target": f"{a.get('value', 'a')}{b.get('value', 'b')}"},
                {"step": 2, "action": "show", "target": f"{a.get('value', 'a')}{c.get('value', 'c')}"}
            ]
        }
    
    def apply_sequence(self, ast: dict) -> List[dict]:
        """
        Generate animation step sequence from expression.
        
        Returns list of animation steps for CIR.
        """
        rewritten = self.rewrite(ast)
        
        if "animation_steps" in rewritten:
            return rewritten["animation_steps"]
        
        return [{"step": 1, "action": "show", "target": "result"}]


def rewrite_expression(ast: dict) -> dict:
    """Convenience function."""
    return AlgebraicRewriter().rewrite(ast)
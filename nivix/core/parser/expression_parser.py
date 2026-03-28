# Nivix Expression Parser v6.2
# AST Parser for mathematical expressions

from typing import Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum

class ExprType(Enum):
    """Expression node types."""
    LITERAL = "literal"
    VARIABLE = "variable"
    BINARY_OP = "binary_op"
    UNARY_OP = "unary_op"
    FUNCTION = "function"
    POWER = "power"

class BinaryOp(Enum):
    """Binary operators."""
    ADD = "+"
    SUB = "-"
    MUL = "*"
    DIV = "/"
    POW = "^"
    MOD = "%"

class ExpressionNode:
    """Base expression node."""
    
    def __init__(self, expr_type: ExprType, value: Any = None):
        self.expr_type = expr_type
        self.value = value
        self.children: List["ExpressionNode"] = []
    
    def add_child(self, child: "ExpressionNode") -> None:
        self.children.append(child)
    
    def to_dict(self) -> dict:
        return {
            "type": self.expr_type.value,
            "value": self.value,
            "children": [c.to_dict() for c in self.children]
        }

@dataclass
class LiteralNode(ExpressionNode):
    """Literal value (number, string)."""
    def __init__(self, value: Any):
        super().__init__(ExprType.LITERAL, value)

@dataclass
class VariableNode(ExpressionNode):
    """Variable symbol."""
    def __init__(self, name: str):
        super().__init__(ExprType.VARIABLE, name)

@dataclass
class BinaryExprNode(ExpressionNode):
    """Binary expression (a op b)."""
    def __init__(self, operator: BinaryOp, left: ExpressionNode, right: ExpressionNode):
        super().__init__(ExprType.BINARY_OP, operator.value)
        self.add_child(left)
        self.add_child(right)

@dataclass  
class PowerNode(ExpressionNode):
    """Power expression (a^b)."""
    def __init__(self, base: ExpressionNode, exponent: ExpressionNode):
        super().__init__(ExprType.POWER, "^")
        self.add_child(base)
        self.add_child(exponent)


class ExpressionParser:
    """
    Parses mathematical expressions into AST.
    
    Input:  "3/4"
    Output: Division(Literal(3), Literal(4))
    
    Supported:
        - a/b (division)
        - a*b (multiplication)
        - a+b (addition)
        - a-b (subtraction)
        - a^b (power)
        - (a+b) grouped expressions
    """
    
    def __init__(self):
        self.pos = 0
        self.expr = ""
    
    def parse(self, expression: str) -> ExpressionNode:
        """Parse expression string into AST."""
        self.expr = expression.replace(" ", "").replace("=", "").strip()
        self.pos = 0
        
        if not self.expr:
            return LiteralNode("")
        
        return self._parse_add()
    
    def _peek(self) -> str:
        """Peek at current character."""
        if self.pos < len(self.expr):
            return self.expr[self.pos]
        return ""
    
    def _consume(self) -> str:
        """Consume and advance."""
        char = self._peek()
        self.pos += 1
        return char
    
    def _parse_add(self) -> ExpressionNode:
        """Parse addition/subtraction (lowest precedence)."""
        left = self._parse_mul()
        
        while self._peek() in ["+", "-"]:
            op = self._consume()
            right = self._parse_mul()
            if op == "+":
                left = BinaryExprNode(BinaryOp.ADD, left, right)
            else:
                left = BinaryExprNode(BinaryOp.SUB, left, right)
        
        return left
    
    def _parse_mul(self) -> ExpressionNode:
        """Parse multiplication/division."""
        left = self._parse_power()
        
        while self._peek() in ["*", "/"]:
            op = self._consume()
            right = self._parse_power()
            if op == "*":
                left = BinaryExprNode(BinaryOp.MUL, left, right)
            else:
                left = BinaryExprNode(BinaryOp.DIV, left, right)
        
        return left
    
    def _parse_power(self) -> ExpressionNode:
        """Parse power/exponent."""
        left = self._parse_unary()
        
        if self._peek() == "^":
            self._consume()
            right = self._parse_unary()
            return PowerNode(left, right)
        
        return left
    
    def _parse_unary(self) -> ExpressionNode:
        """Parse unary operators."""
        if self._peek() == "-":
            self._consume()
            child = self._parse_unary()
            return BinaryExprNode(BinaryOp.SUB, LiteralNode(0), child)
        
        return self._parse_primary()
    
    def _parse_primary(self) -> ExpressionNode:
        """Parse primary values (numbers, variables, grouped)."""
        char = self._peek()
        
        # Grouped expression
        if char == "(":
            self._consume()
            node = self._parse_add()
            if self._peek() == ")":
                self._consume()
            return node
        
        # Number
        if char.isdigit() or char == ".":
            num = ""
            while self._peek().isdigit() or self._peek() == ".":
                num += self._consume()
            return LiteralNode(num)
        
        # Variable (letter)
        if char.isalpha():
            name = ""
            while self._peek().isalnum():
                name += self._consume()
            return VariableNode(name)
        
        # Fallback
        return LiteralNode(char)


def parse_expression(expr: str) -> ExpressionNode:
    """Convenience function."""
    return ExpressionParser().parse(expr)


def ast_to_dependency_graph(ast: ExpressionNode) -> dict:
    """Convert AST to dependency graph structure."""
    graph = {}
    node_id = 0
    
    def traverse(node: ExpressionNode, parent_id: Optional[str] = None) -> str:
        nonlocal node_id
        
        if node.expr_type == ExprType.LITERAL:
            nid = f"literal_{node.value}"
            graph[nid] = {"type": "literal", "value": node.value, "depends_on": []}
            return nid
        
        elif node.expr_type == ExprType.VARIABLE:
            nid = f"var_{node.value}"
            graph[nid] = {"type": "variable", "value": node.value, "depends_on": []}
            return nid
        
        elif node.expr_type == ExprType.BINARY_OP or node.expr_type == ExprType.POWER:
            op_name = node.value
            nid = f"op_{node_id}"
            node_id += 1
            
            deps = []
            for child in node.children:
                child_id = traverse(child, nid)
                deps.append(child_id)
            
            graph[nid] = {"type": "operator", "value": op_name, "depends_on": deps}
            return nid
        
        return f"node_{node_id}"
    
    traverse(ast)
    return graph
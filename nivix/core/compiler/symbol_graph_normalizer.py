# Nivix Symbol Graph Normalizer v6.5
# Canonicalizes symbolic expressions for generalization

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

class SymbolType(Enum):
    """Canonical symbol types."""
    VARIABLE = "variable"
    TERM = "term"
    OPERATOR = "operator"
    EXPRESSION = "expression"
    CONSTANT = "constant"

@dataclass
class Symbol:
    """Canonical symbol representation."""
    id: str
    symbol_type: SymbolType
    value: Any = None
    base: Optional[str] = None
    exponent: Optional[Any] = None
    children: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)

class SymbolGraphNormalizer:
    """
    Normalizes symbol graph to canonical form.
    
    Before normalization:
        apow2 -> id="apow2", label="a^2"
    
    After normalization:
        {
            id: "apow2",
            type: "term",
            base: "a",
            exponent: 2,
            properties: {coefficient: 1, degree: 2}
        }
    
    Enables hierarchical camera zooms:
        expression -> term -> symbol
    """
    
    def __init__(self):
        self.symbols: Dict[str, Symbol] = {}
        self.next_id = 0
    
    def normalize_cir(self, cir: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize CIR nodes to canonical symbol graph."""
        print("--- [NORMALIZER] Canonicalizing symbol graph ---")
        
        self.symbols = {}
        
        nodes = cir.get("nodes", [])
        
        for node in nodes:
            self._normalize_node(node)
        
        for node in nodes:
            self._infer_relationships(node, nodes)
        
        normalized_cir = cir.copy()
        normalized_cir["_canonical_symbols"] = self._serialize()
        normalized_cir["_symbol_index"] = self._build_index()
        
        print(f"--- [NORMALIZER] Normalized {len(self.symbols)} symbols")
        
        return normalized_cir
    
    def _normalize_node(self, node: Dict[str, Any]) -> None:
        """Normalize single node to canonical form."""
        node_id = node.get("id", "")
        label = node.get("label", "")
        
        sym = Symbol(
            id=node_id,
            symbol_type=SymbolType.TERM,
            value=label
        )
        
        if label:
            if "^" in label:
                parts = label.split("^")
                sym.base = parts[0]
                sym.exponent = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else parts[1]
                sym.properties["degree"] = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
            
            elif any(op in label for op in ["+", "-", "*", "/"]):
                sym.symbol_type = SymbolType.EXPRESSION
                sym.properties["operator"] = self._detect_operator(label)
        
        self.symbols[node_id] = sym
    
    def _detect_operator(self, label: str) -> str:
        """Detect primary operator in expression."""
        if "+" in label:
            return "+"
        elif "-" in label and label.count("-") == 1:
            return "-"
        elif "*" in label:
            return "*"
        elif "/" in label:
            return "/"
        return "unknown"
    
    def _infer_relationships(self, node: Dict[str, Any], all_nodes: List[Dict]) -> None:
        """Infer parent-child relationships."""
        node_id = node.get("id", "")
        label = node.get("label", "")
        
        if node_id not in self.symbols:
            return
        
        sym = self.symbols[node_id]
        
        if "^" in label:
            base = label.split("^")[0]
            for n in all_nodes:
                nlabel = n.get("label", "")
                if nlabel == base:
                    sym.children.append(n.get("id", ""))
                    break
        
        elif any(op in label for op in ["+", "-"]):
            tokens = label.replace("+", " ").replace("-", " ").split()
            for token in tokens:
                token = token.strip()
                if token and not token.isdigit():
                    for n in all_nodes:
                        nlabel = n.get("label", "")
                        if token in nlabel:
                            sym.children.append(n.get("id", ""))
                            break
    
    def _serialize(self) -> Dict[str, Any]:
        """Serialize normalized symbols."""
        return {
            sid: {
                "type": s.symbol_type.value,
                "value": s.value,
                "base": s.base,
                "exponent": s.exponent,
                "children": s.children,
                "properties": s.properties
            }
            for sid, s in self.symbols.items()
        }
    
    def _build_index(self) -> Dict[str, List[str]]:
        """Build index by symbol type."""
        index = {
            "variables": [],
            "terms": [],
            "expressions": []
        }
        
        for sid, sym in self.symbols.items():
            if sym.symbol_type == SymbolType.VARIABLE:
                index["variables"].append(sid)
            elif sym.symbol_type == SymbolType.TERM:
                index["terms"].append(sid)
            elif sym.symbol_type == SymbolType.EXPRESSION:
                index["expressions"].append(sid)
        
        return index
    
    def get_camera_targets(self) -> List[Dict[str, Any]]:
        """Generate hierarchical camera targets from normalized graph."""
        targets = []
        
        for sid, sym in self.symbols.items():
            if sym.symbol_type == SymbolType.TERM and sym.base:
                targets.append({
                    "target": sid,
                    "path": ["expression", "term", f"symbol:{sym.base}"],
                    "zoom": sym.properties.get("degree", 1) * 0.3 + 1.0
                })
        
        return targets


def normalize_cir(cir: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function."""
    return SymbolGraphNormalizer().normalize_cir(cir)
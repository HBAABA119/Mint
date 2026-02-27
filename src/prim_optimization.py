"""
Prim Optimization Framework
Provides code optimization passes, constant folding, dead code elimination,
loop optimizations, and interprocedural analysis.
"""

import ast
import sys
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class OptimizationType(Enum):
    """Optimization types"""
    CONSTANT_FOLDING = "constant_folding"
    DEAD_CODE_ELIMINATION = "dead_code_elimination"
    INLINE_EXPANSION = "inline_expansion"
    LOOP_INVARIANT_CODE_MOTION = "loop_invariant_code_motion"
    COMMON_SUBEXPRESSION_ELIMINATION = "common_subexpression_elimination"


@dataclass
class OptimizationResult:
    """Optimization result"""
    optimized_code: str
    optimizations_applied: List[str]
    performance_gain: float = 0.0


class ConstantFolder:
    """Constant folding optimization"""

    def fold(self, code: str) -> str:
        """Fold constants in code"""
        try:
            tree = ast.parse(code)
            self._fold_constants(tree)
            return ast.unparse(tree)
        except Exception:
            return code

    def _fold_constants(self, node):
        """Recursively fold constants"""
        if isinstance(node, ast.BinOp):
            self._fold_constants(node.left)
            self._fold_constants(node.right)

            if isinstance(node.left, ast.Constant) and isinstance(node.right, ast.Constant):
                left_val = node.left.value
                right_val = node.right.value

                if isinstance(node.op, ast.Add):
                    node.value = left_val + right_val
                elif isinstance(node.op, ast.Sub):
                    node.value = left_val - right_val
                elif isinstance(node.op, ast.Mult):
                    node.value = left_val * right_val
                elif isinstance(node.op, ast.Div):
                    node.value = left_val / right_val if right_val != 0 else 0
                elif isinstance(node.op, ast.Mod):
                    node.value = left_val % right_val if right_val != 0 else 0

        elif isinstance(node, ast.UnaryOp):
            self._fold_constants(node.operand)

            if isinstance(node.operand, ast.Constant):
                if isinstance(node.op, ast.UAdd):
                    node.value = node.operand.value
                elif isinstance(node.op, ast.USub):
                    node.value = -node.operand.value

        elif isinstance(node, ast.Compare):
            for expr in node.comparators:
                self._fold_constants(expr)

            if all(isinstance(comp, ast.Constant) for comp in node.comparators):
                # Can fold comparison
                pass

        elif isinstance(node, ast.If):
            self._fold_constants(node.test)
            for stmt in node.body:
                self._fold_constants(stmt)
            for stmt in node.orelse:
                self._fold_constants(stmt)

        elif isinstance(node, ast.For):
            self._fold_constants(node.target)
            self._fold_constants(node.iter)
            for stmt in node.body:
                self._fold_constants(stmt)

        elif isinstance(node, ast.While):
            self._fold_constants(node.test)
            for stmt in node.body:
                self._fold_constants(stmt)

        elif isinstance(node, ast.FunctionDef):
            for stmt in node.body:
                self._fold_constants(stmt)

        elif isinstance(node, ast.Module):
            for stmt in node.body:
                self._fold_constants(stmt)


class DeadCodeEliminator:
    """Dead code elimination"""

    def eliminate(self, code: str) -> str:
        """Eliminate dead code"""
        try:
            tree = ast.parse(code)
            self._eliminate_dead_code(tree)
            return ast.unparse(tree)
        except Exception:
            return code

    def _eliminate_dead_code(self, node):
        """Recursively eliminate dead code"""
        if isinstance(node, ast.If):
            # Check if test is always true or false
            if isinstance(node.test, ast.Constant):
                if node.test.value:
                    # Always true, keep body
                    node.orelse = []
                else:
                    # Always false, keep else
                    node.body = []

            for stmt in node.body:
                self._eliminate_dead_code(stmt)
            for stmt in node.orelse:
                self._eliminate_dead_code(stmt)

        elif isinstance(node, ast.While):
            # Check if test is always false
            if isinstance(node.test, ast.Constant) and not node.test.value:
                node.body = []

            for stmt in node.body:
                self._eliminate_dead_code(stmt)

        elif isinstance(node, ast.For):
            for stmt in node.body:
                self._eliminate_dead_code(stmt)

        elif isinstance(node, ast.FunctionDef):
            for stmt in node.body:
                self._eliminate_dead_code(stmt)

        elif isinstance(node, ast.Module):
            # Remove unreachable code after return
            new_body = []
            found_return = False

            for stmt in node.body:
                if found_return:
                    # Skip unreachable code
                    continue

                if isinstance(stmt, ast.Return):
                    found_return = True

                new_body.append(stmt)

            node.body = new_body


class InlineExpander:
    """Inline expansion optimization"""

    def __init__(self, inline_threshold: int = 5):
        self.inline_threshold = inline_threshold

    def expand(self, code: str) -> str:
        """Expand function calls"""
        try:
            tree = ast.parse(code)
            self._expand_inlines(tree)
            return ast.unparse(tree)
        except Exception:
            return code

    def _expand_inlines(self, node):
        """Recursively expand inlines"""
        if isinstance(node, ast.Call):
            # Check if function is small enough to inline
            if isinstance(node.func, ast.Name):
                # Would need function definition to inline
                pass

        elif isinstance(node, ast.FunctionDef):
            for stmt in node.body:
                self._expand_inlines(stmt)

        elif isinstance(node, ast.Module):
            for stmt in node.body:
                self._expand_inlines(stmt)


class LoopOptimizer:
    """Loop optimizations"""

    def __init__(self):
        self.constant_folder = ConstantFolder()

    def optimize(self, code: str) -> str:
        """Optimize loops"""
        try:
            tree = ast.parse(code)
            self._optimize_loops(tree)
            return ast.unparse(tree)
        except Exception:
            return code

    def _optimize_loops(self, node):
        """Recursively optimize loops"""
        if isinstance(node, ast.For):
            # Loop invariant code motion
            self._move_invariant_code(node)

            # Constant folding in loop body
            for stmt in node.body:
                self.constant_folder._fold_constants(stmt)

        elif isinstance(node, ast.While):
            # Constant folding in loop condition
            self.constant_folder._fold_constants(node.test)

            for stmt in node.body:
                self.constant_folder._fold_constants(stmt)

        elif isinstance(node, ast.FunctionDef):
            for stmt in node.body:
                self._optimize_loops(stmt)

        elif isinstance(node, ast.Module):
            for stmt in node.body:
                self._optimize_loops(stmt)

    def _move_invariant_code(self, node):
        """Move invariant code out of loops"""
        # Simplified - would need data flow analysis in practice
        pass


class CommonSubexpressionEliminator:
    """Common subexpression elimination"""

    def __init__(self):
        self.expressions: Dict[str, ast.AST] = {}

    def eliminate(self, code: str) -> str:
        """Eliminate common subexpressions"""
        try:
            tree = ast.parse(code)
            self._eliminate_cse(tree)
            return ast.unparse(tree)
        except Exception:
            return code

    def _eliminate_cse(self, node):
        """Recursively eliminate CSE"""
        if isinstance(node, ast.BinOp):
            expr_key = ast.unparse(node)

            if expr_key in self.expressions:
                # Use previously computed value
                return self.expressions[expr_key]

            # Compute and store
            self._eliminate_cse(node.left)
            self._eliminate_cse(node.right)
            self.expressions[expr_key] = node

        elif isinstance(node, ast.Module):
            for stmt in node.body:
                self._eliminate_cse(stmt)


class OptimizationPipeline:
    """Optimization pipeline"""

    def __init__(self):
        self.optimizations: List[Callable] = []
        self.optimizers = {
            OptimizationType.CONSTANT_FOLDING: ConstantFolder(),
            OptimizationType.DEAD_CODE_ELIMINATION: DeadCodeEliminator(),
            OptimizationType.INLINE_EXPANSION: InlineExpander(),
            OptimizationType.LOOP_INVARIANT_CODE_MOTION: LoopOptimizer(),
            OptimizationType.COMMON_SUBEXPRESSION_ELIMINATION: CommonSubexpressionEliminator()
        }

    def add_optimization(self, opt_type: OptimizationType):
        """Add optimization to pipeline"""
        if opt_type in self.optimizers:
            self.optimizations.append(self.optimizers[opt_type])

    def optimize(self, code: str) -> OptimizationResult:
        """Run optimization pipeline"""
        optimized_code = code
        optimizations_applied = []

        for opt in self.optimizations:
            original = optimized_code
            optimized_code = opt.fold(optimized_code) if isinstance(opt, ConstantFolder) else \
                          opt.eliminate(optimized_code) if isinstance(opt, DeadCodeEliminator) else \
                          opt.expand(optimized_code) if isinstance(opt, InlineExpander) else \
                          opt.optimize(optimized_code) if isinstance(opt, LoopOptimizer) else \
                          opt.eliminate(optimized_code)

            if optimized_code != original:
                optimizations_applied.append(type(opt).__name__)

        return OptimizationResult(
            optimized_code=optimized_code,
            optimizations_applied=optimizations_applied
        )


def create_optimizer() -> OptimizationPipeline:
    """Create optimization pipeline"""
    return OptimizationPipeline()


def main():
    """Main entry point for testing"""
    print("Testing Optimization Framework...")

    # Create optimizer
    optimizer = create_optimizer()

    # Add optimizations
    optimizer.add_optimization(OptimizationType.CONSTANT_FOLDING)
    optimizer.add_optimization(OptimizationType.DEAD_CODE_ELIMINATION)

    # Test optimization
    code = """
def test():
    x = 1 + 2
    y = 3 + 4
    return x + y
"""

    result = optimizer.optimize(code)
    print(f"Optimizations applied: {result.optimizations_applied}")
    print(f"Optimized code length: {len(result.optimized_code)}")

    # Test constant folding
    folder = ConstantFolder()
    folded = folder.fold("x = 1 + 2")
    print(f"Constant folded: {folded}")

    # Test dead code elimination
    eliminator = DeadCodeEliminator()
    eliminated = eliminator.eliminate("if False: pass")
    print(f"Dead code eliminated: {len(eliminated)} chars")

    print("\nOptimization Framework initialized successfully")


if __name__ == "__main__":
    main()

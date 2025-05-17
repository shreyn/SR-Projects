import math

class Node: #abstract
    def evaluate(self, variable_vals):
        return 
    def __repr__(self):
        return
    
class ConstantNode(Node):
    def __init__(self, val):
        self.val = float(val)
    def evaluate(self, variable_vals):
        return self.val
    def __repr__(self):
        return str(self.val)
    

class VariableNode(Node):
    def __init__(self, name):
        self.name = name
    def evaluate(self, variable_vals):
        return variable_vals[self.name]
    def __repr__(self):
        return str(self.name)

operator_arity = {
    '+': 2, '-': 2, '*': 2, '/': 2, '^': 2, 
    'sin': 1, 'cos': 1, 'exp': 1, 'log': 1
}


class OperatorNode(Node):
    def __init__(self, operator, children):
        self.operator = operator
        self.children = children

    def evaluate(self, variable_vals):
        try:
            evaluated_children = [child.evaluate(variable_vals) for child in self.children]

            if self.operator == '+':
                result = evaluated_children[0] + evaluated_children[1]
            elif self.operator == '-':
                result = evaluated_children[0] - evaluated_children[1]
            elif self.operator == '*':
                result = evaluated_children[0] * evaluated_children[1]
            elif self.operator == '/':
                denominator = evaluated_children[1]
                result = float('inf') if abs(denominator) < 1e-6 else evaluated_children[0] / denominator
            elif self.operator == 'sin':
                result = math.sin(evaluated_children[0])
            elif self.operator == 'cos':
                result = math.cos(evaluated_children[0])
            elif self.operator == 'exp':
                x = evaluated_children[0]
                result = math.exp(x) if x < 100 else float('inf')
            elif self.operator == 'log':
                x = evaluated_children[0]
                result = float('-inf') if x <= 0 else math.log(x)
            # elif self.operator == 'sqrt':
            #     x = evaluated_children[0]
            #     result = float('inf') if x < 0 else math.sqrt(x)
            # elif self.operator == 'abs':
            #     result = abs(evaluated_children[0])
            elif self.operator == '^':
                base, exp = evaluated_children
                if abs(base) > 1e3 or abs(exp) > 10:
                    result = float('inf')
                else:
                    result = base ** exp
            # elif self.operator == 'max':
            #     result = max(evaluated_children[0], evaluated_children[1])
            # elif self.operator == 'min':
            #     result = min(evaluated_children[0], evaluated_children[1])
            else:
                raise ValueError(f"Unknown operator: {self.operator}")
        except Exception:
            return float('inf')

        # Final safety check
        if isinstance(result, complex) or math.isnan(result) or math.isinf(result):
            return float('inf')
        return max(min(result, 1e6), -1e6)
        
    
    def __repr__(self):
        if len(self.children) == 1:
            return f"{self.operator}({self.children[0]})"
        elif len(self.children) >= 2:
            return f"({f' {self.operator} '.join(map(str, self.children))})"
        else:
            raise ValueError("OperatorNode must have at least one child")

   
def tree_size(tree):
        if isinstance(tree, OperatorNode):
            return 1 + sum(tree_size(child) for child in tree.children)
        else:
            return 1  # leaf node (constant or variable)



# x = VariableNode('x')   
# c = ConstantNode(5)
# oper = OperatorNode('^', [x,c])
# print(oper)

# newOp = OperatorNode('sin', [oper])
# print(newOp)

# y = VariableNode('y')
# print(OperatorNode('*', [oper, y]))

## Testing more functions
# x = VariableNode('x')
# expr = OperatorNode('log', [x])
# print(expr, '=>', expr.evaluate({'x': math.e}))

# expr = OperatorNode('sqrt', [ConstantNode(9)])
# print(expr, '=>', expr.evaluate({}))

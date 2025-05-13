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
    

class OperatorNode(Node):
    def __init__(self, operator, children):
        self.operator = operator
        self.children = children

    def evaluate(self, variable_vals):
        evaluated_children = [child.evaluate(variable_vals) for child in self.children]

        if self.operator == '+':
            return evaluated_children[0] + evaluated_children[1]
        elif self.operator == '-':
            return evaluated_children[0] - evaluated_children[1]
        elif self.operator == '*':
            return evaluated_children[0] * evaluated_children[1]
        elif self.operator == '/':
            denominator = evaluated_children[1]
            return float('inf') if abs(denominator) < 1e-6 else evaluated_children[0]/denominator
        elif self.operator == 'sin':
            return math.sin(evaluated_children[0])
        else:
            raise ValueError(f"Unknown operator: {self.operator}")
    
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
# oper = OperatorNode('+', [x,c])
# print(oper)

# newOp = OperatorNode('sin', [oper])
# print(newOp)

# y = VariableNode('y')
# print(OperatorNode('*', [oper, y]))

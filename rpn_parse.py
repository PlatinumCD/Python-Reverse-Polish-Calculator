"""
Postfix, a.k.a. Reverse Polish Notation (RPN) parser
for a symbolic calculator.  Produces 
Expr objects. 

Author: Initial version by M Young
"""
from typing import List
import expr
import syntax
import lexer
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class InputError(Exception):
    """Raised when we can't parse the input"""
    pass


def parse(s: str) -> expr.Expr:
    """Parse s, which should be a sequence of 
    blank-separated tokens in RPN, into an Expr
    object.   Example: parse('3 4 * x +') => 
    Plus(Times(Const(3), Const(4)), Var('x'))
    """
    stack: List[expr.Expr] = [ ] # Stack List
    stream = lexer.Token_Stream(s) # called stream = Gets all Tokens in form [num/token, category name, category call]
    while stream.has_more(): # while a stream is len > 0
        token = stream.take() # token = first token from stream
        if token.kind == syntax.ASSIGN: # if token has an assign (=) sign
            if len(stack) < 2: #Fail if not enough num/oper in token
                raise InputError("Insufficient operands for {}".format(token))
            right = stack.pop() # Get num/var on far right
            left = stack.pop() # Get num/var after far right
            op_class = token.clazz # Get function for (=) assign
            if not isinstance(right, expr.Var): # Right must be var for assign
                raise InputError("First operand of assignment must be" +
                                 " a variable, not {}".format(right))
            node = op_class(left, right) # Assign left to var-right
            stack.append(node)  # Add back into stack
        elif token.kind == syntax.BINOP: 
            if len(stack) < 2:
                raise InputError("Insufficient operands for {}".format(token))
            right = stack.pop() #Last element in stack
            left = stack.pop() #Next element in stack
            op_class = token.clazz # Class of BinOp
            node = op_class(left, right)#use opclass on left and right
            stack.append(node)
        elif token.kind == syntax.UNOP:
            if len(stack) < 1:
                raise InputError("Insufficient operands for {}".format(token))
            left = stack.pop()
            op_class = token.clazz
            node = op_class(left)
            stack.append(node)
        elif token.kind in [syntax.CONST, syntax.IDENT]:
            leaf_class = token.clazz
            node = leaf_class(token.value)
            stack.append(node)
    if len(stack) > 1:
        raise InputError("Unbalanced expression (too many operands)")
    if len(stack) == 0:
        raise InputError("Empty expression")
    return stack[0]


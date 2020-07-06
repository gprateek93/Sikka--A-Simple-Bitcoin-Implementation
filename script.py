from opcodes import is_op, opcode2method

# expects a stack from the caller.
def execute_script(script, transaction, index):
	stack = []
	for word in script:
		if type(word) == str and is_op(word):
			# get function and execute
			stack = opcode2method[word](stack) if word !='OP_CHECKSIG' else opcode2method[word](stack, transaction, index)
		else:
			stack.append(word)
		if stack == False:
			return False
	return stack



if __name__ == "__main__":
	
	s = ['hashahs', 'OP_DUP', 'OP_DUP', 'OP_HASH160']
	stack = []
	stack = execute_script(s, None, None)
	print(stack)









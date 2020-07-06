from opcodes import is_op, opcode2method

# expects a stack from the caller.
def execute_script(script, transaction, index):
	script = script.split()
	stack = []
	for word in script:
		if is_op(word):
			# get function and execute
			stack = opcode2method[word](stack) if word !='CHECKSIG' else opcode2method[word](stack, transaction, index)
		else:
			stack.append(word)
	return stack



if __name__ == "__main__":
	
	s = 'hashahs OP_DUP OP_DUP OP_HASH160'
	stack = []
	stack = execute_script(s, stack, None, None)
	print(stack)









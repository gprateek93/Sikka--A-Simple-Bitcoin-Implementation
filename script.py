from opcodes import is_op, opcode2method

# expects a stack from the caller.
def exectue_script(script, stack):
	script = script.split()
	for word in script:
		if is_op(word):
			# get function and execute
			stack = opcode2method[word](stack)
		else:
			stack.append(word)
	return stack



if __name__ == "__main__":
	
	s = 'hashahs OP_DUP OP_DUP OP_HASH160'
	stack = []
	stack = exectue_script(s, stack)
	print(stack)









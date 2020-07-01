# from crypto import generate_hash
import hashlib
# to add an opcode:
# add it to the opcode list
# create a method that only takes a single argument 'stack' and returns 'stack'
# add the function mapping in opcode2method dictionary at the end of the file
#create method to execute the script which takes the transaction also as input.

opcode_list = ['OP_CHECKSIG', 'OP_EQUAL', 'OP_DUP', 'OP_HASH160', 'OP_VERIFY', 'OP_EQAULVERIFY', 'OP_CHECKMULTISIG']

def is_op(word):
	if word in opcode_list:
		return True
	return False

# def checksig(stack):
# 	public_key = stack.pop()
# 	signature = stack.pop()
	
# 	return stack

def dup(stack):
	stack.append(stack[-1])
	return stack

def equal(stack):
	arg1 = stack.pop()
	arg2 = stack.pop()
	if arg1 == arg2:
		stack.append(True)
	else:
		stack.append(False)
	return stack

def verify(stack):
	if stack[-1] == True:
		return 1
	else:
		return 0

def hash160(stack):
	# compute hash (SHA-256) of the TOS and place is back
	# m = stack.pop()
	# stack.append(generate_hash(m))
	m = hashlib.sha256()
	m.update(bytes(stack.pop(), encoding='UTF-8'))
	stack.append(m.hexdigest())
	return stack


opcode2method = {
				 'OP_EQUAL' : equal, 
				 'OP_DUP' : dup, 
				 'OP_HASH160' : hash160, 
				 'OP_VERIFY' : verify, 
				#  'OP_CHECKSIG' : checksig, 
				#  'OP_EQAULVERIFY' : equalverify, 
				#  'OP_CHECKMULTISIG' : checkmultisig
				}
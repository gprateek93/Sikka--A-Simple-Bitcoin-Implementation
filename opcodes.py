from crypto import generate_hash, verify_signature
import hashlib
# to add an opcode:
# add it to the opcode list
# create a method that only takes a single argument 'stack' and returns 'stack'
# add the function mapping in opcode2method dictionary at the end of the file
#create method to execute the script which takes the transaction also as input.

opcode_list = ['OP_CHECKSIG', 'OP_EQUAL', 'OP_DUP', 'OP_HASH256', 'OP_VERIFY', 'OP_EQAULVERIFY', 'OP_CHECKMULTISIG']

def is_op(word):
	if word in opcode_list:
		return True
	return False

def checksig(stack, transaction, index):
	public_key = stack.pop()
	signature = stack.pop()
	stack.append(verify_signature(transaction.get_raw_signature(index), public_key, signature))
	return stack

def dup(stack):
	stack.append(str((stack[-1].e,stack[-1].n)))
	return stack

def equal(stack):
	arg1 = stack.pop()
	arg2 = stack.pop()
	if arg1 != arg2:
		return False
	return stack

def verify(stack):
	if stack[-1] == True:
		return True
	else:
		return False

def hash256(stack):
	# compute hash (SHA-256) of the TOS and place is back
	# m = stack.pop()
	# stack.append(generate_hash(m))
	stack.append(hex(generate_hash(stack.pop())))
	return stack


opcode2method = {
				 'OP_EQUAL' : equal, 
				 'OP_DUP' : dup, 
				 'OP_HASH256' : hash256, 
				 'OP_VERIFY' : verify, 
				 'OP_CHECKSIG' : checksig 
				#  'OP_EQAULVERIFY' : equalverify, 
				#  'OP_CHECKMULTISIG' : checkmultisig
				}
def found_golden_hash(block, mining_effort):
	num_leading_zeros = b'0' * mining_effort
	block_hash = hex_to_bytes(block.get_hash()[2:]) # becasue hex string
	# print('---------', block_hash)
	if block_hash[mining_effort] != b'0' and block_hash.startswith(num_leading_zeros):
		return True
	return False

def calc_proof_of_work(block, mining_effort):
	# find the correct nonce 
	block.finalize()
	while(not found_golden_hash(block, mining_effort)):
		block.increment_nonce()
		block.finalize()
		# print('block hash', block.get_hash())
	block.difficulty = mining_effort	
	# print('block mined: ', block.get_hash(),'\n Adding to Chain')
	return block

def hex_to_bytes(hex_str):
	b_str = b''
	bit_map = {
		'0' : b'0000',
		'1' : b'0001',
		'2' : b'0010',
		'3' : b'0011',
		'4' : b'0100',
		'5' : b'0101',
		'6' : b'0110',
		'7' : b'0111',
		'8' : b'1000',
		'9' : b'1001',
		'a' : b'1010',
		'b' : b'1011',
		'c' : b'1100',
		'd' : b'1101',
		'e' : b'1110',
		'f' : b'1111'}
	for i in hex_str:
		b_str += bit_map[i]
	return b_str








































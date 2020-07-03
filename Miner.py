from constants import mining_effort
class Miner:
	def __init__(self, neighbour_node_list,):
		self.pending_txns = [] # for mining


	def found_golden_hash(self, block):
		num_leading_zeros = '0' * mining_effort
		block_hash = block.get_hash()[2:] # becasue hex string
		if block_hash[mining_effort] != '0' and block_hash[0:mining_effort] == num_leading_zeros:
			return True
		return False

	def mine(self, blockChain):
		
		# create the block to be mined
		# look in block handler and see if anything else is needed in the args


		# find the correct nonce 
		block.generate_hash()
		while(not self.found_golden_hash(block)):
			block.increment_nonce()
			block.generate_hash()
		# announce only after consensus
		print('block mined: ', block.get_hash(),'\n Adding to Chain')

	# Simple Nakamoto consensus 
	# Ask the network for their longest chain
	# Take max of all verified chains, keep longest one
	def consensus(self):
		return True
	
	



		


			






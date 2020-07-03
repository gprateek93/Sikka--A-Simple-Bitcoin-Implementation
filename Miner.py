from constants import mining_effort, num_block_txns
from crypto import generate_key
import Block
import TransactionHandler as TxnH
import threading as th

class Miner:
	def __init__(self, blockchain, miner_id, node_pool):
		self.id  = miner_id # for logging
		self.pending_txns = [] # for mining
		assert blockchain != None, 'Empty Blockchain received' 
		self.blockchain = blockchain
		self.pending_txn_pool = []
		self.key_pair = generate_key()
		self.public_key = self.key_pair.publickey()
		self.node_pool = node_pool # Nodes connected with this miner
		
	def found_golden_hash(self, block):
		num_leading_zeros = '0' * mining_effort
		block_hash = block.get_hash()[2:] # becasue hex string
		if block_hash[mining_effort] != '0' and block_hash[0:mining_effort] == num_leading_zeros:
			return True
		return False

	def calc_proof_of_work(self, block):
		# find the correct nonce 
		block.generate_hash()
		while(not self.found_golden_hash(block)):
			block.increment_nonce()
			block.generate_hash()	
		# print('block mined: ', block.get_hash(),'\n Adding to Chain')
		return block

	def create_block(self):
		parent = self.blockchain.get_max_height_block()
		parent_hash = parent.get_hash()
		current_block = Block(parent_hash, self.public_key)
		max_node_utxo_pool = self.blockchain.get_max_height_node_UTXO_pool()
		handler = TxnH(max_node_utxo_pool)
		# number of valid txns may be less than num_block_txn
		valid_txns = handler.handleTxs(self.pending_txn_pool[0:num_block_txns])
		for txn in valid_txns:
			current_block.add_transactions(tnx)		
		return current_block

	def mine(self, blockChain):
		
		# create the block to be mined
		# look in block handler and see if anything else is needed in the args
		if len(self.pending_txn_pool) < num_block_txns:
			return False
		else:
			block = self.create_block()
			## this may take time.
			block = self.calc_proof_of_work(block)
			self.blockchain.addBlock(block)
			self.pending_txn_pool = self.pending_txn_pool[num_block_txns:]
			return block

	# Simple Nakamoto consensus 
	# Ask the network for their longest chain
	# Take max of all verified chains, keep longest one
	def consensus(self):
		# get the blockchain of neighbours (threads)

		# find a chain longer than your chain
		
		return True
	
	def worker(self):

		# receive all txns save them to self.pending txn pool
		# see if you can mine
		# if true then mine
		# concensus
		# broadcast block
		# else wait




		


			






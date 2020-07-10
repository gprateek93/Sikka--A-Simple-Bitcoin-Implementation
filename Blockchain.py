from UTXO import UTXO
from UTXO_pool import UTXO_pool
from TransactionHandler import TransactionHandler
from constants import max_branch_len_diff,mining_effort,genesis_prev_block_hash
from Block import Block
from Miner import Miner
import logging
import crypto
from Transaction import Transaction
# TODO Create a replace blockchain method. See Miner.consensus()
# TODO Create a method Blockchain.contains_block(block) which returns True if block is added in block chain


class Blockchain:
	class BlockNode:
		def __init__(self, block = None, parent = None, utxo_pool = None):
			self.block =  block
			self.parent = parent
			self.utxo_pool = utxo_pool
			self.children = []
			if parent is not None:
				self.height = parent.height + 1
				parent.children.append(self)
			else:
				self.height = 1

	def __init__(self, genesis_block = None):
		self.blockchain = dict({})
		utxo_pool = UTXO_pool()
		self.add_coinbase_tx(genesis_block,utxo_pool)
		genesis_node = Blockchain.BlockNode(block= genesis_block, utxo_pool= utxo_pool)
		self.maxheightnode = genesis_node
		self.blockchain[genesis_block.get_hash()] = genesis_node
		logging.info(f"Blockchain created with maxheightnode = {self.maxheightnode} and dictionary = {self.blockchain}")


	def add_block(self, block = None, proof= None):
		prev_hash = block.get_prev_block_hash()
		if prev_hash == None:
			logging.info(f"Block not valid because previous block hash is None")
			return False
		if prev_hash not in self.blockchain:
			logging.info(f"Block not valid because previous block hash is not in the blockchain")
			return False
		if not self.is_valid_proof(block,proof):
			return False
		parent_node = self.blockchain[prev_hash]
		tx_handler = TransactionHandler(parent_node.utxo_pool)
		txs = block.get_all_transactions()[1:] #because the first transaction is the coinbase transaction
		validTXs = tx_handler.handleTxs(txs)
		#block gets verified here
		if len(validTXs) != len(txs):
			logging.info(f"Block not valid because there is some invalid transaction")
			return False
		height = parent_node.height + 1
		if (height <= self.maxheightnode.height - max_branch_len_diff):
			logging.info(f"Block not valid because of invalid forking")
			return False
		utxo_pool = tx_handler.utxo_pool
		self.add_coinbase_tx(block=block, utxo_pool=utxo_pool)
		block_node = Blockchain.BlockNode(block=block, parent=parent_node, utxo_pool=utxo_pool)
		if height > self.maxheightnode.height:
			self.maxheightnode = block_node
		self.blockchain[block.get_hash()] = block_node
		logging.info(f"new block with hash = {block.get_hash()} gets added in the block-chain")
		return True

	def get_max_height_block(self):
		return self.maxheightnode.block

	def get_max_height_node_UTXO_pool(self):
		return self.maxheightnode.utxo_pool     

	def add_coinbase_tx(self,block = None, utxo_pool = None):
		coinbase = block.get_coinbase_txn()
		for i in range(coinbase.total_outputs()):
			out = coinbase.get_output(i)
			utxo = UTXO(coinbase.get_hash(), i)
			utxo_pool.add_UTXO(utxo, out)

	def contains_block(self, block = None):
		if block is None:
			return False
		else:
			if block.get_hash() in self.blockchain:
				return True
			else:
				return False

	def is_valid_proof(self, block, block_hash):
		return (block_hash[2:].startswith('0' * mining_effort) and block.get_hash() == block_hash)

	def is_valid_chain(self):
		prev_block_hash = genesis_prev_block_hash
		for current_block_hash in self.blockchain:
			current_block = self.blockchain[current_block_hash].block
			print(current_block)
			if current_block.get_prev_block_hash() != prev_block_hash:
				return False
			current_block.finalize()
			recomputed_current_hash = current_block.get_hash()
			if not self.is_valid_proof(current_block,recomputed_current_hash):
				return False
			prev_block_hash = recomputed_current_hash

		return True
		
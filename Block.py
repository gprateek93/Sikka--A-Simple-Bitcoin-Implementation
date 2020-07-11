from Transaction import Transaction
from merkle import MerkleTree
import crypto
from constants import miner_reward,genesis_prev_block_hash
import Miner
import logging


class Block:

	def __init__(self, prev_hash= None, node_pool= None, address=None, genesis_block = False):
		logging.basicConfig(filename=f'LOG-Block.log', level=logging.DEBUG, format='%(asctime)s : %(levelname)s :Process- %(process)d %(processName)s: Thread- %(thread)d %(threadName)s: %(funcName)s : %(message)s')
		if genesis_block:
			self.__coinbase_txn = self.create_genesis_block(node_pool)
			self.__txns = [self.__coinbase_txn]
			self.__prev_block_hash = genesis_prev_block_hash
			logging.info(f"Genesis block created")
		else:
			self.__prev_block_hash = prev_hash
			self.__coinbase_txn = Transaction(coin=miner_reward, address=address)
			self.__coinbase_txn.finalize()
			self.__txns = [self.__coinbase_txn]
			self.__address = address # public key of miner
		self.__merkle_tree_root = None
		self.__nonce = 0
		self.__hash = None
		self.difficulty = None

	def create_genesis_block(self, node_pool=None):
		assert len(node_pool) > 0, "The system cannot have 0 nodes initially during the creation of genesis block"
		genesis_txn = Transaction(version= 0, lock_time= 0, coin= 100, address = node_pool[0].get_address())
		for node in node_pool[1:]:
			pubkey = node.get_address()
			genesis_txn.add_output(pubkey,100)
		genesis_txn.finalize()
		return genesis_txn

	def get_coinbase_txn(self):
		return self.__coinbase_txn
	
	def get_hash(self):
		return self.__hash
	
	def get_prev_block_hash(self):
		return self.__prev_block_hash
	
	def get_all_transactions(self):
		return self.__txns
	
	def get_transaction_at(self, index):
		return self.__txns[index]
	
	def add_transaction(self, txn):
		self.__txns.append(txn)
	
	
	def increment_nonce(self):
		self.__nonce += 1

	def construct_merkle_tree(self):
		mt = MerkleTree(self.__txns)
		self.__merkle_tree_root = mt.root
		

	def get_raw_block(self):
		raw_block = str(self.__nonce) + self.__merkle_tree_root.hash

		if self.__prev_block_hash != None:
			# hex string
			raw_block += self.__prev_block_hash[2:]
		for i in range(len(self.__txns)):
			# str of tnx
			raw_block += self.__txns[i].get_raw_txn()
		return raw_block

	def finalize(self):
		self.__hash = hex(crypto.generate_hash(self.get_raw_block()))

import Transaction
import merkle
from hashlib import sha256
class Block:

	def __init__(self, prev_hash, address, merkle_arity=2):
		self.coinbase_value = 25
		self.__hash = None
		self.__prev_block_hash = prev_hash
		self.__coinbase_txn = Transaction(coinbase_value, address)
		self.__txns = []
		self.__merkle_tree_root = None
		self.__merkle_arity = merkle_arity
		self.__nonce = 0
	
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
		mt = MerkleTree(self.__merkle_arity, self.__txns)
		self.__merkle_tree_root = mt.root

	def get_raw_block(self):
		raw_block = str(self.__nonce) + self.__merkle_tree_root

		if self.__prev_block_hash != None:
			# hex string
			raw_block += self.__prev_block_hash[2:]
		for i in range(self.__txns):
			# str of tnx
			raw_block += self.__txns[i].getRawTx()
		return raw_block

	def generate_hash(self):
		m = sha256()
		m.update(bytes(self.get_raw_block(), encoding='UTF-8'))
		self.__hash = m.hexdigest()




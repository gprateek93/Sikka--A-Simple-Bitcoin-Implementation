from functools import total_ordering
import sys

@total_ordering
class UTXO:
	def __init__(self, txn_hash, index):
		self.txn_hash = txn_hash
		self.index = index
		self.hash_index_tup = (txn_hash, index)
	
	def __eq__(utxo_1, utxo_2):
		if utxo_1.index == utxo_2.index and utxo_1.txn_hash == utxo_2.txn_hash:
			return True
		return False

	def __lt__(utxo_1, utxo_2):
		if utxo_1.index < utxo_2.index:
			return True
		elif utxo_1.index > utxo_2.index:
			return False
		else:
			if len(utxo_1.txn_hash) < len(utxo_2.txn_hash):
				return True
		return False

	def __hash__(self):
		return hash(self.hash_index_tup)
	
	def __sizeof__(self):
		return sys.getsizeof(self.txn_hash) + sys.getsizeof(self.index) + sys.getsizeof(self.hash_index_tup)

			


	


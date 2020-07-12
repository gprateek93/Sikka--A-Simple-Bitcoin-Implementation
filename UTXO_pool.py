from collections import defaultdict as dd
import sys

class UTXO_pool:
	def __init__(self):
		self.mappings = dict({})

	def add_UTXO(self, utxo, txn_output):
		# add the utxo and txn output
		self.mappings[utxo] = txn_output

	def delete_utxo(self, utxo):
		del self.mappings[utxo]
	
	def get_txn_output(self, utxo):
		return self.mappings[utxo]
	
	def has_utxo(self, utxo):
		return utxo in self.mappings

	def get_all_utxo(self):
		return list(self.mappings.keys())
	
	# return dict with Key as public key of miner 
	# and value as total unspent coins in that block
	def get_total_unspent_coins(self):
		total_unspent_coins = dd(int)
		for utxo, op in self.mappings.items():
			# for op in txn_outputs:
			total_unspent_coins[op.pubkey_hash] += op.value
		return total_unspent_coins

	def get_total_unspent_utxo(self):
		total_unspent_utxo = dd(list)
		for utxo, op in self.mappings.items():
			# for op in txn_outputs:
			total_unspent_utxo[op.pubkey_hash].append((utxo,op.value))
		return total_unspent_utxo

	def __sizeof__(self):
		size = 0
		for key in self.mappings.keys():
			size += sys.getsizeof(key) + sys.getsizeof(self.mappings[key])



	
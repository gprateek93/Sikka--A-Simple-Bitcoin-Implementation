
class UTXO_pool:
	def __init__(self):
		self.mappings = dict({})

	def add_UTXO(self, utxo, txn_output):
		# add the utxo and txn output
		self.mappings[utxo.hash_index_tup] = txn_output

	def delete_utxo(self, utxo):
		del self.mappings[utxo.hash_index_tup]
	
	def get_txn_output(self, utxo):
		return self.mappings[utxo.hash_index_tup]
	
	def has_utxo(self, utxo):
		return utxo.hash_index_tup in self.mappings

	def get_all_utxo(self):
		return list(self.mappings.keys())
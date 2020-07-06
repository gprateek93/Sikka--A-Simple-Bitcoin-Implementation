
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
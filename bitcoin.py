from Miner import Miner
from Block import Block
from Blockchain import Blockchain
from multiprocessing.managers import BaseManager
from concurrent.futures import ProcessPoolExecutor
from MessageClass import Queue_Event_Lock
from constants import num_seed_nodes,num_non_seed_nodes
from Miner_utils import calc_proof_of_work

if __name__ == "__main__":

	class MyManager(BaseManager):
		pass  

	MyManager.register('QEL', Queue_Event_Lock)
	main_node_pool = []
	seed_nodes = dict({})
	manager = MyManager()
	manager.start()

	# create genesis block
	for i in range(num_seed_nodes):    
		# seed_nodes[i] = new_seed.get_QEL()
		seed_nodes[i] = manager.QEL()
		new_seed = Miner(miner_id=i, blockchain = None, manager_qel=seed_nodes[i], node_type="SEED")
		main_node_pool.append(new_seed)

	# create genesis blockchain with cionbase for each seed node
	block = Block(node_pool= main_node_pool, genesis_block=True)
	block.construct_merkle_tree()
	print('Node 0 ki compute power', main_node_pool[0].compute_power)
	# block = calc_proof_of_work(block, main_node_pool[0].compute_power)
	block = calc_proof_of_work(block, 2)
	print('Done computing')

	gen_blockchain = Blockchain(genesis_block=block)
	for i in range(num_seed_nodes):
		main_node_pool[i].blockchain = gen_blockchain

	for i in range(num_seed_nodes, num_non_seed_nodes + num_seed_nodes):
		test_node = Miner(miner_id=i, blockchain = None, manager_qel=manager.QEL(), seed_node_pool=seed_nodes, node_type="NON-SEED")
		main_node_pool.append(test_node)

	with ProcessPoolExecutor(max_workers=num_non_seed_nodes+num_seed_nodes+2) as executor:
		for node in main_node_pool:
			executor.submit(node.spawn)

	print('Done with everything')
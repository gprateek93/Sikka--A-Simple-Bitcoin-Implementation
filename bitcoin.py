import Miner
from concurrent.futures import ThreadPoolExecutor

def run_node(node):
	print(f'Running {os.getpid()} with node id {node.id}') 
	node.spawn()

if __name__ == "__main__":
	main_node_pool = []
	seed_nodes = dict({})
	for i in range(2):
		new_seed = Miner(miner_id=i,node_type="SEED")
		seed_nodes[i] = (new_seed.lock, new_seed.message_queue)
		main_node_pool.append(new_seed)

	test_node = Miner(miner_id=3, seed_node_pool=seed_nodes, node_type="NON-SEED")
	main_node_pool.append(test_node)
	print("here")
	with ThreadPoolExecutor(max_workers=3) as executor:
		print("here")
		executor.map(run_node,main_node_pool)
import multiprocessing 
import logging
import os
import pickle
import random
from collections import deque
from constants import mining_effort, num_block_txns, min_neighbours, num_non_seed_nodes, num_seed_nodes
from concurrent.futures import ProcessPoolExecutor
from copy import copy, deepcopy # check if deep copy works for classes and if it doesn't create a function in blockchain to give a copy of it
from crypto import generate_key, sign_message, generate_hash
from MessageClass import Message
from multiprocessing import Manager, Lock
from multiprocessing.managers import BaseManager
from threading import Thread, Event
from time import sleep
from Transaction import Transaction
from Block import Block
from Blockchain import Blockchain
from Miner_utils import calc_proof_of_work, found_golden_hash
from random import randint, sample
from TransactionHandler import TransactionHandler as TxnH
class Miner:
	def __init__(self, miner_id, blockchain, manager_qel, seed_node_pool = dict({}), node_type=None):

		self.id  = miner_id # for logging
		self.blockchain = deepcopy(blockchain)
		self.key_pair = generate_key()
		self.public_key = self.key_pair.publickey()
		self.node_pool = dict({}) # Nodes connected with this miner
		self.node_pool_address = dict({}) # public keys of neighbours
		self.seed_node_pool = seed_node_pool
		self.__type = node_type # "SEED" / "NON-SEED"
		self.QEL = manager_qel
		self.pending_txn_pool = []
		self.waiting_for_consensus_reply = (None, None)
		self.received_txns = set() # txn_hash
		self.received_blocks = set() # block_hash
		self.compute_power = randint(3,10) # lower the number higher is the compute power coz faster will be the mining
		self.start_mining = False
		self.start_creating_txns = False
		self.connected_with_neighbours = 1
		self.run_mine = 5
		self.len_list= 0
		self.temp_utxo_list = []
		self.first_txn = False

		logging.basicConfig(filename=f'LOG-MINER-{self.id}.log', level=logging.DEBUG, format='%(asctime)s : %(levelname)s :Process- %(process)d %(processName)s: Thread- %(thread)d %(threadName)s: %(funcName)s : %(message)s')
		logging.info(f'Miner {self.id} object Created')
	
	def get_QEL(self):
		return self.QEL

	def get_address(self):
		return self.public_key

	def process_messages(self):

		# Message Structure
		## Connect Request: (CONNECT_REQEUST, Node ID, Reffered_by Node ID, Node_QEL)
		### reffered by node id == SEED for seed nodes and actual NodeID for other nodes
		### Yes, a malacious node can lock my queue forever. 
		### Assuming a malacious node isn't interested in hampering communication 
		### as irl it will happen over the internet therefore no locks will be shared. 
		### Assumption: A node once connected will not be disconnected. Can be handled by adding a last seen param to neighbours.
		## Connect Reply: (CONNECT_REPLY, Node ID, blockchain, node_pool, ) # no need to send message queue
		### Also, send the data of the neighbours ie, node id, lock and queue. 
		### So that this new node can connect with them if it wishes to
		
		## New Incoming TXN: (NEW_TXN, Transaction obj) # for now, this is not coming from any node.
		## Request Blockchain: (REQUEST_BLOCKCHAIN, NodeID, REQ_NUM) 
		## Reply to BC REQ: (REPLY_BLOCKCHAIN, NodeID, Blockchain, REQ_NUM)
		## Broadcast newly mined Block: (NEW_BLOCK, Creator_NodeID, Sender_node_id, Block) 
		
		# check messages
		self.QEL.acquire()
		if self.QEL.empty():
			self.QEL.release()
			return None
		message = self.QEL.pop_message()
		self.QEL.release()

		if message.id == 'CONNECT_REQUEST':
			self.connect_request(message)
		elif message.id == 'CONNECT_REPLY':
			self.connect_reply(message)
		elif message.id == 'REQUEST_BLOCKCHAIN':
			self.request_blockchain(message)
		elif message.id == 'REPLY_BLOCKCHAIN':
			self.reply_blockchain(message)
		elif message.id == 'NEW_TXN':
			self.new_txn(message)
		elif message.id == 'NEW_BLOCK':
			self.new_block(message)
		else:
			print(f'Node: {self.id} received undecipherable message: {Message}')


		# receive all txns save them to self.pending txn pool
		# see if you can mine
		# if true then mine
		# concensus
		# broadcast block
		# else wait
	
	# Only need node_id if sending message to neighbour
	# else give lock and message queue too!
	def send_message(self, node_id, message, node_QEL=None):
		# To ensure that we only send messages to our neighbours
		# And non-neighbours only get CONNECT REQUESTS
		QEL = self.node_pool[node_id] if node_id in self.node_pool else node_QEL 	
		if QEL is not None:
			QEL.acquire()
			QEL.add_message(message)
			QEL.release()
			# print(f'Node {self.id} sent Message: {message} to Node {node_id}')
		else:
			s = f'Node {node_id} is not my (node {self.id}) neighbour and None QEL supplied. So can not send messages'
			print(s)
			logging.info(s)

	def connect_request(self, message):
		new_node_id, ref_node_id, new_node_QEL, new_node_pubkey = message.args
		logging.info(f'CONNECT REQ received from {new_node_id}')
		if (ref_node_id == 'SEED' and self.__type == 'SEED') or (ref_node_id != 'SEED' and ref_node_id in self.node_pool) :
			# craft connect message
			reply_node_pool = copy(self.node_pool)
			if ref_node_id != 'SEED':
				# reply_node_pool.remove(ref_node_id)
				del reply_node_pool[ref_node_id]
			connect_reply_message = Message('CONNECT_REPLY', [self.id, deepcopy(self.blockchain), reply_node_pool, self.QEL, self.public_key])
			# Add NodeID to known neighbours
			# self.node_pool.add(new_node_id)
			self.node_pool[new_node_id] = new_node_QEL
			self.node_pool_address[new_node_id] = new_node_pubkey
			# send a connect reply
			self.send_message(new_node_id, connect_reply_message)
			logging.info(f"CONNECT Successful : connected to {new_node_id}")
		else:
			logging.info(f"CONNECT UNSuccessful : not connected to {new_node_id}")

	def connect_reply(self, message):
		# Add the replying node to your pool 
		new_node_id, new_blockchain, reply_node_pool, reply_node_QEL, new_node_publickey = message.args
		# self.node_pool.add(new_node_id) 
		self.node_pool[new_node_id] = reply_node_QEL 
		self.node_pool_address[new_node_id] = new_node_publickey
		logging.info(f'CONNECT REPLY received from {new_node_id}')
		
		# if your blockchain is None add reply_blockchain
		if self.blockchain is None:
			self.blockchain = new_blockchain # already deep-copied

		# send a connect request to the node pool received.
		# Ignore the node pool if number of neighbours are equal to constants.max_neighbours
		if len(self.node_pool) < min_neighbours:
			diff =  min_neighbours - len(self.node_pool) 
			for node_id in reply_node_pool:
				if diff > 0 and node_id not in self.node_pool:
					connect_message = Message('CONNECT_REQUEST', [self.id, new_node_id, self.QEL, self.public_key])			
					self.send_message(node_id, connect_message, reply_node_pool[node_id])
					diff -= 1
		
	def request_blockchain(self, m):
		node_id, req_num = m.args
		logging.info(f'Node {self.id} received BLOCKCHAIN REQUEST from Node {node_id}')
		if node_id in self.node_pool:
			m = Message('REPLY_BLOCKCHAIN', [self.id, deepcopy(self.blockchain), req_num])
			self.send_message(node_id, m)
		else:
			s = f'Node {node_id} not in node {self.id}s node pool, How did it send me a message?'
			print(s)
			logging.info(s)
	
	def reply_blockchain(self, message):
		# use the protocol in connect reply to replace the blockchain if needed 
		reply_node_id, reply_node_blockchain, req_num = message.args
		logging.info(f'Node {self.id} received BLOCKCHAIN REPLY from Node {reply_node_id}||| {(reply_node_id, req_num)} == {self.waiting_for_consensus_reply}')
		# wake up the sleeping thread for consensus.
		if (reply_node_id, req_num) == self.waiting_for_consensus_reply:
			# it will be replaced iff a longer valid block chain is found
			# TODO Create a replace_blockchain method
			# must make sure that transactions in the old block chain are checked with the new one 
			# and the pending_txn pool is appropriately changed.
			current_height = self.blockchain.maxheightnode.height 
			reply_height = reply_node_blockchain.maxheightnode.height 
			if  current_height < reply_height and \
				reply_node_blockchain.is_valid_chain():
				
				logging.info(f'Consensus {self.id}: BC updated {self.blockchain} --> {reply_node_blockchain}')
				self.blockchain = reply_node_blockchain				
			else:
				logging.info(f'Consensus {self.id}: BC updated {self.blockchain} --> {self.blockchain}')
		else:
			s = f'How did {self.waiting_for_consensus_reply} consensus reply for node {self.id} come now? \nDiscarding it.'
			print(s)
			logging.info(s)

		self.QEL.set()
		logging.info(f'Consensus {self.id}: EVENT is now SET')

	def new_txn(self, message):
		sending_node, new_txn = message.args
		if new_txn.get_hash() not in self.received_txns:
			self.received_txns.add(new_txn.get_hash())
			self.pending_txn_pool.append(new_txn)
			self.broadcast(new_txn, ele_type='txn')
	
	def new_block(self, message):
		# this method is used when receiving a new_block message.
		# To send a new_block message: see mine() after consensus()
		new_node_id, block = message.args
		# add this new block to our blockchain if Not already added and verified otherwise discard
		# remove all pending transactions that are part of the newly ADDED block
		# make appropriate changes to the internals of blockchain

		# if you add the block to your blockchain
		# make sure to forward this to all the nodes that are in your node_pool except the incoming node.
		if block.get_hash() not in self.received_blocks:
			self.received_blocks.add(block.get_hash())
			# propagate block
			self.broadcast(block, ele_type='block')
			if not self.blockchain.contains_block(block):
				self.blockchain.add_block(block, block.get_hash())

	def broadcast(self, element, ele_type):
		# send out this block to all your neighbours in the node_pool.
		if ele_type == 'block':
			m = Message('NEW_BLOCK', [self.id, deepcopy(element)])
		else:
			m = Message('NEW_TXN', [self.id, deepcopy(element)])
		for node_id in self.node_pool:
			self.send_message(node_id, m)

	# TODO TEST
	def create_block(self):
		parent = self.blockchain.get_max_height_block()
		parent_hash = parent.get_hash()
		current_block = Block(prev_hash=parent_hash, address=self.public_key)
		max_node_utxo_pool = self.blockchain.get_max_height_node_UTXO_pool()
		handler = TxnH(max_node_utxo_pool)
		# number of valid txns may be less than num_block_txn
		valid_txns = handler.handleTxs(self.pending_txn_pool)
		for txn in valid_txns:
			current_block.add_transaction(txn)		
		current_block.construct_merkle_tree()
		return current_block
	
	# TODO TEST
	def create_random_txn(self):
		# look at the block chain and see how much money you have
		if self.first_txn and (self.len_list == len(self.temp_utxo_list)):
			return None
		total_cash = self.blockchain.get_max_height_node_UTXO_pool().get_total_unspent_utxo()
		if len(total_cash) > 0:
			my_utxos_and_values = total_cash[hex(generate_hash(str((self.public_key.e,self.public_key.n))))]
			if not self.first_txn:
				self.len_list = len(my_utxos_and_values)

			#create blank Transactions
			new_txn = Transaction()
			# choose random (utxo, op) and add them to inputs

			if len(my_utxos_and_values) == 0:
				return None
			r = randint(1, len(my_utxos_and_values)) if len(my_utxos_and_values) > 1 else 1
			chosen_utxos = sample(my_utxos_and_values, r)
			self.temp_utxo_list += chosen_utxos
			value = 0
			for utxo, op_value in chosen_utxos:
				new_txn.add_input(utxo.txn_hash, utxo.index)
				value += op_value
			# Choose a 'k' random neighbours and send a random amts to them
			k = randint(1, len(self.node_pool))
			lucky_neighbours = sample(self.node_pool.keys(), k)
			for neigh in lucky_neighbours:
				if value <= 0:
					break
				neigh_value = randint(0, value)
				if neigh_value == 0:
					continue
				new_txn.add_output(self.node_pool_address[neigh], neigh_value)
				value -= neigh_value
			if value > 0:
				new_txn.add_output(self.public_key, value)
			for i in range(new_txn.total_inputs()):
				message = new_txn.get_raw_signature(i)
				signature = sign_message(message=message, keyPair=self.key_pair)
				new_txn.add_signature(i, signature)
				new_txn.get_input(i).add_unlocking_script(signature, self.public_key)
			new_txn.finalize()
			self.first_txn = True
			return new_txn
		else:
			print(f'Node {self.id} could not create a transaction. not utxos ')
		return None

	# TODO TEST
	def find_block(self):		
		# create the block to be mined
		# look in block handler and see if anything else is needed in the args
		if len(self.pending_txn_pool) == 0:
			return False
		else:
			block = self.create_block()
			## this may take time.
			block = calc_proof_of_work(block, 2)
			self.pending_txn_pool = []
			return block

	def mine(self):
		# find / extract a block from the mine :D
		found_block = self.find_block()
		while not found_block:
			found_block = self.find_block()
		print(f'Node {self.id} found a block')
		# sleep(random.random()*10)

		self.blockchain.add_block(found_block, found_block.get_hash())
		print(f'Node {self.id} added a block to blockchain')
		# consensus
		pre_concensus_blockchain = deepcopy(self.blockchain)
		blockchain_changed = False
		consensus_thread = Thread(target=self.consensus, name='Consesus-'+str(self.id))
		consensus_thread.start()
		consensus_thread.join()
		# if len(pre_concensus_blockchain) < len(self.blockchain): # => Concensus failed
		current_height = self.blockchain.maxheightnode.height 
		pre_consensus_height = pre_concensus_blockchain.maxheightnode.height 
		if pre_consensus_height < current_height: # => Concensus failed
			# put all the transactions in the mined block into the pending txn pool
			# check for transactions that have been already covered in the blockchain
			# remove them from pending txn pool
			logging.info(f'Consesus FAILED! Node:{self.id} | prev vs now = {pre_concensus_blockchain} vs {self.blockchain}')
			found_block = None
		else: 
			# concensus acheived
			logging.info(f'Consesus ACHEIVED! Node:{self.id} |  prev vs now = {pre_concensus_blockchain} vs {self.blockchain}')
			self.broadcast(found_block, ele_type='block')
		self.len_list= 0
		self.temp_utxo_list = []
		self.first_txn = False
		consensus_thread = None

	# Simple Nakamoto consensus 
	# Ask the network for their longest chain
	# Take max of all verified chains, keep longest one
	def consensus(self):
		# get the blockchain of neighbours (threads)
		logging.info(f'Consensus for {self.id}: Begin')
		req_num = random.randint(0,1e5)
		for node_id in self.node_pool:
			m =  Message('REQUEST_BLOCKCHAIN', [self.id, req_num])
			self.send_message(node_id, m)
			self.waiting_for_consensus_reply = (node_id, req_num)
			# Now wait for the node to reply with their blockchain
			self.QEL.clear()
			logging.info(f'Consensus for {self.id}: REQUEST sent to {node_id} waiting for EVENT. {self.waiting_for_consensus_reply}')
			self.QEL.wait()

		return True

	# Process Messages till you Die!
	def run_message_thread(self):
		while True:
			self.process_messages()
			if self.connected_with_neighbours > 0 and ((self.__type == "SEED" and len(self.node_pool) >= min_neighbours-num_seed_nodes+1 ) or (len(self.node_pool) >= min_neighbours)):
				s = f'Node {self.id} is done connecting with neighbours. They are great! Should start mining now. Uhh! Work!' 
				print(s)
				logging.info(s)        
				print(f'Node {self.id} blockchain : {self.blockchain} neigh num: {len(self.node_pool)}')
				self.connected_with_neighbours = 0
				self.start_mining = True
				self.start_creating_txns = True
	
	# First Mine then Dine :D
	def run_mining_thread(self):
		while self.run_mine:
			if not self.start_mining:
				continue
			# if self.blockchain is None:
			# 	# this includes mining the genesis block
			# 	self.create_genesis_blockchain()
			# 	continue
			s = f'Node: {self.id} | Run_mine = {self.run_mine}'
			print(s)
			logging.info(s)
			self.mine()
			self.run_mine -= 1 # to mine a fixed number of blocks 
			print(f'Node: {self.id} miner is sleeping for 90s')
			sleep(90)
			print(f'Node: {self.id} miner is done sleeping. Time to Work!')

		s = f'Node {self.id} has mined all the blocks. Stopping mining now.'
		print(s)
		logging.info(s)

	def run_txn_creation(self):
		
		while True:
			if not self.start_creating_txns:
				continue
			print(f'Node {self.id} creating a Transaction')
			txn = self.create_random_txn()
			if txn is not None:
				print(f'Node {self.id} CREATED a Transaction')
				# add to pending txn pool and received txn pool
				self.received_txns.add(txn.get_hash())
				self.pending_txn_pool.append(txn)
				self.broadcast(txn, ele_type='txn')
			else:
				print(f'Node {self.id} could not create a Transaction')
			sleep(10)
		 
	def spawn(self):
		# make two threads
		print(f'Running {os.getpid()} with node id {self.id}')
		process_messsage_thread = Thread(target=self.run_message_thread, name='Processing-'+str(self.id))
		mine_thread = Thread(target=self.run_mining_thread, name='Mining-'+str(self.id))
		txn_thread = Thread(target=self.run_txn_creation, name='Txn_Creation-'+str(self.id))
		# create transact thread which will create transactions using the image of blockchain and broadcast transactions to all nodes 
		string = f"message + mining thread created for node {self.id}"
		# print(string)
		logging.info(string)
		#send connect messages to seed_node_pool
		if len(self.seed_node_pool) > 0:
			for node_id in self.seed_node_pool:
				m = Message('CONNECT_REQUEST', [self.id, 'SEED', self.QEL, self.public_key])
				self.send_message(node_id, m, self.seed_node_pool[node_id])
				s = f'CONNECT REQUEST sent to {node_id}'
				print(s)
				logging.info(s)
		else:
			s = f'Node {self.id} received empty'
			print(s)
			logging.info(s)
		#run the threads
		process_messsage_thread.start()
		mine_thread.start()
		txn_thread.start()
		logging.info(f'Node {self.id}: Threads Started!')
		mine_thread.join()
		txn_thread.join()
		process_messsage_thread.join()		
		logging.info(f"Loop ends here for node {self.id}")


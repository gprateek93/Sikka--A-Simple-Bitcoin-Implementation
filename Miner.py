from constants import mining_effort, num_block_txns, max_neighbours
from crypto import generate_key
from MessageClass import Message, Message_Queue
import Block
import TransactionHandler as TxnH
import logging
from merkel import MerkleTree
from copy import deepcopy # check if deep copy works for classes and if it doesn't create a function in blockchain to give a copy of it
import threading as th
from threading import Lock, Thread

class Miner:
	def __init__(self, blockchain, miner_id, seed_node_pool, node_type, genesis_miner=False):

		self.id  = miner_id # for logging
		if not genesis_miner:
			assert blockchain != None, 'Empty Blockchain received' 

		self.blockchain = deepcopy(blockchain)
		self.pending_txn_pool = []
		self.key_pair = generate_key()
		self.public_key = self.key_pair.publickey()

		# NodeID : (lock, queue)
		# I think we should send seed nodes separately and add them only once they reply.
		# That means no need for node pool
		self.node_pool = dict({}) # Nodes connected with this miner
		self.seed_node_pool = seed_node_pool
		self.message_queue = Message_Queue()
		self.lock = Lock()
		self.__type = node_type # "SEED" / "NON-SEED"
		self.received_blocks = set()
		
		self.consensus_event_pool = dict({}) # node_id : thread_obj
		self.run = 1
		logging.basicConfig(filename=f'LOG-MINER-{self.id}.log', level=logging.DEBUG, format='%(asctime)s : %(levelname)s :Process- %(process)d %(processName)s: Thread- %(thread)d %(threadName)s: %(funcName)s : %(message)s')
		logging.info(f'Miner {self.id} object Created')


	# this is the function that will be called to run by the process
	def spawn(self):
		# make two threads
		mine_thread = Thread(target=self.mine, name='Mining-'+str(self.id))
		process_messsage_thread = Thread(target=self.process_messages, name='Processing-'+str(self.id))
		logging.info(f'mining and message Threads created')
		#send connect messages to seed_node_pool
		for node_id in self.seed_node_pool:
			m = Message('CONNECT_REQUEST', [self.id, 'SEED', self.lock, self.message_queue])
			lock, Q = self.seed_node_pool(node_id)
			self.send_message(node_id, m, lock, Q)
			logging.info(f'CONNECT REQUEST sent to {node_id}')
		#run the threads
		while self.run:
			process_messsage_thread.start()
			mine_thread.start()
			logging.info(f'Threads Started')
			if len(self.node_pool) >= max_neighbours:
				print('Done connecting with neighbours')				
				self.run = 0

	def mine(self):
		# find / extract a block from the mine :D
		found_block = self.find_block()
		# consensus
		pre_concensus_blockchain = deepcopy(self.blockchain)
		blockchain_changed = False
		self.consensus()
		if len(pre_concensus_blockchain) < len(self.blockchain): # => Concensus failed
			# put all the transactions in the mined block into the pending txn pool
			# check for transactions that have been already covered in the blockchain
			# remove them from pending txn pool
		else: 
			# concensus acheived
			# broadcast_new_mined_block() to all neighbours


	def found_golden_hash(self, block):
		num_leading_zeros = '0' * mining_effort
		block_hash = block.get_hash()[2:] # becasue hex string
		if block_hash[mining_effort] != '0' and block_hash[0:mining_effort] == num_leading_zeros:
			return True
		return False

	def calc_proof_of_work(self, block):
		# find the correct nonce 
		block.generate_hash()
		while(not self.found_golden_hash(block)):
			block.increment_nonce()
			block.generate_hash()	
		# print('block mined: ', block.get_hash(),'\n Adding to Chain')
		return block

	def create_block(self):
		parent = self.blockchain.get_max_height_block()
		parent_hash = parent.get_hash()
		current_block = Block(parent_hash, self.public_key)
		max_node_utxo_pool = self.blockchain.get_max_height_node_UTXO_pool()
		handler = TxnH(max_node_utxo_pool)
		# number of valid txns may be less than num_block_txn
		valid_txns = handler.handleTxs(self.pending_txn_pool[0:num_block_txns])
		for txn in valid_txns:
			current_block.add_transactions(tnx)		
		current_block.construct_merkle_tree()
		return current_block


	def find_block(self):		
		# create the block to be mined
		# look in block handler and see if anything else is needed in the args
		if len(self.pending_txn_pool) < num_block_txns:
			return False
		else:
			block = self.create_block()
			## this may take time.
			block = self.calc_proof_of_work(block)
			self.blockchain.addBlock(block)
			self.pending_txn_pool = self.pending_txn_pool[num_block_txns:]
			return block

	# Simple Nakamoto consensus 
	# Ask the network for their longest chain
	# Take max of all verified chains, keep longest one
	def consensus(self):
		# get the blockchain of neighbours (threads)
		for node_id in self.node_pool:
			self.send_message(node_id, Message('REQUEST_BLOCKCHAIN', [self.id]))
			# Now wait for the node to reply with their blockchain
			# it will be replaced iff a longer valid block chain is found

			# TODO Create a replace_blockchain method
			# must make sure that transactions in the old block chain are checked with the new one 
			# and the pending_txn pool is appropriately changed.
 		
		return True
	

	def process_messages(self):

		# Message Structure
		## Connect Request: (CONNECT_REQEUST, Node ID, Reffered_by Node ID, node.lock, node.message_queue)
		### reffered by node id == SEED for seed nodes and actual NodeID for other nodes
		### Yes, a malacious node can lock my queue forever. 
		### Assuming a malacious node isn't interested in hampering communication 
		### as irl it will happen over the internet therefore no locks will be shared. 
		### Assumption: A node once connected will not be disconnected. Can be handled by adding a last seen param to neighbours.
		## Connect Reply: (CONNECT_REPLY, Node ID, blockchain, node_pool, node.lock, node.message_queue) # no need to send message queue
		### Also, send the data of the neighbours ie, node id, lock and queue. 
		### So that this new node can connect with them if it wishes to
		
		## New Incoming TXN: (NEW_TXN, Transaction obj) # for now, this is not coming from any node.
		## Request Blockchain: (REQUEST_BLOCKCHAIN, NodeID, REQ_NUM) 
		## Reply to BC REQ: (REPLY_BLOCKCHAIN, NodeID, Blockchain, REQ_NUM)
		## Broadcast newly mined Block: (NEW_BLOCK, Creator_NodeID, Sender_node_id, Block) 
		
		# check messages
		if self.message_queue.empty():
			return None
		self.lock.acquire()
		message = self.message_queue.pop_message()
		self.lock.release()

		if message.id == 'CONNECT_REQUEST':
			self.connect_request(message)
		elif message.id == 'CONNECT_REPLY':
			self.connect_reply(message)
		elif message.id == 'NEW_TRANSACTION':
			self.new_transaction(message.args[0])
		elif message.id == 'REQUEST_BLOCKCHAIN':
			self.request_blockchain(message.args[0], message.args[1])
		elif message.id == 'REPLY_BLOCKCHAIN':
			self.reply_blockchain(message)
		elif message.id == 'NEW_BLOCK':
			self.new_block(message) # what all things do we need to check for?
			# do we need the public key?
			# is there a method to add block to block chain?
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
	def send_message(self, node_id, message, lock=None, Q=None):
		# 	return None
		if node_id in self.node_pool:
			lock, Q = self.node_pool[node_id]
		else:
			if lock is None or Q is None:
				print(f'{self.id} can not send {message} to {node_id}: Lock/Queue missing')
				return None
		lock.acquire()
		Q.add_message(message)
		lock.release()

	def connect_request(self, message):
		new_node_id, ref_node_id, new_node_lock, new_node_message_queue = message.args
		if (ref_node_id == 'SEED' and self.__type == 'SEED') or (ref_node_id != 'SEED') :
			# craft connect message
			reply_node_pool = deepcopy(self.node_pool)
			if ref_node_id != 'SEED':
				del reply_node_pool[ref_node_id]
			connect_reply_message = Message('CONNECT_REPLY', [self.id, deepcopy(self.blockchain), reply_node_pool, self.lock, self.message_queue])
			# Add NodeID to known neighbours
			self.node_pool[new_node_id] = (new_node_lock, new_node_message_queue)
			# send a connect reply
			self.send_message(new_node_id, connect_reply_message)
			# logging: Connect-message Successfully received and processed connected to new_node_id
		# else:
			# logging: Connect-message processed, NOT connected to new_node_id

	def connect_reply(self, message):
		# Add the replying node to your pool 
		new_node_id, blockchain, reply_node_pool, new_node_lock, new_node_message_queue = message.args
		self.node_pool[new_node_id] = (new_node_lock, new_node_message_queue)

		# if your blockchain is None add reply_blockchain
		if self.blockchain is None:
			self.blockchain = blockchain # already deep-copied

		# send a connect request to the node pool received.
		# Ignore the node pool if number of neighbours are equal to constants.max_neighbours
		if len(self.node_pool) < max_neighbours:
			diff =  max_neighbours - len(self.node_pool) 
			for node_id in reply_node_pool:
				if diff > 0 and node_id not in self.node_pool:
					connect_message = Message('CONNECT_REQUEST', [self.id, new_node_id, self.lock, self.message_queue])			
					lock, Q =  reply_node_pool[node_id][0]
					self.send_message(node_id, connect_message, lock, Q)
					diff -= 1

	def new_transaction(self, transaction):
		# just add it to pending txn pool
		self.pending_txn_pool.append(txn)

	def request_blockchain(self, node_id, req_num):
		if node_id in self.node_pool:
			m = Message('REPLY_BLOCKCHAIN', [self.id, deepcopy(self.blockchain), req_num])
			self.send_message(node_id, m)
		# else:
		# 	print('node not in node pool, How did it send me a message?')
	
	def reply_blockchain(self, message):
		# use the protocol in connect reply to replace the blockchain if needed 
		reply_node_id, reply_node_blockchain, req_num = message.args
		# wake up the sleeping thread for consensus.

	def broadcast_new_mined_block(self, creator_node_id, block, sender_node_id=None):
		# send out this block to all your neighbours in the node_pool.
		for node_id in self.node_pool:
			if node_id == sender_node_id:
				continue
			m = Message('NEW_BLOCK', [creator_node_id, self.id, deepcopy(block)])
			self.send_message(node_id, m)

	def new_block(self, message):
		# this method is used when receiving a new_block message.
		# To send a new_block message: see mine() after consensus()
		creator_node_id, sender_node_id, block = message.args
		# add this new block to our blockchain if Not already added and verified otherwise discard
		# remove all pending transactions that are part of the newly ADDED block
		# make appropriate changes to the internals of blockchain

		# if you add the block to your blockchain
		# make sure to forward this to all the nodes that are in your node_pool except the incoming node.
		if block.get_hash() not in self.received_blocks:
			self.received_blocks.add(block.get_hash())
			# propagate block
			self.broadcast_new_mined_block(creator_node_id, block, self.id)
			if not self.blockchain.contains_block(block):
				self.blockchain.addBlock(block)
				
	def get_address(self):
		return self.public_key
	
	

	
	
	




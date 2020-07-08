from dataclasses import dataclass
# from collections import deque
from queue import Queue as Q

# Message Structure
## Connect Request: (CONNECT_REQEUST, Node ID, node.message_queue)
## Connect Reply: (CONNECT_REPLY, Node ID, blockchain) # no need to send message queue
## New Incoming TXN: (NEW_TXN, Transaction obj) # for now this is not coming from any node.
## Request Blockchain: (REQ_BlockChain, NodeID) 
## Reply to BC REQ: (REPLY_BlockChain, NodeID, Blockchain)
## Broadcast newly mined Block: (NEW_BLOCK, NodeID, Block)
@dataclass
class Message:
	id: str
	args: []

class Message_Queue:
	def __init__(self):
		self.q = Q()
	
	def pop_message(self):
		return self.q.get()
	
	def add_message(self, m):
		self.q.put(m)
		
	def empty(self):
		return self.q.empty()

# class Message_Queue:
# 	def __init__(self):
# 		self.q = deque()
	
# 	def pop_message(self):
# 		return self.q.popleft()
	
# 	def add_message(self, m):
# 		self.q.append(m)
		
# 	def empty(self):
# 		if len(self.q) == 0:
# 			return True
# 		return False

		
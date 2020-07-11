from dataclasses import dataclass
from collections import deque
from multiprocessing import Lock
from threading import Event

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

class Queue_Event_Lock:
	def __init__(self):
		self.__q = deque()
		self.__e = Event()
		self.__lock = Lock()
	def acquire(self):
		return self.__lock.acquire()
	def release(self):
		return self.__lock.release()	
	def pop_message(self):
		return self.__q.popleft()
	def add_message(self, m):
		self.__q.append(m)
	def empty(self):
		if len(self.__q) == 0:
			return True
		return False
	def isSet(self):
		return self.__e.isSet()
	def wait(self):
		return self.__e.wait()
	def set(self):
		return self.__e.set()
	def clear(self):
		return self.__e.clear()

	def __repr__(self):
		return str(self.q)

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

# 	def __repr__(self):
# 		return str(self.q)


# class Manager_Message_Queue:
# 	def __init__(self, Q):
# 		self.q = Q
	
# 	def pop_message(self):
# 		return self.q.get()
	
# 	def add_message(self, m):
# 		self.q.put(m)
		
# 	def empty(self):
# 		return self.q.empty()
		
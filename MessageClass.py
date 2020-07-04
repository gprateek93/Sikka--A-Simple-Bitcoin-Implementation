from dataclasses import dataclass
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
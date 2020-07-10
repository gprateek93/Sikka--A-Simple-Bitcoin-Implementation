import Transaction
from constants import merkle_arity
import crypto
class MerkleNode:
    def __init__(self, hash = ""):
        self.hash = hash #hex string
        self.children  = []

class MerkleTree:
    def __init__(self, transactions = []):
        self.airity = merkle_arity
        self.transactions = transactions
        node_list = self.tx_nodes()
        self.constructTree(node_list)

    def tx_nodes(self):
        tx_node_list = []
        for tx in self.transactions:
            node = MerkleNode(tx.hash)
            # node = MerkleNode(tx)
            tx_node_list.append(node)
        return tx_node_list

    def constructTree(self,tx_nodes = []):
        if len(tx_nodes) == 1:
            self.root = tx_nodes[0]
            return
        airity = self.airity
        m = len(tx_nodes) % airity
        updated_nodes = []
        for i in range(0,len(tx_nodes) - m,airity):
            node = MerkleNode()
            hash = hex(0)
            for j in range(0,airity):
                hash = hex(crypto.generate_hash(hash[2:] + tx_nodes[i+j].hash[2:]))
                node.children.append(tx_nodes[i+j])
            node.hash = hash
            updated_nodes.append(node)
        
        if m != 0:
            node = MerkleNode()
            hash = hex(0)
            for i in range(m,0,-1):
                hash = hex(crypto.generate_hash(hash[2:] + tx_nodes[-i].hash[2:]))
                node.children.append(tx_nodes[-i])
            for i in range(0,airity-m):
                hash = hex(crypto.generate_hash(hash[2:] + tx_nodes[-1].hash[2:]))
                node.children.append(tx_nodes[-1])
            node.hash = hash
            updated_nodes.append(node)
        self.constructTree(updated_nodes)
    
    def traverse(self, root = None):
        if root is not None:
            print(root.hash)
        if root == None or len(root.children) == 0:
            return
        else:
            for child in root.children:
                self.traverse(child)
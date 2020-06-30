import Transaction

class MerkleNode:
    def __init__(self, hash = ""):
        self.hash = hash
        self.children  = []

class MerkleTree:
    def __init__(self,airity = 2, transactions = []):
        self.airity = airity
        self.transactions = transactions
        node_list = self.tx_nodes()
        self.constructTree(node_list)

    def tx_nodes(self):
        tx_node_list = []
        for tx in self.transactions:
            # node = MerkleNode(tx.hash)
            node = MerkleNode(tx)
            tx_node_list.append(node)
        return tx_node_list

    def constructTree(self,tx_nodes = []):
        print("printing")
        for node in tx_nodes:
            print(node.hash)
        if len(tx_nodes) == 1:
            self.root = tx_nodes[0]
            return
        airity = self.airity
        m = len(tx_nodes) % airity
        updated_nodes = []
        for i in range(0,len(tx_nodes) - m,airity):
            node = MerkleNode()
            # hash = hex(0)
            hash = ""
            for j in range(0,airity):
                hash += tx_nodes[i+j].hash
                node.children.append(tx_nodes[i+j])
            node.hash = hash
            updated_nodes.append(node)
        
        if m != 0:
            node = MerkleNode()
            # hash = hex(0)
            hash = ""
            for i in range(m,0,-1):
                hash += tx_nodes[-i].hash
                node.children.append(tx_nodes[-i])
            for i in range(0,airity-m):
                hash += tx_nodes[-1].hash
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
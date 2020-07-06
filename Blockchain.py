import UTXO
import UTXO_pool
import TransactionHandler
from constants import max_branch_len_diff
# TODO Create a replace blockchain method. See Miner.consensus()
# TODO Create a method Blockchain.contains_block(block) which returns True if block is added in block chain
class Blockchain:
    class BlockNode:
        def __init__(self, block = None, parent = None, utxo_pool = None):
            self.block =  block
            self.parent = parent
            self.utxo_pool = utxo_pool
            self.children = []
            if parent is not None:
                self.height = parent.height + 1
                parent.children.append(self)
            else:
                self.height = 1

    def __init__(self, genesis_block = None):
        self.blockchain = dict({})
        utxo_pool = UTXO_pool()
        self.addcoinbasetx(genesis_block,utxo_pool)
        genesis_node = Blockchain.BlockNode(block= genesis_block, utxo_pool= utxo_pool)
        self.maxheightnode = genesis_node
        self.blockchain[genesis_block.get_hash()] = genesis_node


    def addBlock(self, block = None):
        prev_hash = block.get_prev_block_hash()
        if prev_hash == None:
            return False
        if prev_hash not in self.blockchain:
            return False
        parent_node = self.blockchain[prev_hash]
        tx_handler = TransactionHandler(parent_node.utxo_pool)
        txs = block.get_all_transactions()[1:] #because the first transaction is the coinbase transaction
        validTXs = tx_handler.handleTxs(txs)
        #block gets verified here
        if len(validTXs) != len(txs) :
            return False
        height = parent_node.height + 1
        if (height <= self.maxheightnode.height - max_branch_len_diff):
            return False
        utxo_pool = tx_handler.utxo_pool
        self.addcoinbasetx(block=block, utxo_pool=utxo_pool)
        block_node = Blockchain.BlockNode(block=block, parent=parent_node, utxo_pool=utxo_pool)
        if height > self.maxheightnode.height:
            self.maxheightnode = block_node
        self.blockchain[block.get_hash()] = block_node
        return True

    def get_max_height_block(self):
        return self.maxheightnode.block

    def get_max_height_node_UTXO_pool(self):
        return self.maxheightnode.utxo_pool     

    def addcoinbasetx(self,block = None, utxo_pool = None):
        coinbase = block.get_coinbase_txn()
        for i in coinbase.total_outputs():
            out = coinbase.getOutput(i)
            utxo = UTXO(coinbase.getHash(), i)
            utxo_pool.add_UTXO(utxo, out)

    def contains_block(self, block = None):
        if block is None:
            return False
        else:
            if block.get_hash() in self.blockchain:
                return True
            else:
                return False
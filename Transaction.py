import crypto
import logging
import sys

logging.basicConfig(filename=f'LOG-Transaction.log', level=logging.DEBUG, format='%(asctime)s : %(levelname)s :Process- %(process)d %(processName)s: Thread- %(thread)d %(threadName)s: %(funcName)s : %(message)s')
class Transaction:
    class Input:
        def __init__(self,prev_hash = None ,index = None):
            self.prev_hash = prev_hash
            self.index = index
            self.signature = None
            self.unlocking_script = None
            logging.info(f"New input added with reference to previous transaction {self.prev_hash} and output index {self.index}")
        
        def add_signature(self, signature = None):
            self.signature = signature
            logging.info(f"Input with reference to previous transaction {self.prev_hash} and output index {self.index} has been successfully signed with signature {self.signature}")
        
        def add_unlocking_script(self, signature = None, pubkey = None):
            assert signature is not None, "A certain unlocking script can't have signature as None"
            assert pubkey is not None, "A certain unlocking script can't have public key as None"
            self.unlocking_script = [signature,pubkey]
        
        def __eq__(self,other):
            if self.prev_hash == other.prev_hash and self.index == other.index and self.unlocking_script == other.unlocking_script:
                return True
            return False

    class Output:
        def __init__(self, pubkey = None, value = None):
            self.value = value
            self.pubkey = pubkey
            self.pubkey_hash = hex(crypto.generate_hash(str((pubkey.e,pubkey.n)))) 
            #hex string of integer hash.
            #For comparison in unlocking first convert into hexstring after removing '0x'
            self.locking_script = ["OP_DUP" , "OP_HASH256", self.pubkey_hash, "OP_EQUAL",  "OP_CHECKSIG"]
            logging.info(f"New Transaction output created with value {self.value} given to address {self.pubkey_hash}")

        def __eq__(self,other):
            if self.value == other.value and self.locking_script == other.locking_script:
                return True
            return False
        
        def __sizeof__(self):
            return sys.getsizeof(self.value) + sys.getsizeof(self.pubkey) + sys.getsizeof(self.pubkey_hash) + sys.getsizeof(self.locking_script)

    def __init__(self,version = 0,lock_time = 0, coin = -1, address = None):
        if(coin == -1):
            self.coinbase = False
            self.version = version
            self.inputs = []
            self.outputs = []
            self.lock_time = lock_time
            self.hash = None
            logging.info(f"New Transaction created with version number {self.version}")
        else:
            assert address is not None, "Address to a certain coinbase transaction can't be None"
            self.coinbase = True
            self.inputs = []
            self.outputs = []
            self.add_output(address, coin)
            self.version = version
            self.lock_time = lock_time
            self.hash = None
            logging.info(f"New Coinbase Transaction created with version number {self.version} and coin value {coin}")

        
    
    def coinbase(self):
        return self.coinbase

    def add_input(self, prev_hash, index):
        inp = Transaction.Input(prev_hash,index)
        self.inputs.append(inp)
    
    def add_output(self, pubkey, value):
        out = Transaction.Output(pubkey,value)
        self.outputs.append(out)

    def remove_input(self,index):
        inputs.pop(index)

    def get_raw_txn(self):
        rawTx = ""
        rawTx+= str(self.version)
        for inp in self.inputs:
            if inp.prev_hash is not None:
                rawTx += str(inp.prev_hash)
            if inp.index is not None:
                rawTx += str(inp.index)
            if inp.signature is not None:
                rawTx += str(inp.signature)
        for out in self.outputs:
            if out.value is not None:
                rawTx += str(out.value)
            if out.pubkey_hash is not None:
                rawTx += str(out.pubkey_hash)
        rawTx += str(self.lock_time)
        return rawTx

    def finalize(self):
        self.hash  = hex(crypto.generate_hash(self.get_raw_txn()))

    def get_raw_signature(self, index):
        rawTx = ""
        rawTx+= str(self.version)
        inp = self.get_input(index)
        if inp.prev_hash is not None:
            rawTx += str(inp.prev_hash)
        if inp.index is not None:
            rawTx += str(inp.index)
        for out in self.outputs:
            if out.value is not None:
                rawTx += str(out.value)
            if out.pubkey_hash is not None:
                rawTx += str(out.pubkey_hash)
        rawTx += str(self.lock_time)
        return rawTx

    def add_signature(self, index = -1, signature = None):
        assert index < len(self.inputs) and index >= 0 , "Index out of bounds"
        assert signature is not None, "Signature of a certain input can't be None"
        self.inputs[index].add_signature(signature)

    def total_outputs(self):
        return len(self.outputs)

    def total_inputs(self):
        return len(self.inputs)

    def get_input(self,index):
        return self.inputs[index]

    def get_output(self,index):
        return self.outputs[index]
    
    def get_hash(self):
        return self.hash

    def __eq__(self, other):
        if self.hash!=other.hash or self.coinbase != other.coinbase or self.version != other.version or self.inputs != other.inputs or self.outputs != self.outputs or self.lock_time != other.lock_time:
            return False
        else:
            return True

    def __hash__(self):
        return int(self.hash,16)

    def __sizeof__(self):
        return sys.getsizeof(self.get_raw_txn())
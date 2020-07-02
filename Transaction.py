import crypto

class Transaction:
    class Input:
        def __init__(self,prev_hash = None ,index = None):
            self.prev_hash = prev_hash
            self.index = index
        
        def addSignature(self, signature = None):
            self.signature = signature
        
        def addUnlockingScript(self, signature = None, pubkey = None):
            assert signature is not None, "A certain unlocking script can't have signature as None"
            assert pubkey is not None, "A certain unlocking script can't have public key as None"
            self.unlocking_script = str(signature) + " " + str(pubkey)
        
        def __eq__(self,other):
            if self.prev_hash == other.prev_hash and self.index == other.index and self.unlocking_script == other.unlocking_script:
                return True
            return False

    class Output:
        def __init__(self, pubkey = None, value = None):
            self.value = value
            self.pubkey = pubkey
            pubkey_hash = crypto.generate_hash(pubkey)
            self.locking_script = "OP_DUP" + " " + "OP_HASH160" + " " + str(pubkey_hash) + " " + "OP_EQUALVERIFY" + " " + "OP_CHECKSIG"

        def __eq__(self,other):
            if self.value == other.value and self.locking_script == other.locking_script:
                return True
            return False

    def __init__(self,version = 0,lock_time = 0, coin = -1, address = None):
        if(coin == -1):
            self.coinbase = False
            self.version = version
            self.inputs = []
            self.outputs = []
            self.lock_time = lock_time
        else:
            assert address is not None, "Address to a certain coinbase transaction can't be None"
            self.coinbase = True
            self.inputs = []
            self.outputs = []
            self.add_output(address, coin)
            self.version = version
            self.lock_time = lock_time
    
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

    def getRawTx(self):
        rawTx = ""
        rawTx+= str(self.version)
        for inp in self.inputs:
            if inp.prev_hash is not None:
                rawTx += str(inp.prev_hash)
            if inp.index is not None:
                rawTx += str(inp.index)
            if inp.script_sig is not None:
                rawTx += str(inp.script_sig)
        for out in self.outputs:
            if out.value is not None:
                rawTx += str(out.value)
            if out.pubkey is not None:
                rawTx += str(out.pubkey)
        rawTx += self.lock_time
        return rawTx

    def finishTx(self):
        self.hash  = hex(crypto.generate_hash(bytes(self.getRawTx(),"utf-8")))

    def getRawSig(self):
        rawTx = ""
        rawTx+= str(self.version)
        for inp in self.inputs:
            if inp.prev_hash is not None:
                rawTx += str(inp.prev_hash)
            if inp.index is not None:
                rawTx += str(inp.index)
        for out in self.outputs:
            if out.value is not None:
                rawTx += str(out.value)
            if out.pubkey is not None:
                rawTx += str(out.pubkey)
        rawTx += self.lock_time
        return rawTx

    def addSignature(self, index = -1, signature = None):
        assert index < len(self.inputs) and index >= 0 , "Index out of bounds"
        assert signature is not None, "Signature of a certain input can't be None"
        self.inputs[index].addSignature(signature)

    def total_outputs(self):
        return len(self.outputs)

    def total_inputs(self):
        return len(self.inputs)

    def getInput(self,index):
        return self.inputs[index]

    def getOutput(self,index):
        return self.outputs[index]
    
    def getHash(self):
        return self.hash

    def __eq__(self, other):
        if self.hash!=other.hash or self.coinbase != other.coinbase or self.version != other.version or self.inputs != other.inputs or self.outputs != self.outputs or self.lock_time != other.lock_time:
            return False
        else:
            return True
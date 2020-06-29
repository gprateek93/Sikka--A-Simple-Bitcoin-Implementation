import crypto

class Transaction:
    class Input:
        def __init__(self,prev_hash = None ,index = None):
            self.prev_hash = prev_hash
            self.index = index
        
        def addSignature(self, script_sig = None):
            self.script_sig = script_sig
    
    class Output:
        def __init__(self, pubkey = None, value = None):
            self.value = value
            self.pubkey = pubkey
    
    def __init__(self,version,lock_time):
        self.version = version
        self.inputs = []
        self.outputs = []
        self.lock_time = lock_time
    
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
        rawTx = bytes(rawTx , "utf-8")
        return rawTx

    def finishTx(self):
        self.hash  = crypto.generate_hash(self.getRawTx())
    
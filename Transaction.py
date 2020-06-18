import crypto

class Transaction:
    class Input:
        def __init__(self,prev_hash,index):
            self.prev_hash = prev_hash
            self.index = index
        
        def addSignature(self,signature):
            self.signature = signature
    
    class Output:
        def __init__(self, public_key, value):
            self.value = value
            self.public_key = public_key
    
    def __init__(self, tx = None):
        if tx == None:
            self.dictionary = {}
            self.inputs = []
            self.outputs = []
        else:
            self.dictionary = tx.dictionary
            self.inputs = tx.inputs
            self.outputs = tx.outputs

    def add_input(self, prev_hash, index):
        inp = Transaction.Input(prev_hash,index)
        self.inputs.append(inp)
    
    def add_output(self, public_key, value):
        out = Transaction.Output(public_key,value)
        self.outputs.append(out)

    def remove_input(self,index):
        inputs.pop(index)
    
    
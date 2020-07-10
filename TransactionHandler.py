import crypto
import UTXO
import opcodes
import UTXO_pool
import script
from Transaction import Transaction
from UTXO_pool import UTXO_pool
from UTXO import UTXO

class TransactionHandler:
    def __init__(self, utxo_pool):
        self.utxo_pool = utxo_pool

    def isValidTx(self, tx):
        unique_utxo = UTXO_pool()
        input_sum = 0
        output_sum = 0
        for i in range(tx.total_inputs()):
            inp = tx.get_input(i)
            utxo = UTXO(inp.prev_hash, inp.index)
            if not self.utxo_pool.has_utxo(utxo):
                return False
            out = self.utxo_pool.mappings[utxo]
            verification_script = inp.unlocking_script + out.locking_script + ["OP_VERIFY"]
            if not script.execute_script(verification_script,tx,i):
                return False
            if unique_utxo.has_utxo(utxo):
                return False
            unique_utxo.add_UTXO(utxo, out)
            input_sum += out.value

        for i in range(tx.total_outputs()):
            out = tx.get_output(i)
            if out.value<0:
                return False
            output_sum += out.value

        return input_sum >= output_sum
            
    def handleTxs(self, transactions=[]):
        validTX = []
        i = 0
        for tx in transactions:
            if(self.isValidTx(tx)):
                validTX.append(tx)
                for inp in tx.inputs:
                    utxo = UTXO(inp.prev_hash, inp.index)
                    self.utxo_pool.delete_utxo(utxo)
                for i in range(tx.total_outputs()):
                    utxo = UTXO(tx.get_hash(), i)
                    self.utxo_pool.add_UTXO(utxo,tx.get_output(i))
            i+=1
        validTX = list(set(validTX))
        return validTX
        
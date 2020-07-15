# Sikka - A Simple Bitcoin Implementation
This repository contains code for the python implementation of simple blockchain architecture for multi-transaction bitcoin.

# Bitcoin System
Our implementation of the Bitcoin Cryptocurrency supports multiple transactions, has integrity checks for transactions using digital signatures and for blocks using merkle tree in blocks and proof of work is used to verify block before adding them to the blockchain. Satoshi Nakamoto consensus of chosing the longest valid chain each time at consensus is used to ensure the node agree upon the histroy of transactions.
# Simple Bitcoin
Nodes are implemented as separate processes each running 3 threads in parallel, one for communication, one for mining and, another for transaction generation. The proof of work used in the implementation is to 2 bit length which can be easily modified by changing the mining effort variable in constants.py. We have used merkle trees in the block to ensure that transactions in the block are not tampered with or rearranged in any way. The arity of the merkle tree used can be modified by changing the merkle arity variable in constants.py Every node has an RSA keypair to identify and communicate with each other and sign transactions. To ensure simple Nakamoto consensus a node asks each neighbour for their blockchains and among them the longest verified blockchain is selected to be ours if the current blockchain turns out to be of a smaller size. To ensure honest nodes, all generated transactions are valid and so are the blocks with their correct proof of work.
# Transactions
## Structure
Each of the transactions has two main classes, Input and Output. The Input class objects are maintained to keep track of inputs to the transaction. These inputs refer previous hash and output indices, stored in an unspent transactions pool of block. The outputs are specified by the address of the receiver and the value of the transaction. After adding these inputs and outputs, for each input a signature is generated and the transaction is signed for that particular input.
<br> A transaction can be either a coin-base transaction or a normal transaction. A coin-base transaction is made whenever someone makes a new block. Every unspent transaction(UTXO) in a block gets into the unspent transaction pool of that block (UTXO Pool). Each unspent transaction is a pair of previous transaction hash and output index which is mapped to a transaction output object in UTXO pool.
<br>![Figure 1. The parts of a Transaction](/Images/Transactions.png)
<br>*Figure 1. The parts of a Transaction*
## Transaction Verification
Each and every transaction is verified using a TransactionHandler object. This object checks the validity of the transaction by checking three things:  
1. Each of the inputs must refer some entry in the UTXO pool of the block.
2. The sum of input values must be greater than or equal to sum of output values and output values must be non negative.
3. The combination of the locking script of previous referred output matches with the unlocking script of the referring input.
<br>
The testing of verification script is done using a stack. We have followed the P2PKH verification. Each of the script’s data elements are put on the stack and are verified using the opcodes and popped. In the end an a Boolean result is obtained from the top of the stack. The following is the list of opcodes implemented:

- __OP DUP__: This opcode duplicates the data at the top of stack
- __OP HASH256__: This opcode generates a SHA-256 hash of the element at the top of the stack.
- __OP EQUAL__: This opcode checks the top two objects of the stack for equality.
- __OP CHECKSIG__: This opcode, given a signed message, signature and a public key, checks whether the message is signed with the given signature or not.
- __OP VERIFY__: Returns True if the top of the stack is 1 otherwise returns False.
# Blockchain
## Structure of a Block
Each of the block is capable of handling multiple transactions. Blocks are designed such that on creation of the block, the node creating the block gets block creation fee or a coin-base transaction is made towards the address of the node. Apart from the list of transactions, a block has a block header which has its, previous block hash, nonce, and merkle tree root. In the starting genesis block is created with some coin creation transactions giving some seed nodes an initial amount of bitcoins to spend.
## Structure of the Blockchain
A blockchain is a dictionary storing keys as the block hash and values as block nodes. Each block node has an associated block, a UTXO pool, a parent node, list of children nodes and height. Initially the blockchain is initialized with the genesis block. Blockchain keeps track of the maximum height node so that any new block is added after that only.
## Verification and adding a block into the blockchain
A block is added in the blockchain only if it meets the following condition:
1. The parent block of the given block is not None and is present in the current blockchain.
2. The proof of work (We have talked about this in a later section) of the block is valid.
3. The transactions inside the block are all valid.
4. The parent node is at most 10 nodes behind the max height node.
## Proof of Work, Mining and Consensus
There is a function to calculate the proof of work. The nonce value is randomly changed until the proof of work is achieved. Proof of work states that the block hash must start with a string of zeros with number of zeros equal to the difficulty of mining. More the difficulty, more time it takes to calculate the proof of work.
Mining of a block is done once the proof of work for the block is calculated. After that a simple consensus algorithm is run to achieve consensus among all nodes. A particular node/miner receives valid blockchains only from all the neighbour nodes and replace its current blockchain with the one having the largest height. If no blockchain is larger than its blockchain it adds its own newly mined block in its blockchain and broadcast in the network the newly mined block. All the nodes getting this new block then verifies it and adds them to their blockchain.
# Communication
A miner class is defined which personifies each of the computing node. Each miner is given its own process and inside that three threads are running in parallel. One thread is creating random transactions and sending to its neighbours. Other thread is mining for a block with multiple transactions. This mining operation happens after a specified amount of time as in the original bitcoin system. The last thread is for communication. Communication between two miners happens through message passing. The different messages for communication are:
- __Connect Request__: This message is sent by a miner ready to establish a connection with its neigh- bour
- __Connect Reply__: This is an acknowledge message to the connect request. Also signalling to connect.
- __Request Blockchain__: This message is sent to get the blockchain from a node.
- __Reply Blockchain__: This message is piggybacked with the node’s blockchain and serves as acknowl- edgement to request blockchain message.
- __New Block__: This message is to add a new block broadcasted in the network
- __New Txn__: This message is to add a new transaction in the network.
# How to run the code
1. Change the values in constants.py to configure the simulation.
2. Rename any old LOG files generated from previous execution.
3. To run the code use the following command:
```
python bitcoin.py
```

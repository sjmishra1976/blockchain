# Create a Cryptocurrency
# Create a virtual env using 'python3 -m venv blkchnenv'. source blkchnenv/bin/activate
# Install Flask as a pre-requisite. pip install Flask==0.12.2
# Install Requests==2.18.4 pip install Requests==2.18.4
# @author: santmishra

# import libraries
from datetime import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# part-1 Building blockchain
class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof = 1, previous_hash = '0')
        self.nodes = set()
        
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1, 
                 'timestamp': str(datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions':self.transactions
                 }
        self.transactions =[] 
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self,previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            # non symmetrical hence - and square are done, encode will give b'5' for previous_proof = 2 and new_proof = 3
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash1(self, block):  
        encoded_block = json.dumps(block,sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()             
                
            
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash1(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True

    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({ 'sender':sender,
        'receiver':receiver,
        'amount':amount
        })
        previous_block= self.get_previous_block()
        return previous_block['index'] + 1

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)


    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False





        
        

# part-2 Mining blockchain


# Writing webapp
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Creating address for node on port 5000
node_address = str(uuid4()).replace('-','')

# Creating blockchain
blockchain = Blockchain()

# Mine new block
@app.route('/mine_block', methods=['GET'])
def mine_block():
   previous_block = blockchain.get_previous_block()
   previous_proof = previous_block['proof']
   proof = blockchain.proof_of_work(previous_proof)
   previous_hash = blockchain.hash1(previous_block)
   blockchain.add_transaction(sender = node_address, receiver = 'santmishra_p2', amount = 1)
   block = blockchain.create_block(proof, previous_hash)
   response = {'message':'Congratulations, you just mined a block:',
               'index':block['index'],
               'timestamp':block['timestamp'],
               'proof':block['proof'],
               'previous_hash':block['previous_hash'],
               'transactions':block['transactions']
               }
   return jsonify(response), 200

#Getting the full blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain':blockchain.chain,'length':len(blockchain.chain)}
    return jsonify(response), 200
   
# Check if chain is valid
@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid_flag = blockchain.is_chain_valid(blockchain.chain)
    if is_valid_flag == True :
        response = {'message': 'All good. The Blockchain is valid.'}
    else :
        response = {'message': 'blockchain is invalid'}
    
    return jsonify(response), 200
# Adding a transaction to the Blockchain
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    transactions_keys = ['sender','receiver','amount']
    if not all (key in json for key in transactions_keys):
        return 'Some elements in transaction are missing', 400
    index = blockchain.add_transaction(json['sender'],json['receiver'],json['amount'])
    response = {'message':f'This transaction will be added to Block {index}' }
    return jsonify(response), 201


# Decentralizing the blockchain

# Connecting new node
@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
         return 'No Node', 400
    for node in nodes:
         blockchain.add_node(node)
    response = {'message': 'All the nodes are connected. The sanmiscoin blockchain now contains the total nodes ',
                'total_nodes':list(blockchain.nodes)}
    return jsonify(response), 201

# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced == True :
        response = {'message': 'Nodes has different chains so Chain Replaced by longest one.',
        'new_chain': blockchain.chain}
    else :
        response = {'message': 'All good, the chain the largest one','actual_chain': blockchain.chain}
    return jsonify(response), 200



# Running App
app.run(host='0.0.0.0', port = 5002)
#app.run(host='127.0.0.1', port = 5000)
                                   






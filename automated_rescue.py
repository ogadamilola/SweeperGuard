import os
import json
import time
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
PAYER_KEY = os.getenv("PAYER_KEY")
PAYER_ADDRESS = Web3.to_checksum_address("REPLACE ME WITH THE VAULT ADDY")
COMPROMISED_KEY = os.getenv("COMPROMISED_KEY")
COMPROMISED_ADDRESS = Web3.to_checksum_address("REPLACE ME WITH YOUR 'COMPRIMISED' ADDRESS")
VAULT_CONTRACT_ADDRESS = Web3.to_checksum_address("REPLACE ME WITH THE VAULT ADDY")
RPC_URL = "http://127.0.0.1:9650/ext/bc/C/rpc" # change this to your rpc endpoint
CHAIN_ID = 43114 # replace with your chain ID 

# Initialize web3
w3 = Web3(Web3.HTTPProvider(RPC_URL))
assert w3.is_connected(), "Web3 connection failed"

# Load ABI
with open("vault_compiled.json") as f:
    compiled = json.load(f)
vault_abi = compiled["contracts"]["Vault.sol"]["Vault"]["abi"]
vault_contract = w3.eth.contract(address=VAULT_CONTRACT_ADDRESS, abi=vault_abi)

# Step 1: Estimate gas and funding amount
gas_limit = 150000
gas_price = w3.eth.gas_price
required_funding = gas_limit * gas_price
required_funding_avax = w3.from_wei(required_funding, "ether")

print(f"[1] Rescue will cost approximately: {required_funding_avax:.6f} AVAX")

# Step 2: Send exact AVAX to compromised wallet
nonce = w3.eth.get_transaction_count(PAYER_ADDRESS, "pending")

funding_tx = {
    "nonce": nonce,
    "to": COMPROMISED_ADDRESS,
    "value": required_funding,
    "gas": 21000,
    "gasPrice": gas_price,
    "chainId": CHAIN_ID
}

signed_funding_tx = w3.eth.account.sign_transaction(funding_tx, PAYER_KEY)
funding_tx_hash = w3.eth.send_raw_transaction(signed_funding_tx.raw_transaction)
print(f"[2] Sent funding TX: {funding_tx_hash.hex()}")

# Step 3: Wait for confirmation
print("[3] Waiting for funding transaction to confirm...")
w3.eth.wait_for_transaction_receipt(funding_tx_hash)
print("[✓] Funding confirmed.")

# Step 4: Trigger the rescueAndSelfDestruct
rescue_nonce = w3.eth.get_transaction_count(COMPROMISED_ADDRESS, "pending")
rescue_tx = vault_contract.functions.rescueAndSelfDestruct().build_transaction({
    "from": COMPROMISED_ADDRESS,
    "nonce": rescue_nonce,
    "gas": gas_limit,
    "gasPrice": gas_price,
    "chainId": CHAIN_ID,
})

signed_rescue_tx = w3.eth.account.sign_transaction(rescue_tx, COMPROMISED_KEY)
rescue_tx_hash = w3.eth.send_raw_transaction(signed_rescue_tx.raw_transaction)
print(f"[4] Rescue TX sent: {rescue_tx_hash.hex()}")

# Step 5: Wait for rescue confirmation
print("[5] Waiting for rescue confirmation...")
receipt = w3.eth.wait_for_transaction_receipt(rescue_tx_hash)
print("[✓] Rescue confirmed in block:", receipt.blockNumber)

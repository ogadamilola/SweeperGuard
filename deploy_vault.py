import json
import time
from web3 import Web3
from eth_account import Account

# === CONFIG ===
PRIVATE_KEY = "YOUR PRIVATE KEY"  # Replace this!
SAFE_ADDRESS = Web3.to_checksum_address(Account.from_key(PRIVATE_KEY).address)

RPC_URL = "https://api.avax.network/ext/bc/C/rpc"  # Public Avalanche C-Chain RPC
CHAIN_ID = 43114

NFT_CONTRACT = Web3.to_checksum_address("NFT CONTRACT")  # Your NFT contract
COMPROMISED_ADDRESS = Web3.to_checksum_address("COMPROMISED ADDRESS")
TO_ADDRESS = Web3.to_checksum_address("ADDRESS WHICH YOU WANT TO SEND YOUR NFTS")
TOKEN_IDS = []  # Add all token IDs to rescue

# === SETUP ===
w3 = Web3(Web3.HTTPProvider(RPC_URL))
assert w3.is_connected(), "Web3 connection failed"

# Load ABI + bytecode from vault_compiled.json
with open("vault_compiled.json") as f:
    vault_data = json.load(f)

vault_abi = vault_data["abi"]
vault_bytecode = vault_data["bytecode"]

Vault = w3.eth.contract(abi=vault_abi, bytecode=vault_bytecode)

# === STEP 1: Deploy Vault contract ===
nonce = w3.eth.get_transaction_count(SAFE_ADDRESS)
gas_price = int(w3.eth.gas_price * 1.2)

print("Deploying Vault contract...")
deploy_tx = Vault.constructor(
    NFT_CONTRACT,
    COMPROMISED_ADDRESS,
    TO_ADDRESS,
    TOKEN_IDS
).build_transaction({
    "from": SAFE_ADDRESS,
    "nonce": nonce,
    "gas": 800000,
    "gasPrice": gas_price,
    "chainId": CHAIN_ID,
})

signed_deploy_tx = w3.eth.account.sign_transaction(deploy_tx, PRIVATE_KEY)
deploy_hash = w3.eth.send_raw_transaction(signed_deploy_tx.raw_transaction)
print(f"Sent deployment tx: {deploy_hash.hex()}")

print("Waiting for contract deployment confirmation...")
deploy_receipt = w3.eth.wait_for_transaction_receipt(deploy_hash)
vault_address = deploy_receipt.contractAddress
print(f"Vault deployed at: {vault_address}")

# === STEP 2: Trigger vault with AVAX ===
time.sleep(1)  # tiny delay to separate txs
trigger_tx = {
    "from": SAFE_ADDRESS,
    "to": vault_address,
    "value": w3.to_wei("0.01", "ether"),  # enough to execute transfers + leave nothing
    "gas": 21000,
    "gasPrice": gas_price,
    "nonce": nonce + 1,
    "chainId": CHAIN_ID,
}

signed_trigger = w3.eth.account.sign_transaction(trigger_tx, PRIVATE_KEY)
trigger_hash = w3.eth.send_raw_transaction(signed_trigger.raw_transaction)
print(f"Trigger sent to vault: {trigger_hash.hex()}")

print("Watching for NFTs + self-destruct...")
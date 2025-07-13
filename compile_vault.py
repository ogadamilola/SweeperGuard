from solcx import compile_standard, install_solc
import json

install_solc("0.8.0")

# Load Vault.sol source code
with open("Vault.sol", "r") as file:
    vault_source = file.read()

# Compile the contract
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {
            "Vault.sol": {
                "content": vault_source
            }
        },
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "evm.bytecode"]
                }
            }
        }
    },
    solc_version="0.8.0"
)

# Extract only ABI and Bytecode
vault_contract = compiled_sol["contracts"]["Vault.sol"]["Vault"]
abi = vault_contract["abi"]
bytecode = vault_contract["evm"]["bytecode"]["object"]

# Save simplified output for deployment
with open("vault_compiled.json", "w") as f:
    json.dump({
        "abi": abi,
        "bytecode": "0x" + bytecode
    }, f, indent=2)

print("Vault contract compiled and saved to vault_compiled.json")
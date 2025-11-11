# Configuration constants for Opinion CLOB SDK

# Supported chain IDs
SUPPORTED_CHAIN_IDS = [56]  # BNB Chain (BSC) mainnet

# BNB Chain (BSC) Mainnet Contract Addresses
BNB_CHAIN_CONDITIONAL_TOKENS_ADDR = "0xAD1a38cEc043e70E83a3eC30443dB285ED10D774"
BNB_CHAIN_MULTISEND_ADDR = "0x998739BFdAAdde7C933B942a68053933098f9EDa"

# Default contract addresses by chain ID
DEFAULT_CONTRACT_ADDRESSES = {
    56: {  # BNB Chain Mainnet
        "conditional_tokens": BNB_CHAIN_CONDITIONAL_TOKENS_ADDR,
        "multisend": BNB_CHAIN_MULTISEND_ADDR,
    }
}

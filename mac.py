"""
CBC-MAC module
"""

import aes

BLOCK_SIZE_BYTES = 16

def get_mac(plaintext, mac_key, mac_iv = None):
    """
    Return CBC-MAC block as bytes
    """
    ciphertext = aes.aes_encrypt(plaintext, mac_key, mac_iv)
    return ciphertext[:BLOCK_SIZE_BYTES], take_last_aes_block(ciphertext)

def take_last_aes_block(ciphertext):
    cipher_length = len(ciphertext)
    last_block = ciphertext[cipher_length-BLOCK_SIZE_BYTES:]
    return bytes(last_block)

def check_mac(plaintext, mac_received, mac_key, mac_iv):
    """
    Confirm mac is good
    """
    print (plaintext)
    mac_val = get_mac(plaintext, mac_key, mac_iv)
    if mac_val != mac_received:
        msg = "{} != {}".format(mac_val, mac_received)
        print(msg)
        return False
    return True

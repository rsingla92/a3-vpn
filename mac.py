"""
CBC-MAC module
"""

import aes

BLOCK_SIZE_BYTES = 16

class InvalidMACException(Exception):
    pass

def get_mac(plaintext, mac_key):
    """
    Return CBC-MAC block as bytes
    """
    ciphertext = aes.aes_encrypt(plaintext, mac_key)
    return take_last_aes_block(ciphertext)

def take_last_aes_block(ciphertext):
    cipher_length = len(ciphertext)
    last_block = ciphertext[cipher_length-BLOCK_SIZE_BYTES:]
    return bytes(last_block)

def check_mac(plaintext, ciphertext, mac_key):
    """
    Confirm mac is good
    """
    mac = get_mac(plaintext, mac_key)
    mac_received = take_last_aes_block(ciphertext)
    if mac != mac_received:
        msg = "{} != {}".format(mac, mac_received)
        raise InvalidMACException(msg)
    return ciphertext[:-BLOCK_SIZE_BYTES]

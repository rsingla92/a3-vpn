"""This module contains an implementation of the Deffie-Hellman 
Key Exchange Protocol.

Functions:


"""

debug = True

import random
import aes
import struct
from bitstring import BitArray

PUB_TRANSPORT_IDX = 0
LOC_EXPONENT_IDX = 1

#public large prime number
#1536 bit prime number - http://www.ietf.org/rfc/rfc3526.txt
prime = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA237327FFFFFFFFFFFFFFFF

#associated generator number - http://www.ietf.org/rfc/rfc3526.txt
gen = 2

def gen_public_transport(encrypt_protocol=False, long_term_key=0):
    if debug:
        print("generating public transport data")
    
    local_exponent = random.getrandbits(128)
    if debug:
        print("local_exponent: " + str(local_exponent))
    
    pub_transport = pow(gen, local_exponent, prime)
    if debug:
        print("pub_transport:" + str(pub_transport))
        
    if encrypt_protocol == False:
        return (pub_transport, local_exponent)
    else:
        ciphertext = aes.aes_encrypt(intToByteArray(pub_transport), long_term_key)
        if debug:
            print("ciphertext: " + str(ciphertext))
        return (str(ciphertext), local_exponent)

def gen_session_key(inc_pub_transport, local_exponent, encrypt_protocol=False, long_term_key=0):
    
    if encrypt_protocol == True:
        inc_pub_transport_bytes = aes.aes_decrypt(inc_pub_transport, long_term_key) #JHH This needs attention, as it comes back as a list of bytes
        inc_pub_transport = byteArrayToInt(inc_pub_transport_bytes)
    
    session_key = pow(inc_pub_transport, local_exponent, prime)
    
    if debug:
        print("private session key is: " + str(session_key))
    
    return session_key

#implemented to remind procedure on perfect forward secrecy
def finish_dh_key_generation(pfs, local_exponent):
    if pfs == True:
        local_exponent = 0
        
    return local_exponent
    
def run_test():
    #Jorden Testing:
    
    '''# Test basic functionality.  -- PASSES
    data1 = gen_public_transport()
    data2 = gen_public_transport()
    
    s1 = gen_session_key(data1[0], data2[1])
    s2 = gen_session_key(data2[0], data1[1])
    
    if s1 == s2:
        print("Test 1: Thank god, dh works\n" + str(data1) + "\n" + str(s1) + "\n" + str(s2) + "\n")
    else:
        print("Test 1: Oh no, something terrible has gone wrong with dh\n" + str(data1) + "\n" + str(s1) + "\n" + str(s2) + "\n")'''

    # Test encrypted key exchange, to implement PFS properly
    long_term_key = "abcdefghijklmnop"
    
    data1 = gen_public_transport(True, long_term_key)
    data2 = gen_public_transport(True, long_term_key)
    
    #s1 = gen_session_key(data1[PUB_TRANSPORT_IDX], data2[LOC_EXPONENT_IDX], True, long_term_key)
    '''s2 = gen_session_key(data2[PUB_TRANSPORT_IDX], data1[LOC_EXPONENT_IDX], True, long_term_key)
    
    if s1 == s2:
        print("Test 2: Thank god, dh works\n" + str(data1) + "\n" + str(s1) + "\n" + str(s2) + "\n")
    else:
        print("Test 2: Oh no, something terrible has gone wrong with dh\n" + str(data1) + "\n" + str(s1) + "\n" + str(s2) + "\n")'''
    
    return
    
    
def intToByteArray(inputInt):
    int_bytes = bytearray()
    idx = 0
    while inputInt > 0:
        int_bytes.append(inputInt % 256)
        inputInt = inputInt // 256        
        idx += 1
    #print(str(int_bytes))
       
    return int_bytes


def byteArrayToInt(int_bytes):
    ret_int = 0
    
    while(len(int_bytes) > 0):
        ret_int = ret_int*256 + int_bytes.pop()
        
    return ret_int
        
        
        
run_test() 


'''
    print(str(struct.pack('@P', 255)))
    print(str(struct.pack('P', 256)))
    print(str(struct.pack('P', 257)))
    
    
    #dh.intToByteArray(255)
    #dh.intToByteArray(256)
    #dh.intToByteArray(257)
    
    '''










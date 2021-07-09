import codecs
import hashlib
import json

import requests
from bitcoinaddress import Wallet
import threading


def base58(address_hex):
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    b58_string = ''
    # Get the number of leading zeros
    leading_zeros = len(address_hex) - len(address_hex.lstrip('0'))
    # Convert hex to decimal
    address_int = int(address_hex, 16)
    # Append digits to the start of string
    while address_int > 0:
        digit = address_int % 58
        digit_char = alphabet[digit]
        b58_string = digit_char + b58_string
        address_int //= 58
    # Add ‘1’ for each 2 leading zeros
    ones = leading_zeros // 2
    for one in range(ones):
        b58_string = '1' + b58_string
    return b58_string


def get_wallet_data(wallet_import_format):
    wallet = Wallet(wallet_import_format)
    address = wallet.address.__dict__.get('mainnet').__dict__.get('pubaddr1c')

    response = requests.get('https://blockchain.info/address/%s?format=json' % address)
    data = json.loads(response.text)
    r = data.get('total_received', 0)
    s = data.get('total_sent', 0)
    balance = r - s
    return {
        'wif': wallet_import_format,
        'address': address,
        'balance': balance,
        'is_valid': balance != 0 or r != 0
    }


def get_wif_by_hash(_hash):
    PK0 = _hash
    PK1 = '80' + PK0
    PK2 = hashlib.sha256(codecs.decode(PK1, 'hex'))
    PK3 = hashlib.sha256(PK2.digest())
    checksum = codecs.encode(PK3.digest(), 'hex')[0:8]
    PK4 = PK1 + str(checksum)[2:10]  # I know it looks wierd
    return base58(PK4)


def log(raw_content):
    def _log():
        file = open("log.txt", 'a')
        file.write(raw_content)
        file.close()
        print(raw_content)

    t = threading.Thread(target=_log)
    t.start()


def log_wallet_if_valid(_hash):
    wif = get_wif_by_hash(_hash)
    wallet_data = get_wallet_data(wif)
    if wallet_data.get('is_valid'):
        log("""\n
            ********************************************************
            WIF: %s
            address: %s
            balance: %f
            ________________________________________________________\n
            """ % (wif, wallet_data.get('address'), wallet_data.get('balance')))

        return True

    return False

class InvalidBlockHashException(Exception):
    pass


def get_block_data_by_hash(block_hash):
    # read cache
    try:
        block_file = open('blocks/%s.js' % block_hash)
        block_file_data = block_file.read()
        return json.loads(block_file_data)
    except FileNotFoundError:
        request = requests.get("https://blockchain.info/rawblock/%s" % block_hash)
        data = json.loads(request.text)
        if data.get('hash', None) == block_hash:
            block_file = open('blocks/%s.js' % block_hash, 'a')
            block_file.write(json.dumps(data))
            block_file.close()
            return data
        else:
            raise InvalidBlockHashException("Invalid Block hash")


def get_hashes_in_block(block_data, only_block_hash=False):
    if only_block_hash:
        return [block_data.get('hash'), ]

    hashes_in_block = [block_data.get('mrkl_root'), block_data.get('hash')]
    for _tx in block_data.get('tx'):
        hashes_in_block.append(_tx.get('hash'))
    return hashes_in_block

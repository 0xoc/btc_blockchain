from utils import log, InvalidBlockHashException, log_wallet_if_valid, get_block_data_by_hash, get_hashes_in_block


def main(end_block_hash, start_block_hash):
    block_hash = end_block_hash
    total = 0
    valid = 0
    while block_hash != start_block_hash:
        try:
            block_data = get_block_data_by_hash(block_hash)
            hashes_in_block = get_hashes_in_block(block_data)
            for _hash in hashes_in_block:
                is_valid = log_wallet_if_valid(_hash)
                if is_valid:
                    valid += 1

                total += 1
                print("%d / %d" % (valid, total))
            block_hash = block_data.get('prev_block')
        except InvalidBlockHashException:
            log("\nERROR: Invalid block hash %s\n" % block_hash)
            break

    print("DONE")


if __name__ == "__main__":
    main("00000000000000000004aa57bc9e5e71ccf5cd32577fde4fb2e996b9d028c850",
         "000000006a625f06636b8bb6ac7b960a8d03705d1ace08b1a19da3fdcc99ddbd")

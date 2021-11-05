from server import utils
from server import cache
import config,logging

class Transaction:
    @classmethod
    def broadcast(cls, raw: str):
        logging.info("Transaction.broadcast")
        return utils.make_request("sendrawtransaction", [raw])

    @classmethod
    @cache.memoize(timeout=config.cache)
    def decode(cls, raw: str):
        logging.info("Transaction.decode")
        return utils.make_request("decoderawtransaction", [raw])

    @classmethod
    def info(cls, thash: str):
        logging.info("Transaction.info")
        data = utils.make_request("getrawtransaction", [thash, True])

        if data["error"] is None:
            if "blockhash" in data["result"]:
                block = utils.make_request("getblock", [data["result"]["blockhash"]])["result"]
                data["result"]["height"] = block["height"]
            else:
                data["result"]["height"] = -1

            if data["result"]["height"] != 0:
                for index, vin in enumerate(data["result"]["vin"]):
                    if "txid" in vin:
                        vin_data = utils.make_request("getrawtransaction", [vin["txid"], True])
                        if vin_data["error"] is None:
                            data["result"]["vin"][index]["scriptPubKey"] = vin_data["result"]["vout"][vin["vout"]]["scriptPubKey"]
                            data["result"]["vin"][index]["value"] = utils.satoshis(vin_data["result"]["vout"][vin["vout"]]["value"])

            amount = 0
            for index, vout in enumerate(data["result"]["vout"]):
                data["result"]["vout"][index]["value"] = utils.satoshis(vout["value"])
                amount += vout["value"]

            data["result"]["amount"] = amount

        return data

    @classmethod
    @cache.memoize(timeout=config.cache)
    def addresses(cls, tx_data):
        logging.info("Transaction.addresses")
        updates = {}
        for tx in tx_data:
            transaction = Transaction.info(tx)
            vin = transaction["result"]["vin"]
            vout = transaction["result"]["vout"]

            for info in vin:
                if "scriptPubKey" in info:
                    if "addresses" in info["scriptPubKey"]:
                        for address in info["scriptPubKey"]["addresses"]:
                            if address in updates:
                                updates[address].append(tx)
                                updates[address] = list(set(updates[address]))
                            else:
                                updates[address] = [tx]

            for info in vout:
                if "scriptPubKey" in info:
                    if "addresses" in info["scriptPubKey"]:
                        for address in info["scriptPubKey"]["addresses"]:
                            if address in updates:
                                updates[address].append(tx)
                                updates[address] = list(set(updates[address]))
                            else:
                                updates[address] = [tx]

        return updates

    @classmethod
    def spent(cls, txid: str):
        logging.info("Transaction.spent")
        return utils.make_request("getspentinfo", [txid])

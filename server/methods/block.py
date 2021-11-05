from server.methods.transaction import Transaction
from server import utils
from server import cache
import config, logging

class Block():
    @classmethod
    def height(cls, height: int):
        logging.info("Block.height")
        data = utils.make_request("getblockhash", [height])

        if data["error"] is None:
            bhash = data["result"]
            data.pop("result")
            data["result"] = utils.make_request("getblock", [bhash])["result"]
            data["result"]["txcount"] = len(data["result"]["tx"])
            #data["result"].pop("nTx")

        return data

    @classmethod
    def hash(cls, bhash: str):
        logging.info("Block.hash")
        data = utils.make_request("getblock", [bhash])

        if data["error"] is None:
            data["result"]["txcount"] = len(data["result"]["tx"])
            #data["result"].pop("nTx")

        return data

    @classmethod
    @cache.memoize(timeout=config.cache)
    def get(cls, height: int):
        logging.info("Block.get")
        return utils.make_request("getblockhash", [height])

    @classmethod
    def range(cls, height: int, offset: int):
        logging.info("Block.range")
        result = []
        for block in range(height - (offset - 1), height + 1):
            data = utils.make_request("getblockhash", [block])
            nethash = utils.make_request("getnetworkhashps", [120, block])

            if data["error"] is None and nethash["error"] is None:
                bhash = data["result"]
                data.pop("result")

                block = utils.make_request("getblock", [bhash])
                if block["error"] is not None:
                    continue

                data["result"] = block["result"]
                data["result"]["nethash"] = int(nethash["result"])
                #data["result"]["txcount"] = data["result"]["nTx"]
                #data["result"]["txcount"] = len(data["result"]["tx"])
                #data["result"].pop("nTx")

                result.append(data["result"])

        return result[::-1]

    @classmethod
    @cache.memoize(timeout=config.cache)
    def inputs(cls, bhash: str):
        logging.info("Block.inputs")
        data = cls.hash(bhash)
        return Transaction.addresses(data["result"]["tx"])

from server import utils
from server import cache
import requests
import config

class General:
    @classmethod
    @cache.memoize(timeout=config.cache)
    def _calc_supply(cls, height):
        #snapshot = 443863973624633
        supply = 0

        for height in range(0, height + 1):
            supply += utils.reward(height)

        return {
            "supply": supply,
            "mining": supply,
            "height": height
        }

    @classmethod
    def info(cls):
        data = utils.make_request("getblockchaininfo")

        if data["error"] is None:
            #data["result"]["supply"] = cls._calc_supply(data["result"]["blocks"])["supply"]
            #data["result"]["reward"] = utils.reward(data["result"]["blocks"])
            data["result"].pop("verificationprogress")
            #data["result"].pop("initialblockdownload")
            data["result"].pop("pruned")
            data["result"].pop("softforks")
            data["result"].pop("bip9_softforks")
            data["result"].pop("warnings")
            data["result"].pop("size_on_disk")

            # nethash = utils.make_request("getnetworkhashps", [120, data["result"]["blocks"]])
            # if nethash["error"] is None:
            #     data["result"]["nethash"] = int(nethash["result"])

        return data

    # @classmethod
    # @cache.memoize(timeout=config.cache)
    # def supply(cls):
    #     data = utils.make_request("getblockchaininfo")
    #     height = data["result"]["blocks"]

    #     return cls._calc_supply(height)

    @classmethod
    def fee(cls):
        data = utils.make_request("estimatesmartfee", [6])

        if "errors" in data["result"]:
            return utils.response({
                "feerate": utils.satoshis(0.0001),
                "blocks": 6
            })

        data["result"]["feerate"] = utils.satoshis(data["result"]["feerate"])

        return data

    @classmethod
    def mempool(cls):
        data = utils.make_request("getmempoolinfo")

        if data["error"] is None:
            if data["result"]["size"] > 0:
                mempool = utils.make_request("getrawmempool")["result"]
                data["result"]["tx"] = mempool
            else:
                data["result"]["tx"] = []

        return data

    @classmethod
    def price(cls):
        link = "https://www.exbitron.com/api/v2/peatio/public/markets/rvlusdt/tickers"
        return requests.get(link).json()

from proxybroker import Broker
import asyncio
import aiohttp
import random
from termcolor import cprint


class ProxyList:
    def __init__(self, debug, num_proxies):
        self.debug = debug
        self.proxy_list = []
        self.num_proxies = num_proxies

        if self.debug:
            cprint(f"[DEBUG] Finding proxies...", "grey", attrs=["bold"])

        self._populate()

    def get(self):
        """ Getter for the populated proxy list """
        return self.proxy_list

    def random(self):
        """ Returns a random proxy from the list """
        try:
            proxy = random.choice(self.proxy_list)
        except IndexError:
            # This means the list is empty, probably because they've all failed
            cprint(f"[DEBUG] Ran out of proxies! Repopulating list!",
                   "red", attrs=["bold"])
            self._populate()

        return proxy

    def remove(self, entry):
        self.proxy_list.remove(entry)

    def _populate(self):
        """ Called on init, populates self.proxy_list """
        proxies = asyncio.Queue()
        broker = Broker(proxies)
        tasks = asyncio.gather(
            broker.find(types=['HTTP', 'HTTPS'], limit=self.num_proxies),
            self._add(proxies))
        loop = asyncio.get_event_loop()
        success = None
        try:
            # Try to complete the task
            success = loop.run_until_complete(tasks)
        except aiohttp.client_exceptions.ClientConnectorError:
            # Ignore the exception, we'll just try again
            pass

        # Try again if not successful
        if not success:
            if self.debug:
                cprint(f"[DEBUG] Loop failed, retrying!",
                       "red", attrs=["bold"])
            self._populate()

    async def _add(self, proxies):
        while True:
            proxy = await proxies.get()
            if proxy is None:
                break

            if self.debug:
                cprint(
                    f"[DEBUG] Added proxy {proxy.host}:{proxy.port} to pool!", "grey", attrs=["bold"])

            self.proxy_list.append(proxy)

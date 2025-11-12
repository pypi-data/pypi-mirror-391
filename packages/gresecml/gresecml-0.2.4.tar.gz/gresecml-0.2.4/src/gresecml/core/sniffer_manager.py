from scapy.all import Packet, AsyncSniffer
from queue import Empty, Queue
from typing import Iterator

def sniff_packets(iface: str = None, timeout: float = 10) -> Iterator[Packet]:
        queue = Queue()

        sniffer = AsyncSniffer(iface=iface, timeout=timeout, store=True, prn=lambda x: queue.put_nowait(x))
        sniffer.start()

        while sniffer.running:
            try:
                yield queue.get(block=False)
            except Empty:
                # no packet available yet, loop again until overall timeout
                continue

        # Wait for the sniffer to finish
        sniffer.join()

        # Get any remaining packets from the queue
        while not queue.empty():
            yield queue.get(block=False)

        # Stop the sniffer if it's still running
        try:
            sniffer.stop()
        except Exception:
            pass
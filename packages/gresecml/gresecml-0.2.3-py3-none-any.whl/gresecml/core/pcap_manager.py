from scapy.all import PcapReader, rdpcap, Packet

def read_packets(pcap_file_path: str) -> list[Packet]:
        try:
            packets = rdpcap(pcap_file_path)
            return packets
        except Exception as e:
            raise ValueError("Not a valid pcap file or unable to read the file.")
        
def lazy_read_packets(pcap_file_path: str):
        try:
            with PcapReader(pcap_file_path) as pcap_reader:
                for packet in pcap_reader:
                    yield packet
        except Exception as e:
            raise ValueError("Not a valid pcap file or unable to read the file.")

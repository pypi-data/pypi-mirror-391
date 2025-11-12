from scapy.packet import Packet as Scapy_packet
from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.layers.dns import DNS
from scapy.all import *

class GrePacket:
    def __init__(self, scapy_packet: Scapy_packet):
        self.sid = None
        self.scapy_packet: Scapy_packet = scapy_packet

        self.set_sid()

    def set_sid(self):
        if self.sid == None:
            sorted_ips: List[str] = sorted([self.src_ip, self.dst_ip])
            sorted_ports: List[str] = sorted([self.src_port, self.dst_port])

            self.sid = (sorted_ips[0], sorted_ips[1], sorted_ports[0], sorted_ports[1])

    @property
    def src_ip(self) -> str:
        if self.scapy_packet.haslayer(IP):
            return self.scapy_packet[IP].src
        return "0.0.0.0"

    @property
    def dst_ip(self) -> str:
        if self.scapy_packet.haslayer(IP):
            return self.scapy_packet[IP].dst
        return "0.0.0.0"

    @property
    def src_port(self) -> str:
        if self.scapy_packet.haslayer(TCP):
            return (str)(self.scapy_packet[TCP].sport)
        elif self.scapy_packet.haslayer(ICMP) and self.scapy_packet[ICMP].type == 3:
            inner = IP(bytes(self.scapy_packet[ICMP].payload))
            return (str)(inner[UDP].sport) if inner.haslayer(UDP) else "0"
        elif self.scapy_packet.haslayer(UDP):
            return (str)(self.scapy_packet[UDP].sport)
        return "0"

    @property
    def dst_port(self) -> str:
        if self.scapy_packet.haslayer(TCP):
            return (str)(self.scapy_packet[TCP].dport)
        elif self.scapy_packet.haslayer(ICMP) and self.scapy_packet[ICMP].type == 3:
            inner = IP(bytes(self.scapy_packet[ICMP].payload))
            return (str)(inner[UDP].dport) if inner.haslayer(UDP) else "0"
        elif self.scapy_packet.haslayer(UDP):
            return (str)(self.scapy_packet[UDP].dport)
        return "0"
    
    @property
    def is_unreachable_dest(self) -> bool:
        return self.scapy_packet.haslayer(ICMP) and self.scapy_packet[ICMP].type == 3

    @property
    def protocol(self) -> str:
        if self.scapy_packet.haslayer(IP):
            if self.scapy_packet.haslayer(UDP):
                return "UDP"
            elif self.scapy_packet.haslayer(TCP):
                return "TCP"
            elif self.scapy_packet.haslayer(ICMP):
                return "ICMP"
            return "Other"
        return "Other"

    @property
    def flag(self) -> str:
        if self.scapy_packet.haslayer(TCP):
            flags = self.scapy_packet[TCP].flags

            if flags & 0x02 and flags & 0x10:
                return "SYN-ACK"
            elif flags & 0x10 and flags & 0x08:
                return "PSH-ACK"
            elif flags & 0x01 and flags & 0x10:
                return "FIN-ACK"
            elif flags & 0x04 and flags & 0x10:
                return "RST-ACK"
            elif flags == 0x02:
                return "SYN"
            elif flags == 0x10:
                return "ACK"
            elif flags == 0x04:
                return "RST"
            elif flags == 0x01:
                return "FIN"
            elif flags == 0x08:
                return "PSH"
            elif flags == 0x20:
                return "URG"
            else:
                return "OTHER"
        return "None"
    
    @property
    def is_dns(self) -> bool:
        return self.scapy_packet.haslayer(DNS)

    @property
    def length(self) -> int:
        return len(self.scapy_packet)

    @property
    def window_size(self) -> int:
        if self.scapy_packet.haslayer(TCP):
            return self.scapy_packet[TCP].window
        return 0
    
    @property
    def inter_arrival(self) -> float | None:
        if self.prev is not None:
            return self.scapy_packet.time - self.prev.scapy_packet.time
        return None
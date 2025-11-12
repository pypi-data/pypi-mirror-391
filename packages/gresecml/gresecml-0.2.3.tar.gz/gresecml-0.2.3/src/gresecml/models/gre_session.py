import time
from gresecml.models.gre_packet import GrePacket

class GreSession:

    gre_packets: list[GrePacket]

    def __init__(self):
        self.gre_packets: list[GrePacket] = []
        self.lastest_arrival: float = 0.0

    def add_packet(self, packet: GrePacket):
        # Add the packet to the session
        self.gre_packets.append(packet)
        # Update latest arrival time for session timeout tracking
        self.lastest_arrival = time.time()

    @property
    def session_sid(self) -> tuple:
        if len(self.gre_packets) > 0:
            return self.gre_packets[0].sid
        else:
            return tuple()

    @property
    def packets(self) -> list[GrePacket]:
        return self.gre_packets
    
    @property
    def successful_connection(self) -> bool:
        # Check if session contains a successful TCP handshake (SYN, SYN-ACK, ACK)
        if len(self.gre_packets) > 0:
            sorted_packets = sorted(self.gre_packets, key=lambda p: p.scapy_packet.time)

        if sorted_packets[0].protocol == "TCP":
            syn_seen = False
            syn_ack_seen = False
            ack_seen = False

            for packet in sorted_packets:
                if packet.flag == "SYN":
                    syn_seen = True
                elif packet.flag == "SYN-ACK" and syn_seen:
                    syn_ack_seen = True
                elif packet.flag == "ACK" and syn_ack_seen:
                    ack_seen = True
                    break

            return syn_seen and syn_ack_seen and ack_seen
        elif sorted_packets[0].protocol == "UDP":
            if self.num_of_dest_unreachable == 0:
                return True
            else:
                return False
        elif sorted_packets[0].protocol == "ICMP":
            return True
        return False
    
    @property
    def num_of_dest_unreachable(self) -> int:
        return sum(1 for packet in self.gre_packets if packet.is_unreachable_dest)

# IPs
    @property
    def first_src_ip(self) -> str:
        if len(self.gre_packets) > 0:
            return self.gre_packets[0].src_ip
        return ""

    @property
    def first_dst_ip(self) -> str:
        if len(self.gre_packets) > 0:
            return self.gre_packets[0].dst_ip
        return ""

# Ports
    @property
    def first_src_port(self) -> int:
        if len(self.gre_packets) > 0:
            return self.gre_packets[0].src_port
        return 0
    
    @property
    def first_dst_port(self) -> int:
        if len(self.gre_packets) > 0:
            return self.gre_packets[0].dst_port
        return 0

# Protocols
    @property
    def first_protocol(self) -> str:
        if len(self.gre_packets) > 0:
            return self.gre_packets[0].protocol
        return "None"
    
    @property
    def protocol_tcp_count(self) -> int:
        return sum(1 for packet in self.gre_packets if packet.protocol == "TCP")

    @property
    def protocol_udp_count(self) -> int:
        return sum(1 for packet in self.gre_packets if packet.protocol == "UDP")

    @property
    def protocol_icmp_count(self) -> int:
        return sum(1 for packet in self.gre_packets if packet.protocol == "ICMP")

    @property
    def protocol_other_count(self) -> int:
        return sum(1 for packet in self.gre_packets if packet.protocol not in ["TCP", "UDP", "ICMP"])

# Flags
    @property
    def flag_syn_count(self) -> int:
        return sum(1 for packet in self.gre_packets if packet.flag == "SYN")

    @property
    def flag_syn_ack_count(self) -> int:
        return sum(1 for packet in self.gre_packets if packet.flag == "SYN-ACK")

    @property
    def flag_psh_ack_count(self) -> int:
        return sum(1 for packet in self.gre_packets if packet.flag == "PSH-ACK")

    @property
    def flag_fin_ack_count(self) -> int:
        return sum(1 for packet in self.gre_packets if packet.flag == "FIN-ACK")

    @property
    def flag_rst_ack_count(self) -> int:
        return sum(1 for packet in self.gre_packets if packet.flag == "RST-ACK")

    @property
    def flag_rst_count(self) -> int:
        return sum(1 for packet in self.gre_packets if packet.flag == "RST")

    @property
    def flag_fin_count(self) -> int:
        return sum(1 for packet in self.gre_packets if packet.flag == "FIN")

    @property
    def flag_ack_count(self) -> int:
        return sum(1 for packet in self.gre_packets if packet.flag == "ACK")

    @property
    def flag_psh_count(self) -> int:
        return sum(1 for packet in self.gre_packets if packet.flag == "PSH")

    @property
    def flag_urg_count(self) -> int:
        return sum(1 for packet in self.gre_packets if packet.flag == "URG")

    @property
    def flag_other_count(self) -> int:
        return sum(1 for packet in self.gre_packets if packet.flag == "OTHER")

# Number of DNS Queries
    @property
    def dns_query_count(self) -> int:
        return sum(1 for packet in self.gre_packets if packet.is_dns)

# Time
    @property
    def total_time(self) -> float:
        if len(self.gre_packets) > 1:
            ordered_packets = sorted(self.gre_packets, key=lambda p: p.scapy_packet.time)
            return ordered_packets[-1].scapy_packet.time - ordered_packets[0].scapy_packet.time
        return 0.0
    
    @property
    def mean_time(self) -> float:
        if len(self.gre_packets) > 1:
            return self.total_time / len(self.gre_packets)
        return 0.0
    
    @property
    def std_time(self) -> float:
        if len(self.gre_packets) > 1:
            mean = self.mean_time
            variance = sum((packet.scapy_packet.time - mean) ** 2 for packet in self.gre_packets) / len(self.gre_packets)
            return variance ** 0.5
        return 0.0
    
    @property
    def first_packet_time(self) -> float:
        if len(self.gre_packets) > 0:
            ordered_packets = sorted(self.gre_packets, key=lambda p: p.scapy_packet.time)
            return ordered_packets[0].scapy_packet.time
        return 0.0
    
    @property
    def last_packet_time(self) -> float:
        if len(self.gre_packets) > 0:
            ordered_packets = sorted(self.gre_packets, key=lambda p: p.scapy_packet.time)
            return ordered_packets[-1].scapy_packet.time
        return 0.0

# Flow
    @property
    def flow_pr_sec(self) -> float:
        if len(self.gre_packets) > 0:
            ordered_packets = sorted(self.gre_packets, key=lambda p: p.scapy_packet.time)
            total_bytes = sum(packet.length for packet in ordered_packets)
            total_time = ordered_packets[-1].scapy_packet.time - ordered_packets[0].scapy_packet.time
            if total_time > 0:
                return total_bytes / total_time
        return 0.0
    
    @property
    def fwd_flow_pr_sec(self) -> float:
        if len(self.gre_packets) > 0:
            ordered_packets = sorted(self.gre_packets, key=lambda p: p.scapy_packet.time)
            total_bytes = sum(packet.length for packet in ordered_packets if packet.src_ip == self.first_src_ip)
            total_time = ordered_packets[-1].scapy_packet.time - ordered_packets[0].scapy_packet.time
            if total_time > 0:
                return total_bytes / total_time
        return 0.0

    @property
    def bwd_flow_pr_sec(self) -> float:
        if len(self.gre_packets) > 0:
            ordered_packets = sorted(self.gre_packets, key=lambda p: p.scapy_packet.time)
            total_bytes = sum(packet.length for packet in ordered_packets if packet.src_ip == self.first_dst_ip)
            total_time = ordered_packets[-1].scapy_packet.time - ordered_packets[0].scapy_packet.time
            if total_time > 0:
                return total_bytes / total_time
        return 0.0

# Lengths
    @property
    def length(self) -> int:
        if len(self.gre_packets) > 0:
            return sum(packet.length for packet in self.gre_packets)
        return 0
    
    @property
    def fwd_length(self) -> int:
        if len(self.gre_packets) > 0:
            return sum(packet.length for packet in self.gre_packets if packet.src_ip == self.first_src_ip)
        return 0
    
    @property
    def bwd_length(self) -> int:
        if len(self.gre_packets) > 0:
            return sum(packet.length for packet in self.gre_packets if packet.src_ip == self.first_dst_ip)
        return 0
    
    @property
    def length_mean(self) -> float:
        if len(self.gre_packets) > 0:
            #Gennemsnit af længder
            return sum(packet.length for packet in self.gre_packets) / len(self.gre_packets)
        return 0.0

    @property
    def length_min(self) -> float:
        if len(self.gre_packets) > 0:
            return min(packet.length for packet in self.gre_packets)
        return 0.0

    @property
    def length_max(self) -> float:
        if len(self.gre_packets) > 0:
            return max(packet.length for packet in self.gre_packets)
        return 0.0
    
    @property
    def length_std(self) -> float:
        if len(self.gre_packets) > 0:
            # Gennemsnit
            mean = self.length_mean
            # Finder varians, gennemsnittet af de kvadrerede afvigelser fra middelværdien
            variance = sum((packet.length - mean) ** 2 for packet in self.gre_packets) / len(self.gre_packets)
            # Kvadratroden af variansen for at finde standardafvigelsen
            return variance ** 0.5
        return 0.0

# Packet counts
    @property
    def packet_count(self) -> int:
        return len(self.gre_packets)
    
# Inter arrival times
    @property
    def inter_arrival_times(self) -> list[float]:
        inter_arrivals = []
        if len(self.gre_packets) > 1:
            ordered_packets = sorted(self.gre_packets, key=lambda p: p.scapy_packet.time)
            for i in range(1, len(ordered_packets)):
                inter_arrival = ordered_packets[i].scapy_packet.time - ordered_packets[i-1].scapy_packet.time
                inter_arrivals.append(inter_arrival)
        return inter_arrivals


    @property
    def inter_arrival_mean(self) -> float:
        inter_arrivals = self.inter_arrival_times
        if len(inter_arrivals) > 0:
            return sum(inter_arrivals) / len(inter_arrivals)
        return 0.0
    
    @property
    def inter_arrival_min(self) -> float:
        inter_arrivals = self.inter_arrival_times
        if len(inter_arrivals) > 0:
            return min(inter_arrivals)
        return 0.0
    
    @property
    def inter_arrival_max(self) -> float:
        inter_arrivals = self.inter_arrival_times
        if len(inter_arrivals) > 0:
            return max(inter_arrivals)
        return 0.0
    
    @property
    def inter_arrival_variance(self) -> float:
        inter_arrivals = self.inter_arrival_times
        if len(inter_arrivals) > 0:
            mean = sum(inter_arrivals) / len(inter_arrivals)
            variance = sum((iat - mean) ** 2 for iat in inter_arrivals) / len(inter_arrivals)
            return variance
        return 0.0
    
    @property
    def inter_arrival_std(self) -> float:
        return self.inter_arrival_variance ** 0.5

    


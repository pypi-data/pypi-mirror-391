import time
import pandas as pd
from typing import Iterator
from scapy.all import TCP, UDP, ICMP, IP, Packet
from gresecml.models.gre_packet import GrePacket
from gresecml.models.gre_session import GreSession
import gresecml.core.pcap_manager as pcap_manager
import gresecml.core.sniffer_manager as sniffer_manager

class SessionManager:
    def __init__(self, tcp_timeout=300, tcp_rst_fin_timeout=20, udp_timeout=60.0, icmp_timeout=60.0):
        self.sessions: dict[tuple, GreSession] = {}
        self.open_sessions: dict[tuple, float] = {}
        self.closing_sessions: dict[tuple, float] = {}
        self.tcp_timeout: float = tcp_timeout # Timeout for established TCP sessions
        self.tcp_rst_fin_timeout: float = tcp_rst_fin_timeout # Timeout for closing TCP sessions (FIN, RST)
        self.udp_timeout: float = udp_timeout # Timeout for inactive UDP sessions
        self.icmp_timeout: float = icmp_timeout # Timeout for inactive ICMP sessions
        self.dataframes_for_export: list[pd.DataFrame] = []

    def start_processing(self, packets: Iterator[Packet]) -> Iterator[pd.DataFrame]:
        self.sessions.clear()
        self.open_sessions.clear()
        self.closing_sessions.clear()

        for packet in packets:
            gre_packet = GrePacket(packet)
            # Håndter pakken baseret på dens protokol
            try:
                self.handle_gre_packet(gre_packet)
            except Exception as e:
                # Burde logge fejl her
                continue

            # Eksporter dataframes hvis der er nogen
            for df in self.export_dataframes():
                yield df

        # Eksporter alle resterende sessioner efter pcap er færdig
        for sid in list(self.sessions.keys()):
            try:
                self.add_to_export(sid)
            except Exception as e:
                # Burde logge fejl her
                continue

        # Eksporter sidste dataframes hvis der er nogen
        for df in self.export_dataframes():
            yield df

#------------------------------------------------------------------------------------------------------------------------------------------------
# ---- Hjælpe metoder ----
#------------------------------------------------------------------------------------------------------------------------------------------------
    def handle_gre_packet(self, gre_packet: GrePacket) -> None:
        if not gre_packet.scapy_packet.haslayer(IP):
            # Ingen IPv6 support
            return
        if gre_packet.scapy_packet.haslayer(TCP):
            self.handle_tcp(gre_packet)
        elif gre_packet.scapy_packet.haslayer(UDP):
            self.handle_udp(gre_packet)
        elif gre_packet.scapy_packet.haslayer(ICMP): 
            self.handle_icmp(gre_packet)
        else:
            return

    # Starter en ny session
    def start_session(self, packet: GrePacket) -> None:
        self.sessions[packet.sid] = GreSession()
        self.add_packet_to_session(packet)
        self.mark_open_session(packet.sid)

    # Tilføjer en pakke til en eksisterende session
    def add_packet_to_session(self, packet: GrePacket) -> None:
        self.sessions[packet.sid].add_packet(packet)

    # Marker en session som åben - til at fange første dele af tcp forbindelsen ved SYN
    def mark_open_session(self, sid) -> None:
        self.open_sessions[sid] = time.time()

    # Marker en session som lukker - til at fange sidste dele af tcp forbindelsen ved FIN-ACK
    def mark_closing_session(self, sid) -> None:
        if sid in self.open_sessions:
            del self.open_sessions[sid]
        self.closing_sessions[sid] = time.time()

#------------------------------------------------------------------------------------------------------------------------------------------------
# ---- Håndtering af pakker efter protokol ----
#------------------------------------------------------------------------------------------------------------------------------------------------

    def handle_tcp(self, gre_packet: GrePacket) -> None:
        # Tjek om timeouts er overskredet for åbne sessions
        for sid in self.open_sessions.copy():
            if self.open_sessions[sid] + self.tcp_timeout < time.time():
                self.mark_closing_session(sid)

        # Tjek om timeouts er overskredet for closing sessions
        for sid in self.closing_sessions.copy():
            if self.closing_sessions[sid] + self.tcp_rst_fin_timeout < time.time():
                self.add_to_export(sid)

        # Håndter SYN pakker - start ny session eller eksporter eksisterende før ny session startes
        if gre_packet.flag == "SYN" and gre_packet.sid not in self.sessions:
            self.start_session(gre_packet)
            return
        elif gre_packet.flag == "SYN" and gre_packet.sid in self.sessions:
            self.add_to_export(gre_packet.sid)
            self.start_session(gre_packet)
            return
        
        # Hvis sessionen eksisterer, tilføj pakken
        if gre_packet.sid in self.sessions:
            self.add_packet_to_session(gre_packet)
            if gre_packet.flag == "FIN":
                self.mark_closing_session(gre_packet.sid)
            elif gre_packet.flag == "RST":
                self.mark_closing_session(gre_packet.sid)
        #Hvis ikke-syn sessions også skal med
        else:
            self.start_session(gre_packet)
            
    def handle_udp(self, gre_packet: GrePacket) -> None:
        if gre_packet.sid in self.sessions:
            if gre_packet.scapy_packet.time - self.sessions[gre_packet.sid].first_packet_time < self.udp_timeout:
                self.add_packet_to_session(gre_packet)
            else:
                self.add_to_export(gre_packet.sid)
                self.start_session(gre_packet)
        else:
            self.start_session(gre_packet)

    def handle_icmp(self, gre_packet: GrePacket) -> None:
        if gre_packet.sid in self.sessions:
            if gre_packet.scapy_packet.time - self.sessions[gre_packet.sid].first_packet_time < self.icmp_timeout:
                self.add_packet_to_session(gre_packet)
            else:
                self.add_to_export(gre_packet.sid)
                self.start_session(gre_packet)
        else:
            self.start_session(gre_packet)

#------------------------------------------------------------------------------------------------------------------------------------------------
# ---- Eksport af sessioner ----
#------------------------------------------------------------------------------------------------------------------------------------------------

    def add_to_export(self, session_id: str) -> None:
        if session_id in self.sessions:
            # Fjern sessionen fra aktiv liste
            session = self.sessions.pop(session_id)
            
            # Fjern fra åbne sessions hvis den er der
            if session_id in self.open_sessions:
                del self.open_sessions[session_id]
            
            # Fjern fra closing sessions hvis den er der
            if session_id in self.closing_sessions:
                del self.closing_sessions[session_id]
            
            # Eksporter session data som dataframe
            data = {
                "src_ip": (str)(session.first_src_ip),
                "dst_ip": (str)(session.first_dst_ip),
                "src_port": (str)(session.first_src_port),
                "dst_port": (str)(session.first_dst_port),
                "packets_total": (int)(session.packet_count),
                "time_total": (float)(session.total_time),
                "bytes_total": (int)(session.length),
                "bytes_mean": (float)(session.length_mean),
                "bytes_std": (float)(session.length_std),
                "bytes_fwd": (int)(session.fwd_length),
                "bytes_bwd": (int)(session.bwd_length),
                "flow_pr_sec": (float)(session.flow_pr_sec),
                "inter_arrival_mean": (float)(session.inter_arrival_mean),
                "inter_arrival_std": (float)(session.inter_arrival_std),
                "inter_arrival_min": (float)(session.inter_arrival_min),
                "inter_arrival_max": (float)(session.inter_arrival_max),
                "protocol": (str)(session.first_protocol),
                "flag_syn_count": (int)(session.flag_syn_count),
                "flag_ack_count": (int)(session.flag_ack_count),
                "flag_fin_count": (int)(session.flag_fin_count),
                "flag_rst_count": (int)(session.flag_rst_count),
                "flag_dns_count": (int)(session.dns_query_count),
                "successful_connection": (str)(session.successful_connection),
                "num_of_dest_unreachable": (int)(session.num_of_dest_unreachable)
            }
            # Tilføj data til eksport listen
            self.dataframes_for_export.append(pd.DataFrame([data]))


    def export_dataframes(self) -> Iterator[pd.DataFrame]:
        for session in self.dataframes_for_export:
            yield session
        self.dataframes_for_export.clear()
    

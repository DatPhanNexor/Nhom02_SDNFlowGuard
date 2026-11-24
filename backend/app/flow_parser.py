"""
SDNFlowGuard OpenFlow 1.3 Flow Criteria Parser & Normalizer
Adheres strictly to ONOS 2.7 REST Flow representation and OpenFlow 1.3 Match Semantics.

Phase B Requirements:
- IPV4_SRC -> source_ip (preserves CIDR prefix, e.g. 10.0.0.1/32)
- IPV4_DST -> destination_ip (preserves CIDR prefix)
- IPV6_SRC -> source_ip
- IPV6_DST -> destination_ip
- ETH_SRC / ETH_DST -> source_mac / destination_mac (Never converted to IP)
- IN_PORT -> in_port
- ETH_TYPE, IP_PROTO, TCP_SRC, TCP_DST, UDP_SRC, UDP_DST retained accurately
- Does NOT infer IP from host inventory, ARP cache, or topology
- Absent IP is represented as None (UI displays N/A with explanation)
- Does NOT convert wildcard to specific IP
"""

ETH_TYPE_MAP = {
    "0x800": "IPv4",
    "0x0800": "IPv4",
    "0x806": "ARP",
    "0x0806": "ARP",
    "0x86dd": "IPv6",
    "0x86DD": "IPv6",
    "0x88cc": "LLDP",
    "0x88CC": "LLDP",
    "0x8942": "BDDP",
    "0x8847": "MPLS",
    "0x8100": "VLAN",
}

IP_PROTO_MAP = {
    1: "ICMP",
    2: "IGMP",
    6: "TCP",
    17: "UDP",
    58: "IPv6-ICMP",
    89: "OSPF",
}


def parse_onos_flow(flow: dict) -> dict:
    """Parse a single raw ONOS flow entry into a standardized SDNFlowGuard flow dictionary.
    
    Guarantees zero-regression with existing API contracts while providing
    complete OpenFlow 1.3 match criteria and treatment visibility.
    """
    if not isinstance(flow, dict):
        flow = {}

    selector = flow.get("selector", {})
    criteria_list = selector.get("criteria", []) if isinstance(selector, dict) else []
    if not isinstance(criteria_list, list):
        criteria_list = []

    criteria_map = {}
    for item in criteria_list:
        if isinstance(item, dict) and "type" in item:
            criteria_map[item["type"]] = item

    # 1. L3 IP Matching (Preserve CIDR prefix if present; never infer from external sources)
    source_ip = None
    if "IPV4_SRC" in criteria_map:
        source_ip = criteria_map["IPV4_SRC"].get("ip")
    elif "IPV6_SRC" in criteria_map:
        source_ip = criteria_map["IPV6_SRC"].get("ip")

    destination_ip = None
    if "IPV4_DST" in criteria_map:
        destination_ip = criteria_map["IPV4_DST"].get("ip")
    elif "IPV6_DST" in criteria_map:
        destination_ip = criteria_map["IPV6_DST"].get("ip")

    # 2. L2 Ethernet Addresses (Strictly MAC; never converted to IP)
    source_mac = criteria_map.get("ETH_SRC", {}).get("mac")
    destination_mac = criteria_map.get("ETH_DST", {}).get("mac")

    # 3. Ports & Protocols
    in_port = criteria_map.get("IN_PORT", {}).get("port")
    eth_type = criteria_map.get("ETH_TYPE", {}).get("ethType")
    ip_proto = criteria_map.get("IP_PROTO", {}).get("protocol")

    # 4. L4 Transport Ports
    tcp_src = criteria_map.get("TCP_SRC", {}).get("tcpPort")
    tcp_dst = criteria_map.get("TCP_DST", {}).get("tcpPort")
    udp_src = criteria_map.get("UDP_SRC", {}).get("udpPort")
    udp_dst = criteria_map.get("UDP_DST", {}).get("udpPort")

    # 5. Build Human-Readable Match Criteria Summary
    match_parts = []
    if in_port is not None:
        match_parts.append(f"IN_PORT: {in_port}")
    if eth_type:
        eth_str = str(eth_type).lower()
        desc = ETH_TYPE_MAP.get(eth_str, eth_type)
        match_parts.append(f"ETH_TYPE: {eth_type} ({desc})")
    if source_mac:
        match_parts.append(f"ETH_SRC: {source_mac}")
    if destination_mac:
        match_parts.append(f"ETH_DST: {destination_mac}")
    if source_ip:
        match_parts.append(f"SRC_IP: {source_ip}")
    if destination_ip:
        match_parts.append(f"DST_IP: {destination_ip}")
    if ip_proto is not None:
        proto_desc = IP_PROTO_MAP.get(ip_proto, f"Proto {ip_proto}")
        match_parts.append(f"IP_PROTO: {ip_proto} ({proto_desc})")
    if tcp_src is not None or tcp_dst is not None:
        match_parts.append(f"TCP: {tcp_src or '*'}:{tcp_dst or '*'}")
    if udp_src is not None or udp_dst is not None:
        match_parts.append(f"UDP: {udp_src or '*'}:{udp_dst or '*'}")

    # Catch any additional criteria types (e.g. VLAN, ICMP)
    standard_types = {
        "IPV4_SRC", "IPV4_DST", "IPV6_SRC", "IPV6_DST",
        "ETH_SRC", "ETH_DST", "IN_PORT", "ETH_TYPE",
        "IP_PROTO", "TCP_SRC", "TCP_DST", "UDP_SRC", "UDP_DST",
    }
    for c_type, c_val in criteria_map.items():
        if c_type not in standard_types:
            val = next((v for k, v in c_val.items() if k != "type"), "")
            match_parts.append(f"{c_type}: {val}" if val else c_type)

    match_summary = ", ".join(match_parts) if match_parts else "WILDCARD (Match All)"

    # 6. Treatment Parsing (Outputs, Drop, Controller)
    treatment = flow.get("treatment", {})
    instructions = treatment.get("instructions", []) if isinstance(treatment, dict) else []
    if not isinstance(instructions, list):
        instructions = []

    output_ports = []
    for item in instructions:
        if isinstance(item, dict) and item.get("type") == "OUTPUT" and item.get("port") is not None:
            output_ports.append(str(item.get("port")))

    other_instructions = [
        item.get("type")
        for item in instructions
        if isinstance(item, dict) and item.get("type") != "OUTPUT"
    ]

    if output_ports:
        treatment_summary = f"OUTPUT: {', '.join(output_ports)}"
    elif other_instructions:
        treatment_summary = ", ".join(other_instructions)
    else:
        treatment_summary = "DROP"

    priority = flow.get("priority", 0)
    table_id = flow.get("tableId", 0)
    is_table_miss = (priority == 0 and not criteria_list)
    has_ip_match = bool(source_ip or destination_ip)

    return {
        # Contract-preserved fields
        "id": str(flow.get("id", "")),
        "device_id": str(flow.get("deviceId", "")),
        "app_id": str(flow.get("appId", "")),
        "state": str(flow.get("state", "ADDED")),
        "priority": priority,
        "source_ip": source_ip,
        "destination_ip": destination_ip,
        "source_mac": source_mac,
        "destination_mac": destination_mac,
        "packets": int(flow.get("packets", 0)),
        "bytes": int(flow.get("bytes", 0)),
        "life_seconds": int(flow.get("life", 0)),
        "output_ports": output_ports,
        # Enhanced OpenFlow 1.3 match & metadata fields
        "table_id": table_id,
        "table_name": str(flow.get("tableName", table_id)),
        "in_port": in_port,
        "eth_type": eth_type,
        "ip_proto": ip_proto,
        "match_criteria": match_summary,
        "criteria_raw": criteria_list,
        "has_ip_match": has_ip_match,
        "is_table_miss": is_table_miss,
        "treatment_summary": treatment_summary,
    }

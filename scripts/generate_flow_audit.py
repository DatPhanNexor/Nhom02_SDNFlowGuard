import json

try:
    with open('raw_onos_flows.json', 'r', encoding='utf-16') as f:
        flows = json.load(f).get('flows', [])
except Exception:
    with open('raw_onos_flows.json', 'r', encoding='utf-8') as f:
        flows = json.load(f).get('flows', [])

print('| # | Flow ID | Device ID | App ID | Table | Priority | Raw Match Criteria | Raw Treatment | Src IP | Dst IP | Reason No IP |')
print('|---|---|---|---|---|---|---|---|---|---|---|')

for idx, fl in enumerate(flows):
    fid = fl.get('id')
    dev = fl.get('deviceId')
    app = fl.get('appId')
    tbl = fl.get('tableId', 0)
    pri = fl.get('priority')
    crit = fl.get('selector', {}).get('criteria', [])
    crit_str = ', '.join([f"{c.get('type')}={c.get('ethType') or c.get('ip') or c.get('mac') or c.get('port') or ''}" for c in crit]) if crit else 'EMPTY (WILDCARD)'
    
    ins_list = fl.get('treatment', {}).get('instructions', [])
    treat_str = ', '.join([ins.get('type') + (f":{ins.get('port')}" if 'port' in ins else '') for ins in ins_list]) or 'DROP/CLEAR'
    
    # check ip
    crit_map = {c.get('type'): c for c in crit}
    src_ip = crit_map.get('IPV4_SRC', {}).get('ip') or crit_map.get('IPV6_SRC', {}).get('ip') or 'N/A'
    dst_ip = crit_map.get('IPV4_DST', {}).get('ip') or crit_map.get('IPV6_DST', {}).get('ip') or 'N/A'
    
    eth_type = crit_map.get('ETH_TYPE', {}).get('ethType')
    if eth_type == '0x88cc':
        reason = 'LLDP Discovery Rule (L2 only, ethType 0x88cc)'
    elif eth_type == '0x8942':
        reason = 'BDDP Discovery Rule (L2 only, ethType 0x8942)'
    elif eth_type == '0x806':
        reason = 'ARP Resolution Rule (L2/L3 ARP punt, ethType 0x806)'
    elif eth_type == '0x800':
        reason = 'IPv4 Wildcard Rule (Punt unhandled IPv4 to Controller fwd, no L3 IP filter)'
    else:
        reason = 'Non-IP criteria'
        
    print(f'| {idx+1} | {fid} | {dev} | {app} | {tbl} | {pri} | {crit_str} | {treat_str} | {src_ip} | {dst_ip} | {reason} |')

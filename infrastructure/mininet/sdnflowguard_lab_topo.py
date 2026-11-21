#!/usr/bin/env python3
"""Reproducible OpenFlow 1.3 Mininet lab topology for SDNFlowGuard.

Supported Topologies:
    1. 'reference' / 'demo_6s9h' (Default):
       6 OpenFlow switches (s1..s6) and 9 network hosts (h1..h9)
       designed for enterprise NOC/SOC visualization & defense evaluation.
    2. 'single': Single switch with N hosts (default: 3).
    3. 'linear': Linear chain of K switches with N hosts.

Usage inside WSL2 Ubuntu (or Linux lab host):
    sudo python3 infrastructure/mininet/sdnflowguard_lab_topo.py --topo reference --daemon
    sudo python3 infrastructure/mininet/sdnflowguard_lab_topo.py --topo reference --cli
    sudo python3 infrastructure/mininet/sdnflowguard_lab_topo.py --topo single --hosts 3
"""

from __future__ import annotations

import argparse
import signal
import sys
import time


def get_reference_topo_class():
    from mininet.topo import Topo

    class SDNFlowGuard6S9HTopo(Topo):
        """6 OpenFlow switches (s1..s6) and 9 network hosts (h1..h9).
        
        Architecture:
            Core Layer:
                s1 (Core-West, DPID 0000000000000001)
                s2 (Core-East, DPID 0000000000000002)
            Distribution Layer:
                s3 (West Distribution, DPID 0000000000000003)
                s4 (South-West Distribution, DPID 0000000000000004)
                s5 (East Distribution, DPID 0000000000000005)
                s6 (South-East Distribution, DPID 0000000000000006)
            
            Inter-Switch Links (Loop-free connected tree graph):
                s1 <-> s2 (Core Trunk)
                s1 <-> s3 (West Distribution)
                s1 <-> s4 (South-West Distribution)
                s2 <-> s5 (East Distribution)
                s2 <-> s6 (South-East Distribution)
                
            End Hosts (9 hosts with clean non-conflicting IP/MAC mapping):
                s1:
                    h1 (10.0.0.1, 00:00:00:00:00:01) -> Client / Step 63 attacker
                    h2 (10.0.0.2, 00:00:00:00:00:02) -> Server / Step 63 target
                s3:
                    h3 (10.0.0.3, 00:00:00:00:00:03) -> Host 3
                s4:
                    h4 (10.0.0.4, 00:00:00:00:00:04) -> Host 4
                    h5 (10.0.0.5, 00:00:00:00:00:05) -> Host 5
                s2:
                    h6 (10.0.0.6, 00:00:00:00:00:06) -> Internal Honeypot host
                s5:
                    h7 (10.0.0.7, 00:00:00:00:00:07) -> Host 7
                    h8 (10.0.0.8, 00:00:00:00:00:08) -> Host 8
                s6:
                    h9 (10.0.0.9, 00:00:00:00:00:09) -> Host 9
        """

        def build(self):
            # 1. Add 6 OpenFlow switches
            s1 = self.addSwitch("s1", dpid="0000000000000001")
            s2 = self.addSwitch("s2", dpid="0000000000000002")
            s3 = self.addSwitch("s3", dpid="0000000000000003")
            s4 = self.addSwitch("s4", dpid="0000000000000004")
            s5 = self.addSwitch("s5", dpid="0000000000000005")
            s6 = self.addSwitch("s6", dpid="0000000000000006")

            # 2. Add inter-switch links (tree backbone)
            self.addLink(s1, s2)
            self.addLink(s1, s3)
            self.addLink(s1, s4)
            self.addLink(s2, s5)
            self.addLink(s2, s6)

            # 3. Add 9 hosts
            h1 = self.addHost("h1", ip="10.0.0.1/24", mac="00:00:00:00:00:01")
            h2 = self.addHost("h2", ip="10.0.0.2/24", mac="00:00:00:00:00:02")
            h3 = self.addHost("h3", ip="10.0.0.3/24", mac="00:00:00:00:00:03")
            h4 = self.addHost("h4", ip="10.0.0.4/24", mac="00:00:00:00:00:04")
            h5 = self.addHost("h5", ip="10.0.0.5/24", mac="00:00:00:00:00:05")
            h6 = self.addHost("h6", ip="10.0.0.6/24", mac="00:00:00:00:00:06")
            h7 = self.addHost("h7", ip="10.0.0.7/24", mac="00:00:00:00:00:07")
            h8 = self.addHost("h8", ip="10.0.0.8/24", mac="00:00:00:00:00:08")
            h9 = self.addHost("h9", ip="10.0.0.9/24", mac="00:00:00:00:00:09")

            # 4. Attach hosts to switches
            self.addLink(h1, s1)
            self.addLink(h2, s1)
            self.addLink(h3, s3)
            self.addLink(h4, s4)
            self.addLink(h5, s4)
            self.addLink(h6, s2)
            self.addLink(h7, s5)
            self.addLink(h8, s5)
            self.addLink(h9, s6)

    return SDNFlowGuard6S9HTopo


def build_and_run(
    topo_mode: str,
    host_count: int,
    switch_count: int,
    controller_ip: str,
    controller_port: int,
    is_daemon: bool = False,
    run_cli: bool = False,
) -> int:
    try:
        from mininet.cli import CLI
        from mininet.log import info, setLogLevel
        from mininet.net import Mininet
        from mininet.node import OVSSwitch, RemoteController
        from mininet.topo import LinearTopo, SingleSwitchTopo
    except ImportError as exc:
        print(f"ERROR: Mininet Python package is not available on this host: {exc}", file=sys.stderr)
        return 1

    setLogLevel("info")

    if topo_mode in ("reference", "demo_6s9h", "6s9h"):
        ref_cls = get_reference_topo_class()
        topo = ref_cls()
    elif topo_mode == "linear":
        topo = LinearTopo(k=switch_count, n=max(1, host_count // max(1, switch_count)))
    else:
        topo = SingleSwitchTopo(k=host_count)

    net = Mininet(
        topo=topo,
        controller=lambda name: RemoteController(name, ip=controller_ip, port=controller_port),
        switch=lambda name, **kwargs: OVSSwitch(name, protocols="OpenFlow13", **kwargs),
        autoSetMacs=False,
        autoStaticArp=False,
    )

    keep_running = True

    def sig_handler(_signum, _frame):
        nonlocal keep_running
        info("\n*** Received shutdown signal, stopping Mininet cleanly...\n")
        keep_running = False

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    try:
        info(f"*** Starting SDNFlowGuard lab topology ({topo_mode}) -> ONOS {controller_ip}:{controller_port}\n")
        net.start()

        info("*** Allowing OpenFlow handshake and LLDP link discovery to settle (3s)...\n")
        time.sleep(3)

        info("*** Running initial pingall to trigger ONOS host discovery...\n")
        loss = net.pingAll()
        info(f"*** PingAll completed with loss: {loss}%\n")

        # Explicit gratuitous ARP to ensure ONOS Host Service records all hosts
        info("*** Sending host announcement ARPs to ONOS Host Service...\n")
        for h in net.hosts:
            h.cmd(f"arping -c 1 -A -I {h.name}-eth0 {h.IP()} > /dev/null 2>&1")

        if run_cli:
            info("*** Entering Mininet Interactive CLI...\n")
            CLI(net)
        elif is_daemon:
            info("*** Topology active in background daemon mode. Preserving dataplane state...\n")
            # Write status file for external verification
            try:
                with open("/tmp/sdnflowguard_topo.status", "w") as f:
                    f.write(f"RUNNING|{topo_mode}|switches={len(net.switches)}|hosts={len(net.hosts)}|time={int(time.time())}\n")
            except Exception:
                pass

            cycle = 0
            while keep_running:
                time.sleep(2)
                cycle += 1
                # Periodically re-announce hosts every 60s to maintain ONOS host lease
                if cycle % 30 == 0:
                    for h in net.hosts:
                        h.cmd(f"arping -c 1 -A -I {h.name}-eth0 {h.IP()} > /dev/null 2>&1")
        else:
            info("*** Lab test execution completed.\n")

    finally:
        info("*** Stopping Mininet network and cleaning up dataplane...\n")
        net.stop()
        try:
            import os
            if os.path.exists("/tmp/sdnflowguard_topo.status"):
                os.remove("/tmp/sdnflowguard_topo.status")
        except Exception:
            pass

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SDNFlowGuard OpenFlow 1.3 Mininet Lab Topology")
    parser.add_argument(
        "--topo",
        choices=("reference", "demo_6s9h", "6s9h", "single", "linear"),
        default="reference",
        help="Topology layout (default: reference - 6 switches & 9 hosts)",
    )
    parser.add_argument("--hosts", type=int, default=3, help="Number of hosts for single/linear topo (default: 3)")
    parser.add_argument("--switches", type=int, default=2, help="Number of switches for linear topo (default: 2)")
    parser.add_argument("--controller-ip", default="127.0.0.1", help="ONOS controller IP (default: 127.0.0.1)")
    parser.add_argument("--controller-port", type=int, default=6653, help="ONOS OpenFlow port (default: 6653)")
    parser.add_argument("--daemon", action="store_true", help="Keep topology alive in background daemon mode")
    parser.add_argument("--cli", action="store_true", help="Launch interactive Mininet CLI")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(
        build_and_run(
            topo_mode=args.topo,
            host_count=args.hosts,
            switch_count=args.switches,
            controller_ip=args.controller_ip,
            controller_port=args.controller_port,
            is_daemon=args.daemon,
            run_cli=args.cli,
        )
    )

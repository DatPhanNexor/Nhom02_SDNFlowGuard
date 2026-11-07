import React, { useEffect, useRef, useState } from 'react';
import { Network } from 'vis-network';
import axios from 'axios';
import OnosLiveFlows from './OnosLiveFlows';
import { API_BASE_URL } from '../config/apiConfig';
import { useLanguage } from '../i18n/LanguageContext';
import './TrafficOverview.css';

function TrafficOverview() {
  const { language, t } = useLanguage();
  const networkRef = useRef(null);
  const [topologyData, setTopologyData] = useState({
    devices: [],
    hosts: [],
    links: [],
  });
  const [topologyError, setTopologyError] = useState('');
  const [flowData, setFlowData] = useState([]);

  useEffect(() => {
    const fetchTopology = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/topology`);
        setTopologyData({
          devices: Array.isArray(response.data?.devices)
            ? response.data.devices
            : [],
          hosts: Array.isArray(response.data?.hosts)
            ? response.data.hosts
            : [],
          links: Array.isArray(response.data?.links)
            ? response.data.links
            : [],
        });
        setTopologyError('');
      } catch (error) {
        setTopologyError(t('trafficOverview.topologyUnavailable'));
      }
    };

    fetchTopology();
  }, [t]);

  useEffect(() => {
    const fetchFlows = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/get-flows`);
        setFlowData(
          Array.isArray(response.data?.data) ? response.data.data : []
        );
      } catch (error) {
        setFlowData([]);
      }
    };

    fetchFlows();
  }, []);

  useEffect(() => {
    const nodes = [];
    const edges = [];
    const processedConnections = new Set();

    const devices = Array.isArray(topologyData.devices)
      ? topologyData.devices
      : [];
    const hosts = Array.isArray(topologyData.hosts) ? topologyData.hosts : [];
    const links = Array.isArray(topologyData.links) ? topologyData.links : [];

    devices.forEach((device, index) => {
      nodes.push({
        id: device.id,
        label: `Switch ${index + 1}\n(${device.id})`,
        shape: 'box',
        color: {
          background: '#0f172a',
          border: '#38bdf8',
          highlight: { background: '#1e293b', border: '#0284c7' },
        },
        font: { color: '#ffffff', size: 12, face: 'monospace' },
        margin: 10,
      });
    });

    hosts.forEach((host, index) => {
      const ips = Array.isArray(host.ipAddresses) ? host.ipAddresses : [];
      const primaryIp = ips[0] || `Host ${index + 1}`;
      nodes.push({
        id: host.id,
        label: `${primaryIp}\n${host.mac || ''}`,
        shape: 'ellipse',
        color: {
          background: '#e0f2fe',
          border: '#0284c7',
          highlight: { background: '#bae6fd', border: '#0369a1' },
        },
        font: { color: '#0f172a', size: 12, face: 'sans-serif' },
        margin: 8,
      });

      const locations = Array.isArray(host.locations) ? host.locations : [];
      locations.forEach((location) => {
        edges.push({
          from: location.elementId,
          to: host.id,
          label: `port ${location.port}`,
          font: { size: 10, color: '#64748b' },
          color: { color: '#94a3b8' },
        });
      });
    });

    links.forEach((link) => {
      if (!link?.src?.device || !link?.dst?.device) return;
      const connectionId = [link.src.device, link.dst.device].sort().join('-');
      if (!processedConnections.has(connectionId)) {
        processedConnections.add(connectionId);
        edges.push({
          from: link.src.device,
          to: link.dst.device,
          smooth: false,
          color: { color: '#0284c7', width: 2 },
        });
      }
    });

    const options = {
      nodes: {
        shadow: true,
      },
      edges: {
        smooth: false,
        shadow: false,
      },
      physics: {
        stabilization: {
          enabled: true,
        },
      },
      interaction: {
        hover: true,
      },
    };

    if (nodes.length > 0 && networkRef.current) {
      const network = new Network(
        networkRef.current,
        { nodes, edges },
        options
      );
      return () => {
        network.destroy();
      };
    }
  }, [topologyData]);

  return (
    <div className="traffic-overview">
      <div style={{ marginBottom: 20 }}>
        <h2 style={{ margin: 0, color: '#0f172a', fontSize: '1.6rem', fontWeight: 700 }}>
          {t('trafficOverview.title')}
        </h2>
        <p style={{ margin: '4px 0 0 0', color: '#64748b', fontSize: 14 }}>
          {language === 'vi'
            ? 'Trực quan hóa topo mạng SDN và bảng luồng chuyển tiếp OpenFlow 1.3'
            : 'Visual SDN network topology and OpenFlow 1.3 flow rule telemetry'}
        </p>
      </div>

      {topologyError && (
        <div
          style={{
            background: '#fef3c7',
            color: '#92400e',
            padding: '10px 14px',
            borderRadius: 6,
            marginBottom: 14,
            fontSize: 13,
            border: '1px solid #fde68a'
          }}
        >
          {topologyError}
        </div>
      )}

      {/* Network Topology Visualizer */}
      <div className="topology-section" style={{ background: '#fff', padding: 20, borderRadius: 10, border: '1px solid #e2e8f0', marginBottom: 24, boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <h3 style={{ margin: 0, color: '#0f172a', fontSize: '1.15rem', fontWeight: 700 }}>
            {t('trafficOverview.topologySection')}
          </h3>
          <span style={{ fontSize: 12, color: '#64748b' }}>
            {topologyData.devices.length} {language === 'vi' ? 'switch' : 'switch(es)'} | {topologyData.hosts.length} {language === 'vi' ? 'host' : 'host(s)'}
          </span>
        </div>
        <div className="network-container" ref={networkRef} style={{ height: '340px', border: '1px solid #f1f5f9', borderRadius: 8, background: '#f8fafc' }}></div>
      </div>

      {/* Live ONOS Flows */}
      <OnosLiveFlows />

      {/* Stored Flow Table (SQLite) */}
      <div className="traffic-details" style={{ background: '#fff', padding: 20, borderRadius: 10, border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <h3 style={{ margin: 0, color: '#0f172a', fontSize: '1.15rem', fontWeight: 700 }}>
            {t('trafficOverview.storedFlowsTitle')} ({flowData.length})
          </h3>
          <span style={{ fontSize: 12, color: '#64748b' }}>
            {language === 'vi' ? 'Lưu trữ SQLite cục bộ' : 'Internal SQLite Storage'}
          </span>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table>
            <thead>
              <tr style={{ background: '#f8fafc' }}>
                <th>{t('trafficOverview.tableHeaders.sourceIp')}</th>
                <th>{t('trafficOverview.tableHeaders.destinationIp')}</th>
                <th>{t('trafficOverview.tableHeaders.protocol')}</th>
                <th>{t('trafficOverview.tableHeaders.priority')}</th>
                <th>{t('trafficOverview.tableHeaders.appId')}</th>
                <th>{t('trafficOverview.tableHeaders.deviceId')}</th>
                <th>{t('trafficOverview.tableHeaders.bytes')}</th>
                <th>{t('trafficOverview.tableHeaders.duration')}</th>
              </tr>
            </thead>
            <tbody>
              {flowData.length === 0 ? (
                <tr>
                  <td colSpan={8} style={{ textAlign: 'center', padding: '24px', color: '#64748b' }}>
                    {t('trafficOverview.noStoredFlows')}
                  </td>
                </tr>
              ) : (
                flowData.map((flow, index) => (
                  <tr key={index}>
                    <td>
                      <code>
                        {flow.source_ip ||
                          (flow.protocol === 'ARP'
                            ? t('trafficOverview.arpBroadcast')
                            : flow.protocol === 'LLDP'
                            ? t('trafficOverview.lldpDiscovery')
                            : t('trafficOverview.l2ControlFlow'))}
                      </code>
                    </td>
                    <td>
                      <code>
                        {flow.destination_ip ||
                          (flow.protocol === 'ARP'
                            ? 'Broadcast (FF:FF:..)'
                            : flow.protocol === 'LLDP'
                            ? 'LLDP Multicast'
                            : t('trafficOverview.l2ControlFlow'))}
                      </code>
                    </td>
                    <td>
                      <span style={{ padding: '2px 6px', borderRadius: 4, background: '#f1f5f9', fontWeight: 600, fontSize: 11 }}>
                        {flow.protocol || 'ETH'}
                      </span>
                    </td>
                    <td>{flow.priority}</td>
                    <td><code>{flow.app_id}</code></td>
                    <td><code>{flow.device_id}</code></td>
                    <td>{Number(flow.bandwidth || 0).toLocaleString()} bytes</td>
                    <td>{flow.flow_duration} ms</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default TrafficOverview;

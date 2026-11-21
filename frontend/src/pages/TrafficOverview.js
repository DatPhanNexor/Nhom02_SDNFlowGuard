import React, { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import { Network } from 'vis-network';
import axios from 'axios';
import OnosLiveFlows from './OnosLiveFlows';
import { API_BASE_URL } from '../config/apiConfig';
import { useLanguage } from '../i18n/LanguageContext';
import { useTheme } from '../theme/ThemeContext';
import './TrafficOverview.css';

const TOPOLOGY_POLL_INTERVAL_MS = 5000;

// High-fidelity vector network device icons (SVG Data URIs)
const SWITCH_ICON_ONLINE =
  'data:image/svg+xml;charset=utf-8,' +
  encodeURIComponent(`
<svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" viewBox="0 0 60 60">
  <rect x="3" y="10" width="54" height="40" rx="8" fill="#0f172a" stroke="#38bdf8" stroke-width="2.5"/>
  <circle cx="11" cy="18" r="2.5" fill="#10b981"/>
  <circle cx="18" cy="18" r="2.5" fill="#10b981"/>
  <path d="M16 30 h28 M38 25 l6 5 -6 5" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M44 40 h-28 M22 35 l-6 5 6 5" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="45" y="20" fill="#38bdf8" font-family="monospace" font-size="7" font-weight="bold" text-anchor="middle">SDN</text>
</svg>
`);

const SWITCH_ICON_OFFLINE =
  'data:image/svg+xml;charset=utf-8,' +
  encodeURIComponent(`
<svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" viewBox="0 0 60 60">
  <rect x="3" y="10" width="54" height="40" rx="8" fill="#334155" stroke="#94a3b8" stroke-width="2"/>
  <circle cx="11" cy="18" r="2.5" fill="#ef4444"/>
  <circle cx="18" cy="18" r="2.5" fill="#ef4444"/>
  <path d="M16 30 h28 M38 25 l6 5 -6 5" fill="none" stroke="#64748b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M44 40 h-28 M22 35 l-6 5 6 5" fill="none" stroke="#64748b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="45" y="20" fill="#94a3b8" font-family="monospace" font-size="7" font-weight="bold" text-anchor="middle">OFF</text>
</svg>
`);

const HOST_ICON =
  'data:image/svg+xml;charset=utf-8,' +
  encodeURIComponent(`
<svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" viewBox="0 0 60 60">
  <rect x="8" y="8" width="44" height="32" rx="5" fill="#0f172a" stroke="#0284c7" stroke-width="2.5"/>
  <rect x="13" y="13" width="34" height="22" rx="2" fill="#0284c7" fill-opacity="0.2"/>
  <line x1="17" y1="20" x2="31" y2="20" stroke="#38bdf8" stroke-width="2" stroke-linecap="round"/>
  <line x1="17" y1="26" x2="25" y2="26" stroke="#38bdf8" stroke-width="2" stroke-linecap="round"/>
  <path d="M26 40 v6 h-8 v3 h24 v-3 h-8 v-6 z" fill="#0284c7"/>
  <circle cx="44" cy="15" r="2" fill="#10b981"/>
</svg>
`);

function computeTopologyHash(data, filterMode, isDark) {
  if (!data) return '';
  const devPart = (data.devices || [])
    .map((d) => `${d.id}:${d.available !== false}`)
    .sort()
    .join(';');
  const hostPart = (data.hosts || [])
    .map((h) => {
      const ips = (h.ipAddresses || []).join(',');
      const locs = (h.locations || []).map((l) => `${l.elementId}:${l.port}`).sort().join(',');
      return `${h.id}:${h.mac}:${ips}:${locs}`;
    })
    .sort()
    .join(';');
  const linkPart = (data.links || [])
    .map((l) => `${l.src?.device}:${l.src?.port}->${l.dst?.device}:${l.dst?.port}`)
    .sort()
    .join(';');
  return `${filterMode}|${isDark ? 'dark' : 'light'}|${devPart}|${hostPart}|${linkPart}`;
}

function buildGraphElements(data, language, isDark) {
  const nodes = [];
  const edges = [];
  const processedLinkKeys = new Set();

  const devices = Array.isArray(data?.devices) ? data.devices : [];
  const hosts = Array.isArray(data?.hosts) ? data.hosts : [];
  const links = Array.isArray(data?.links) ? data.links : [];

  // 1. Switch Nodes with Network Device Vector Icons
  devices.forEach((device, index) => {
    const isAvailable = device.available !== false;
    const switchNum = index + 1;
    const shortId = device.id || `sw-${switchNum}`;
    const swName = device.annotations?.datapathDescription || `Switch ${switchNum}`;
    const statusText = isAvailable
      ? (language === 'vi' ? 'Trực tuyến (Khả dụng)' : 'Online (Available)')
      : (language === 'vi' ? 'Mất kết nối (Offline)' : 'Disconnected (Offline)');
    const offlineTag = isAvailable ? '' : (language === 'vi' ? ' [NGOẠI TUYẾN]' : ' [OFFLINE]');

    const tooltip = [
      `🏷️ Switch: ${swName} (${shortId})`,
      `📡 ${language === 'vi' ? 'Trạng thái' : 'Status'}: ${statusText}`,
      `💻 ${language === 'vi' ? 'Phần cứng' : 'Hardware'}: ${device.hw || 'Open vSwitch'} (${device.sw || '3.7.1'})`,
      `⚡ ${language === 'vi' ? 'Giao thức' : 'Protocol'}: ${device.annotations?.protocol || 'OF_13'}`,
      `⏱️ ${language === 'vi' ? 'Lần cuối thấy' : 'Last Seen'}: ${device.humanReadableLastUpdate || (language === 'vi' ? 'Đang hoạt động' : 'Active')}`,
    ].join('\n');

    nodes.push({
      id: device.id,
      label: `Switch ${switchNum}${offlineTag}\n(${shortId})`,
      shape: 'image',
      image: isAvailable ? SWITCH_ICON_ONLINE : SWITCH_ICON_OFFLINE,
      size: 38,
      title: tooltip,
      font: {
        color: isAvailable ? (isDark ? '#f8fafc' : '#0f172a') : (isDark ? '#94a3b8' : '#64748b'),
        size: 12,
        face: 'monospace',
        multi: true,
        bold: true,
        background: isDark ? '#172033' : '#ffffff',
        strokeWidth: 2,
        strokeColor: isAvailable ? (isDark ? '#334155' : '#e0f2fe') : (isDark ? '#1e293b' : '#e2e8f0'),
      },
      margin: 12,
    });
  });

  // 2. End Host Nodes with Workstation Vector Icons
  hosts.forEach((host, index) => {
    const ips = Array.isArray(host.ipAddresses) ? host.ipAddresses : [];
    const primaryIp = ips[0] || (language === 'vi' ? `Host ${index + 1}` : `Host ${index + 1}`);
    const mac = host.mac || '';
    const locations = Array.isArray(host.locations) ? host.locations : [];
    const locationDesc = locations.map((l) => `${l.elementId} (Port ${l.port})`).join(', ') || 'N/A';

    const tooltip = [
      `🖥️ ${language === 'vi' ? 'Thiết bị đầu cuối (Host)' : 'End Host'}: ${primaryIp}`,
      `🆔 ID: ${host.id}`,
      `🌐 IP: ${ips.join(', ') || (language === 'vi' ? 'Chưa cấp IP' : 'No IP')}`,
      `🏷️ MAC: ${mac}`,
      `🔌 ${language === 'vi' ? 'Điểm gắn mạng' : 'Attachment Point'}: ${locationDesc}`,
    ].join('\n');

    nodes.push({
      id: host.id,
      label: `${primaryIp}\n${mac}`,
      shape: 'image',
      image: HOST_ICON,
      size: 30,
      title: tooltip,
      font: {
        color: isDark ? '#f8fafc' : '#0f172a',
        size: 11,
        face: 'sans-serif',
        multi: true,
        background: isDark ? '#172033' : '#ffffff',
        strokeWidth: 2,
        strokeColor: isDark ? '#334155' : '#e0f2fe',
      },
      margin: 10,
    });

    // Host-to-Switch Edges (Dashed)
    locations.forEach((location) => {
      edges.push({
        id: `host-edge-${host.id}-${location.elementId}-${location.port}`,
        from: location.elementId,
        to: host.id,
        label: `port ${location.port}`,
        title: `${language === 'vi' ? 'Liên kết Host' : 'Host Link'}: ${primaryIp} <-> ${location.elementId} (Port ${location.port})`,
        font: {
          size: 10,
          color: isDark ? '#cbd5e1' : '#475569',
          background: isDark ? '#1e293b' : '#f8fafc',
          strokeWidth: 1,
          strokeColor: isDark ? '#334155' : '#cbd5e1',
        },
        color: { color: isDark ? '#38bdf8' : '#0284c7', highlight: '#0ea5e9' },
        dashes: [5, 5],
        width: 2,
      });
    });
  });

  // 3. Inter-switch Links (Preserving parallel physical links while deduplicating directed reverse pairs)
  links.forEach((link) => {
    if (!link?.src?.device || !link?.dst?.device) return;
    const srcDevice = link.src.device;
    const srcPort = link.src.port || '0';
    const dstDevice = link.dst.device;
    const dstPort = link.dst.port || '0';

    const ep1 = `${srcDevice}:${srcPort}`;
    const ep2 = `${dstDevice}:${dstPort}`;
    const linkKey = ep1 < ep2 ? `${ep1}<->${ep2}` : `${ep2}<->${ep1}`;

    if (!processedLinkKeys.has(linkKey)) {
      processedLinkKeys.add(linkKey);
      edges.push({
        id: `inter-switch-${linkKey}`,
        from: srcDevice,
        to: dstDevice,
        label: `p${srcPort} ⇄ p${dstPort}`,
        title: `${language === 'vi' ? 'Liên kết Trunk Switch' : 'Inter-Switch Link'}: ${srcDevice}:${srcPort} <-> ${dstDevice}:${dstPort} (${link.state || 'ACTIVE'})`,
        font: {
          size: 11,
          color: isDark ? '#38bdf8' : '#0369a1',
          background: isDark ? '#0c4a6e' : '#e0f2fe',
          strokeWidth: 1,
          strokeColor: isDark ? '#0284c7' : '#38bdf8',
        },
        color: { color: isDark ? '#38bdf8' : '#0284c7', highlight: '#0ea5e9' },
        width: 3.5,
        smooth: false,
        dashes: false,
      });
    }
  });

  return { nodes, edges };
}

function TrafficOverview() {
  const { language, t } = useLanguage();
  const { isDark } = useTheme();
  const networkRef = useRef(null);
  const networkInstanceRef = useRef(null);
  const lastTopologyHashRef = useRef('');
  const isMountedRef = useRef(true);
  const isFetchingRef = useRef(false);

  const [topologyData, setTopologyData] = useState({
    devices: [],
    hosts: [],
    links: [],
  });
  const [filterMode, setFilterMode] = useState('active_only'); // 'active_only' | 'all'
  const [controllerStatus, setControllerStatus] = useState('ONLINE');
  const [topologyError, setTopologyError] = useState('');
  const [lastUpdated, setLastUpdated] = useState('');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [flowData, setFlowData] = useState([]);
  const [physicsActive, setPhysicsActive] = useState(true);

  // Fetch Topology from Backend Gateway
  const fetchTopology = useCallback(async (isManual = false) => {
    if (isFetchingRef.current) return;
    isFetchingRef.current = true;
    if (isManual) setIsRefreshing(true);

    try {
      const response = await axios.get(`${API_BASE_URL}/api/topology`, { timeout: 4500 });
      if (!isMountedRef.current) return;

      const devices = Array.isArray(response.data?.devices) ? response.data.devices : [];
      const hosts = Array.isArray(response.data?.hosts) ? response.data.hosts : [];
      const links = Array.isArray(response.data?.links) ? response.data.links : [];

      setTopologyData({ devices, hosts, links });
      const isUnavailable = response.data?.controller_status === 'UNAVAILABLE';
      setControllerStatus(isUnavailable ? 'UNAVAILABLE' : 'ONLINE');
      setTopologyError(isUnavailable ? t('trafficOverview.topologyUnavailable') : '');
      setLastUpdated(new Date().toLocaleTimeString(language === 'vi' ? 'vi-VN' : 'en-US'));
    } catch (error) {
      if (!isMountedRef.current) return;
      setControllerStatus('UNAVAILABLE');
      setTopologyError(t('trafficOverview.topologyUnavailable'));
    } finally {
      isFetchingRef.current = false;
      if (isMountedRef.current) {
        setIsRefreshing(false);
      }
    }
  }, [t, language]);

  // Safe Polling Interval (every 5s)
  useEffect(() => {
    isMountedRef.current = true;
    fetchTopology();

    const intervalId = setInterval(() => {
      if (document.visibilityState === 'visible') {
        fetchTopology();
      }
    }, TOPOLOGY_POLL_INTERVAL_MS);

    return () => {
      isMountedRef.current = false;
      clearInterval(intervalId);
    };
  }, [fetchTopology]);

  // Fetch Stored SQLite Flow Table
  useEffect(() => {
    let mounted = true;
    const fetchFlows = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/get-flows`, { timeout: 4500 });
        if (mounted) {
          setFlowData(Array.isArray(response.data?.data) ? response.data.data : []);
        }
      } catch (error) {
        if (mounted) setFlowData([]);
      }
    };

    fetchFlows();
    const interval = setInterval(fetchFlows, 10000);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  // Filter topology elements based on active_only vs all
  const filteredTopologyData = useMemo(() => {
    const allDevices = topologyData.devices || [];
    const allHosts = topologyData.hosts || [];
    const allLinks = topologyData.links || [];

    if (filterMode === 'all') {
      return { devices: allDevices, hosts: allHosts, links: allLinks };
    }

    // Active Only: only include devices with available !== false
    const activeDevices = allDevices.filter(
      (d) => d.type === 'SWITCH' && d.available !== false
    );
    const activeDeviceIds = new Set(activeDevices.map((d) => d.id));

    // Include hosts attached to active devices
    const activeHosts = allHosts.filter((h) =>
      (h.locations || []).some((l) => activeDeviceIds.has(l.elementId))
    );

    // Include links between active devices
    const activeLinks = allLinks.filter(
      (l) => activeDeviceIds.has(l.src?.device) && activeDeviceIds.has(l.dst?.device)
    );

    return { devices: activeDevices, hosts: activeHosts, links: activeLinks };
  }, [topologyData, filterMode]);

  // Device status counters
  const onlineSwitchesCount = useMemo(
    () => topologyData.devices.filter((d) => d.type === 'SWITCH' && d.available !== false).length,
    [topologyData.devices]
  );
  const offlineSwitchesCount = useMemo(
    () => topologyData.devices.filter((d) => d.type === 'SWITCH' && d.available === false).length,
    [topologyData.devices]
  );

  // Update Vis-network In-Place
  useEffect(() => {
    const newHash = computeTopologyHash(filteredTopologyData, filterMode, isDark);
    const { nodes, edges } = buildGraphElements(filteredTopologyData, language, isDark);

    if (nodes.length === 0) {
      if (networkInstanceRef.current) {
        networkInstanceRef.current.destroy();
        networkInstanceRef.current = null;
      }
      lastTopologyHashRef.current = '';
      return;
    }

    // If topology data did not change, do nothing (no flickering, keep user zoom/pan)
    if (newHash === lastTopologyHashRef.current && networkInstanceRef.current) {
      return;
    }

    const options = {
      nodes: {
        shadow: true,
      },
      edges: {
        smooth: false,
        shadow: false,
      },
      physics: {
        enabled: physicsActive,
        stabilization: {
          enabled: true,
          iterations: 150,
          fit: true,
        },
        barnesHut: {
          gravitationalConstant: -4200,
          springLength: 170,
          springConstant: 0.04,
          damping: 0.09,
          centralGravity: 0.18,
        },
      },
      interaction: {
        hover: true,
        tooltipDelay: 150,
        zoomView: true,
        dragView: true,
      },
    };

    if (networkInstanceRef.current) {
      networkInstanceRef.current.setData({ nodes, edges });
    } else if (networkRef.current) {
      networkInstanceRef.current = new Network(networkRef.current, { nodes, edges }, options);
      // Auto-fit once upon initialization
      networkInstanceRef.current.once('stabilizationIterationsDone', () => {
        if (networkInstanceRef.current) {
          networkInstanceRef.current.fit({ animation: false });
        }
      });
    }

    lastTopologyHashRef.current = newHash;
  }, [filteredTopologyData, language, filterMode, isDark, physicsActive]);

  // Clean unmount
  useEffect(() => {
    return () => {
      if (networkInstanceRef.current) {
        networkInstanceRef.current.destroy();
        networkInstanceRef.current = null;
      }
    };
  }, []);

  // Zoom and pan control handlers
  const handleZoomIn = () => {
    if (networkInstanceRef.current) {
      const scale = networkInstanceRef.current.getScale();
      networkInstanceRef.current.moveTo({ scale: scale * 1.25, animation: { duration: 250 } });
    }
  };

  const handleZoomOut = () => {
    if (networkInstanceRef.current) {
      const scale = networkInstanceRef.current.getScale();
      networkInstanceRef.current.moveTo({ scale: scale * 0.8, animation: { duration: 250 } });
    }
  };

  const handleFitScreen = () => {
    if (networkInstanceRef.current) {
      networkInstanceRef.current.fit({
        animation: { duration: 400, easingFunction: 'easeInOutQuad' },
      });
    }
  };

  const handleTogglePhysics = () => {
    setPhysicsActive((prev) => {
      const next = !prev;
      if (networkInstanceRef.current) {
        networkInstanceRef.current.setOptions({ physics: { enabled: next } });
      }
      return next;
    });
  };

  const totalVisibleSwitches = filteredTopologyData.devices.length;
  const totalVisibleHosts = filteredTopologyData.hosts.length;
  const totalVisibleLinks = filteredTopologyData.links.length;

  return (
    <div className="traffic-overview">
      <div className="traffic-overview-container">
        {/* Header */}
        <div className="traffic-overview-header">
          <h2 className="traffic-overview-title">
            {t('trafficOverview.title')}
          </h2>
          <p className="traffic-overview-subtitle">
            {language === 'vi'
              ? 'Giám sát tôpô mạng SDN thời gian thực, trạng thái thiết bị chuyển mạch và vết luồng OpenFlow'
              : 'Real-time SDN network topology monitoring, switch states, and OpenFlow forwarding traces'}
          </p>
        </div>

        {/* Top Telemetry Control & Status Bar */}
        <div className="topology-controls-bar">
          <div className="topology-status-group">
            <span className={`controller-status-pill ${controllerStatus === 'ONLINE' ? 'online' : 'offline'}`}>
              <span className="pulsing-dot" />
              {controllerStatus === 'ONLINE' ? t('trafficOverview.controllerOnline') : t('trafficOverview.controllerOffline')}
            </span>

            {/* Filter Mode Toggle */}
            <div className="topology-filter-container">
              <button
                type="button"
                onClick={() => setFilterMode('active_only')}
                className={`topology-filter-btn ${filterMode === 'active_only' ? 'active' : ''}`}
                title={language === 'vi' ? 'Chỉ hiển thị các Switch đang kết nối hoạt động' : 'Show only active connected switches'}
              >
                {language === 'vi' ? 'Thiết bị hoạt động' : 'Active Only'}
              </button>
              <button
                type="button"
                onClick={() => setFilterMode('all')}
                className={`topology-filter-btn ${filterMode === 'all' ? 'active' : ''}`}
                title={language === 'vi' ? 'Hiển thị tất cả Switch (kể cả ngoại tuyến)' : 'Show all switches including offline'}
              >
                {language === 'vi' ? 'Tất cả thiết bị' : 'All Devices'}
              </button>
            </div>

            <span className="topology-stat-pill">
              🟢 {onlineSwitchesCount} {language === 'vi' ? 'Trực tuyến' : 'Online'}
              {offlineSwitchesCount > 0 && ` | ⚪ ${offlineSwitchesCount} ${language === 'vi' ? 'Ngoại tuyến' : 'Offline'}`}
            </span>

            <span className="topology-stat-pill">
              🖥️ {totalVisibleHosts} {t('trafficOverview.hostsCount')}
            </span>

            {totalVisibleLinks > 0 && (
              <span className="topology-stat-pill">
                🔗 {totalVisibleLinks} {t('trafficOverview.linksCount')}
              </span>
            )}
          </div>

          <div className="topology-actions-group">
            {lastUpdated && (
              <span className="last-updated-text">
                ⏱️ {t('trafficOverview.lastUpdated')} {lastUpdated}
              </span>
            )}
            <span className="auto-refresh-badge">
              🔄 {t('trafficOverview.autoRefresh')}
            </span>
            <button
              type="button"
              className="refresh-btn"
              onClick={() => fetchTopology(true)}
              disabled={isRefreshing}
            >
              {isRefreshing ? '⏳...' : `🔄 ${t('trafficOverview.refreshNow')}`}
            </button>
          </div>
        </div>

        {topologyError && (
          <div className="topology-error-banner" role="alert">
            ⚠️ {topologyError}
          </div>
        )}

        {/* Network Topology Visualizer Card */}
        <div className="traffic-card topology-card">
          <div className="card-header-bar">
            <div className="card-title-group">
              <h3 className="card-title">{t('trafficOverview.topologySection')}</h3>
              <span className="card-badge-count">
                {totalVisibleSwitches} {t('trafficOverview.switchesCount')} · {totalVisibleHosts} {t('trafficOverview.hostsCount')}
              </span>
            </div>

            {/* Canvas Zoom & View Controls Toolbar */}
            <div className="topology-toolbar">
              <button
                type="button"
                className="canvas-tool-btn"
                onClick={handleZoomIn}
                title={t('trafficOverview.zoomIn')}
                aria-label={t('trafficOverview.zoomIn')}
              >
                🔍+
              </button>
              <button
                type="button"
                className="canvas-tool-btn"
                onClick={handleZoomOut}
                title={t('trafficOverview.zoomOut')}
                aria-label={t('trafficOverview.zoomOut')}
              >
                🔍−
              </button>
              <button
                type="button"
                className="canvas-tool-btn"
                onClick={handleFitScreen}
                title={t('trafficOverview.fitScreen')}
                aria-label={t('trafficOverview.fitScreen')}
              >
                ⛶ {t('trafficOverview.fitScreen')}
              </button>
              <button
                type="button"
                className={`canvas-tool-btn ${physicsActive ? 'tool-active' : ''}`}
                onClick={handleTogglePhysics}
                title={t('trafficOverview.togglePhysics')}
                aria-label={t('trafficOverview.togglePhysics')}
              >
                ⚡ {physicsActive ? (language === 'vi' ? 'Vật lý: BẬT' : 'Physics: ON') : (language === 'vi' ? 'Vật lý: TẮT' : 'Physics: OFF')}
              </button>
            </div>
          </div>

          <div className="topology-canvas-wrapper">
            <div ref={networkRef} className="topology-canvas" />

            {/* Empty State Overlay when no switches are visible */}
            {totalVisibleSwitches === 0 && (
              <div className="topology-empty-overlay">
                <div className="empty-icon">🌐</div>
                <h4>{t('trafficOverview.noSwitchesTitle')}</h4>
                <p>{t('trafficOverview.noSwitchesDesc')}</p>
                <pre className="mininet-code-block">
sudo mn --topo single,3 --controller=remote,ip=127.0.0.1,port=6653 --switch ovsk,protocols=OpenFlow13
                </pre>
                <p className="mininet-tip">
                  💡 {language === 'vi'
                    ? 'Sau khi Mininet kết nối, gõ "pingall" trong terminal Mininet để kích hoạt cơ chế khám phá Host.'
                    : 'After Mininet connects, run "pingall" in the Mininet CLI to trigger host discovery.'}
                </p>
                {offlineSwitchesCount > 0 && filterMode === 'active_only' && (
                  <button
                    type="button"
                    onClick={() => setFilterMode('all')}
                    className="offline-switches-btn"
                  >
                    {language === 'vi'
                      ? `Xem ${offlineSwitchesCount} Switch ngoại tuyến đã lưu vết`
                      : `View ${offlineSwitchesCount} offline switches recorded`}
                  </button>
                )}
              </div>
            )}

            {/* Info Pill when switches are connected but no hosts discovered */}
            {totalVisibleSwitches > 0 && totalVisibleHosts === 0 && (
              <div className="topology-hosts-notice">
                ℹ️ {t('trafficOverview.noHostsNotice')}
              </div>
            )}
          </div>

          {/* Interactive Topology Legend Bar */}
          <div className="topology-legend-bar">
            <div className="legend-item">
              <span className="legend-indicator indicator-switch" />
              <span className="legend-label">{t('trafficOverview.legendSwitch')}</span>
            </div>
            <div className="legend-item">
              <span className="legend-indicator indicator-host" />
              <span className="legend-label">{t('trafficOverview.legendHost')}</span>
            </div>
            <div className="legend-item">
              <span className="legend-indicator indicator-trunk" />
              <span className="legend-label">{t('trafficOverview.legendTrunk')}</span>
            </div>
            <div className="legend-item">
              <span className="legend-indicator indicator-access" />
              <span className="legend-label">{t('trafficOverview.legendHostLink')}</span>
            </div>
          </div>
        </div>

        {/* Real-time ONOS Flow Rules Table Card */}
        <OnosLiveFlows />

        {/* Stored Flow Rules Table Card (SQLite History) */}
        <div className="traffic-card stored-flows-card">
          <div className="card-header-bar">
            <div className="card-title-group">
              <h3 className="card-title">{t('trafficOverview.storedFlowsTitle')}</h3>
              <span className="card-badge-count">
                {flowData.length} {t('common.records')}
              </span>
            </div>
            <p className="card-subtitle-inline">
              {language === 'vi'
                ? 'Cơ sở dữ liệu lưu trữ lịch sử các phiên lưu lượng mạng đã được ghi nhận vào SQLite.'
                : 'Persistent SQLite database log of historical network flow sessions.'}
            </p>
          </div>

          {flowData.length === 0 ? (
            <div className="table-empty-box">
              <p>{t('trafficOverview.noStoredFlows')}</p>
            </div>
          ) : (
            <div className="table-responsive-wrapper">
              <table className="noc-flow-table">
                <thead>
                  <tr>
                    <th style={{ minWidth: '130px' }}>{t('trafficOverview.tableHeaders.sourceIp')}</th>
                    <th style={{ minWidth: '130px' }}>{t('trafficOverview.tableHeaders.destinationIp')}</th>
                    <th style={{ minWidth: '90px' }}>{t('trafficOverview.tableHeaders.protocol')}</th>
                    <th className="col-num" style={{ minWidth: '80px' }}>{t('trafficOverview.tableHeaders.priority')}</th>
                    <th style={{ minWidth: '120px' }}>{t('trafficOverview.tableHeaders.appId')}</th>
                    <th style={{ minWidth: '130px' }}>{t('trafficOverview.tableHeaders.deviceId')}</th>
                    <th className="col-num" style={{ minWidth: '100px' }}>{t('trafficOverview.tableHeaders.bytes')}</th>
                    <th className="col-num" style={{ minWidth: '95px' }}>{t('trafficOverview.tableHeaders.duration')}</th>
                    <th className="col-num" style={{ minWidth: '95px' }}>{t('trafficOverview.tableHeaders.packets')}</th>
                    <th style={{ minWidth: '90px' }}>{t('trafficOverview.tableHeaders.state')}</th>
                    <th style={{ minWidth: '110px' }}>{t('trafficOverview.tableHeaders.output')}</th>
                  </tr>
                </thead>
                <tbody>
                  {flowData.map((flow, index) => {
                    const isAdded = flow.state === 'ADDED' || flow.state === 'ACTIVE';
                    return (
                      <tr key={index}>
                        <td>
                          {flow.source_ip ? (
                            <span className="flow-code-chip">{flow.source_ip}</span>
                          ) : (
                            <span className="dimmed-dash">—</span>
                          )}
                        </td>
                        <td>
                          {flow.destination_ip ? (
                            <span className="flow-code-chip">{flow.destination_ip}</span>
                          ) : (
                            <span className="dimmed-dash">—</span>
                          )}
                        </td>
                        <td>
                          <span className="proto-pill">{flow.protocol || '—'}</span>
                        </td>
                        <td className="col-num font-mono">{flow.priority ?? '—'}</td>
                        <td>
                          <span className="app-id-tag app-id-normal">{flow.app_id || '—'}</span>
                        </td>
                        <td>
                          <span className="device-id-chip" title={flow.device_id}>
                            {flow.device_id || '—'}
                          </span>
                        </td>
                        <td className="col-num font-mono">
                          {Number(flow.bytes || 0).toLocaleString()}
                        </td>
                        <td className="col-num font-mono">{flow.duration || '0s'}</td>
                        <td className="col-num font-mono">
                          {Number(flow.packets || 0).toLocaleString()}
                        </td>
                        <td>
                          <span className={`state-badge ${isAdded ? 'state-added' : 'state-pending'}`}>
                            {flow.state || 'ACTIVE'}
                          </span>
                        </td>
                        <td>
                          {flow.output_port ? (
                            <span className={`port-chip ${flow.output_port === 'CONTROLLER' ? 'port-controller' : 'port-normal'}`}>
                              {flow.output_port}
                            </span>
                          ) : (
                            <span className="dimmed-dash">—</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default TrafficOverview;

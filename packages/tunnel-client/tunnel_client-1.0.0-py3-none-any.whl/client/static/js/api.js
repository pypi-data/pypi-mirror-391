export async function fetchList({ method = '', status = '', path = '' } = {}) {
  const params = new URLSearchParams();
  if (method) params.set('method', method);
  if (status) params.set('status', status);
  const url = `/api/requests?${params.toString()}`;
  const res = await fetch(url);
  const data = await res.json();
  let items = data.items || [];
  if (path) {
    const q = path.toLowerCase();
    items = items.filter(i => (i.url || '').toLowerCase().includes(q));
  }
  return items;
}

export async function fetchDetails(id) {
  const res = await fetch(`/api/requests/${id}`);
  return await res.json();
}

export async function clearAll() {
  await fetch('/api/requests', { method: 'DELETE' });
}

export function connectWS(onCreated) {
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  const ws = new WebSocket(`${proto}://${location.host}/ws`);
  ws.onmessage = ev => {
    try {
      const msg = JSON.parse(ev.data);
      if (msg.type === 'created') onCreated?.(msg.item);
    } catch {}
  };
  return ws;
}

export async function getSettings(){
  const res = await fetch('/api/settings');
  return await res.json();
}

export async function updateSettings(payload){
  await fetch('/api/settings', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload) });
}

export async function generateSubdomain(){
  const res = await fetch('/api/generate-subdomain', { method: 'POST' });
  if(!res.ok) throw new Error('Failed to generate subdomain');
  return await res.json();
}

export async function getConnectionStatus(){
  const res = await fetch('/api/connection/status');
  if(!res.ok) return { status: 'unknown', connected: false };
  return await res.json();
}

export async function replayRequestRaw({ method, url, headers, body }){
  const res = await fetch('/api/replay', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ method, url, headers, body }) });
  if(!res.ok) throw new Error(`Replay failed: ${res.status}`);
  return await res.json();
}

export async function replayRequestById(id, overrides = {}){
  const res = await fetch(`/api/requests/${id}/replay`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(overrides) });
  if(!res.ok) throw new Error(`Replay failed: ${res.status}`);
  return await res.json();
}

// TCP/UDP
export async function fetchTcpStreams(){
  const res = await fetch('/api/tcp/streams');
  return await res.json();
}

export async function fetchTcpEvents(streamId, limit=200){
  const res = await fetch(`/api/tcp/streams/${encodeURIComponent(streamId)}/events?limit=${limit}`);
  return await res.json();
}

export async function tcpSend(streamId, data, mode='text'){
  const res = await fetch(`/api/tcp/streams/${encodeURIComponent(streamId)}/send`, { method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify({ data, mode }) });
  if(!res.ok) throw new Error('tcp send failed');
}

export async function tcpClose(streamId){
  const res = await fetch(`/api/tcp/streams/${encodeURIComponent(streamId)}/close`, { method:'POST' });
  if(!res.ok) throw new Error('tcp close failed');
}

export async function fetchUdpEvents(limit=200){
  const res = await fetch(`/api/udp/events?limit=${limit}`);
  return await res.json();
}

export async function udpSend(ip, port, data, mode='text'){
  const res = await fetch('/api/udp/send', { method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify({ addr:{ ip, port }, data, mode }) });
  if(!res.ok) throw new Error('udp send failed');
}
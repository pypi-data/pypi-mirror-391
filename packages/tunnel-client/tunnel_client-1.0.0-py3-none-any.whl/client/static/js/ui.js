import { $, $all, copyText, formatJSONMaybe, statusClass, prettyTime, relativeTime, escapeHtml } from './utils.js';
import { buildCurl, buildJS, buildPY } from './codegen.js';
import { getSettings, updateSettings, generateSubdomain, getConnectionStatus } from './api.js';
import { replayRequestRaw, replayRequestById, fetchTcpStreams, fetchTcpEvents, tcpSend, tcpClose, fetchUdpEvents, udpSend } from './api.js';

export function bindFilters(onChange){
  ['methodFilter','statusFilter','pathFilter'].forEach(id=>{
    const el = document.getElementById(id);
    if(!el) return;
    const evt = id==='pathFilter' ? 'input' : 'change';
    el.addEventListener(evt, onChange);
  });
}

export function renderList(items, onSelect, selectedId){
  const cont = $('#requestsList');
  if(!items.length){
    cont.innerHTML = `<div class="empty-state"><div class="empty-icon">🔍</div><div class="empty-text">No requests match your filters</div></div>`;
    $('#requestCount').textContent = '0';
    return;
  }
  cont.innerHTML = items.map(req => {
    const safeMethod = escapeHtml(req.method);
    const safeUrl = escapeHtml(req.url);
    const safeUrlTitle = escapeHtml(req.url);
    const timestamp = req.timestamp ? relativeTime(req.timestamp) : '';
    const duration = req.duration_ms || 0;
    return `
    <div class="request-item ${selectedId===req.id?'active':''}" data-id="${req.id}">
      <span class="method-badge method-${req.method}">${safeMethod}</span>
      <span class="request-path" title="${safeUrlTitle}">${safeUrl}</span>
      <span class="status-badge ${statusClass(req.status || req.response_status || 0)}">${req.status || req.response_status || '—'}</span>
      <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 4px; min-width: 120px;">
        <span class="time-badge" style="font-weight: 600; color: var(--text-secondary); font-size: 13px;">${escapeHtml(timestamp)}</span>
        <span class="time-badge">${duration}ms</span>
      </div>
    </div>
  `}).join('');
  $('#requestCount').textContent = String(items.length);
  $all('.request-item').forEach(el=> el.onclick = ()=> onSelect(parseInt(el.dataset.id,10)) );
}

export function renderDetails(d){
  $('#curlBtn').style.display = 'flex';
  $('#codeBtn').style.display = 'flex';
  // Add or show replay/edit buttons
  ensureReplayButtons(d);
  
  // Экранируем все данные для предотвращения рендеринга HTML
  const safeMethod = escapeHtml(d.method);
  const safeUrl = escapeHtml(d.url || d.path);
  const safeReqHeaders = escapeHtml(d.request_headers);
  const safeReqBody = d.request_body ? escapeHtml(formatJSONMaybe(d.request_body)) : '';
  const safeResHeaders = escapeHtml(d.response_headers);
  const safeResBody = escapeHtml(formatJSONMaybe(d.response_body));
  const safeTimestamp = escapeHtml(prettyTime(d.timestamp));
  
  const html = `
    <div class="info-grid">
      <div class="info-item"><div class="info-label">Method</div><div class="info-value">${safeMethod}</div></div>
      <div class="info-item"><div class="info-label">Status</div><div class="info-value ${statusClass(d.response_status)}">${d.response_status}</div></div>
      <div class="info-item"><div class="info-label">Time</div><div class="info-value">${d.duration_ms}ms</div></div>
      <div class="info-item"><div class="info-label">Timestamp</div><div class="info-value">${safeTimestamp}</div></div>
    </div>
    <div class="detail-section"><div class="detail-header"><div class="detail-title">URL</div></div><pre>${safeUrl}</pre></div>
    <div class="detail-section"><div class="detail-header"><div class="detail-title">Request Headers</div><button class="btn btn-sm" id="copy-req-h">📋 Copy</button></div><pre>${safeReqHeaders}</pre></div>
    ${d.request_body?`<div class="detail-section"><div class="detail-header"><div class="detail-title">Request Body</div><button class="btn btn-sm" id="copy-req-b">📋 Copy</button></div><pre>${safeReqBody}</pre></div>`:''}
    <div class="detail-section"><div class="detail-header"><div class="detail-title">Response Headers</div><button class="btn btn-sm" id="copy-res-h">📋 Copy</button></div><pre>${safeResHeaders}</pre></div>
    <div class="detail-section"><div class="detail-header"><div class="detail-title">Response Body</div><button class="btn btn-sm" id="copy-res-b">📋 Copy</button></div><pre>${safeResBody}</pre></div>
  `;
  $('#requestDetails').innerHTML = html;
  $('#copy-req-h')?.addEventListener('click', ()=> copyText(d.request_headers));
  $('#copy-req-b')?.addEventListener('click', ()=> copyText(d.request_body || ''));
  $('#copy-res-h')?.addEventListener('click', ()=> copyText(d.response_headers));
  $('#copy-res-b')?.addEventListener('click', ()=> copyText(d.response_body || ''));
  $('#curlBtn').onclick = ()=> copyText(buildCurl(mapToCodeModel(d)));
  $('#codeBtn').onclick = ()=> showCodeModal(mapToCodeModel(d));
}

function ensureReplayButtons(d){
  // Create buttons once
  if(!$('#replayBtn')){
    const container = document.querySelector('#requestDetails')?.previousElementSibling;
    if(container){
      const replayBtn = document.createElement('button');
      replayBtn.className = 'btn btn-sm';
      replayBtn.id = 'replayBtn';
      replayBtn.textContent = '⤴️ Replay';
      container.appendChild(replayBtn);

      const editBtn = document.createElement('button');
      editBtn.className = 'btn btn-sm btn-primary';
      editBtn.id = 'editReplayBtn';
      editBtn.style.marginLeft = '8px';
      editBtn.textContent = '✏️ Edit & Replay';
      container.appendChild(editBtn);
    }
  }
  // Bind actions
  $('#replayBtn').onclick = async ()=>{
    try {
      await replayRequestById(d.id);
      showToast('Replayed');
    } catch (e){ showToast('Replay failed'); }
  };
  $('#editReplayBtn').onclick = ()=> showReplayModal(d);
}

function mapToCodeModel(d){
  return {
    method: d.method,
    url: d.url || d.path,
    request_headers: d.request_headers,
    request_body: d.request_body
  };
}

export function updateStats(items){
  $('#totalRequests').textContent = String(items.length);
  const success = items.filter(r=> (r.status||0) < 400).length;
  $('#successRequests').textContent = String(success);
  $('#errorRequests').textContent = String(items.length - success);
  const avg = items.length ? Math.round(items.reduce((s,r)=> s + (r.duration_ms||0), 0) / items.length) : 0;
  $('#avgTime').textContent = `${avg}ms`;
}

// Modal + code generation
export function showCodeModal(d){
  const modal = document.getElementById('codeModal');
  modal.classList.add('show');
  let current = 'curl';
  const codeEl = document.getElementById('generatedCode');
  function render(){
    if(current==='curl') codeEl.textContent = buildCurl(d);
    else if(current==='python') codeEl.textContent = buildPY(d);
    else if(current==='javascript') codeEl.textContent = buildJS(d);
    else if(current==='node') codeEl.textContent = buildJS(d); // simple alias
  }
  render();
  document.querySelectorAll('.language-tab').forEach(btn => {
    btn.onclick = (e)=>{
      document.querySelectorAll('.language-tab').forEach(x=>x.classList.remove('active'));
      e.target.classList.add('active');
      current = e.target.textContent.toLowerCase();
      render();
    };
  });
  document.querySelector('.copy-code-btn').onclick = ()=> copyText(codeEl.textContent);
}

export function closeCodeModal(){
  document.getElementById('codeModal').classList.remove('show');
}

// Replay modal
export function showReplayModal(d){
  const modal = document.getElementById('replayModal');
  modal.classList.add('show');
  // Prefill
  $('#rp-method').value = d.method;
  $('#rp-url').value = d.url || d.path || '/';
  $('#rp-headers').value = d.request_headers || '{}';
  $('#rp-body').value = d.request_body || '';

  $('#rp-send').onclick = async ()=>{
    try {
      const method = $('#rp-method').value;
      const url = $('#rp-url').value;
      const headers = $('#rp-headers').value;
      const body = $('#rp-body').value;
      await replayRequestRaw({ method, url, headers, body });
      modal.classList.remove('show');
      showToast('Replayed');
    } catch(e){
      showToast('Replay failed');
    }
  };

  $('#replayModal .modal-close').onclick = ()=> modal.classList.remove('show');
}

// Settings Management for Tabs
export async function mountSettings(){
  // Load settings when switching to settings tabs
  const s = await getSettings();
  
  // Update connection tab
  const connPort = $('#conn-port');
  if(connPort) connPort.value = s.local_port || '';
  
  // Update connection status
  await updateConnectionStatus();
  
  // Update subdomain tab
  const sdInput = $('#sd-input');
  const sdCurrent = $('#sd-current');
  if(sdInput && sdCurrent) {
    sdInput.value = s.selected_subdomain || '';
    sdCurrent.textContent = s.selected_subdomain || '—';
  }
  
  // Update rate limit tab
  const rlInput = $('#rl-input');
  const rlCurrent = $('#rl-current');
  if(rlInput && rlCurrent) {
    rlInput.value = s.rate_limit_per_minute || '';
    rlCurrent.textContent = s.rate_limit_per_minute || '—';
  }
  
  // Update custom response tab
  const crEnabled = $('#cr-enabled');
  const crStatus = $('#cr-status');
  const crHeaders = $('#cr-headers');
  const crBody = $('#cr-body');
  if(crEnabled && crStatus && crHeaders && crBody) {
    crEnabled.checked = !!s.custom_response_enabled;
    crStatus.value = s.custom_response_status || 200;
    crHeaders.value = s.custom_response_headers || '{}';
    crBody.value = s.custom_response_body || '';
  }
  
  // Bind save buttons
  bindSettingsSave();
}

function bindSettingsSave() {
  // Connection settings - Local Port
  const connSavePort = $('#conn-save-port');
  if(connSavePort) {
    connSavePort.onclick = async ()=>{
      const port = parseInt($('#conn-port').value, 10);
      if(!port || port < 1 || port > 65535) {
        showToast('Invalid port (1-65535)');
        return;
      }
      await updateSettings({ local_port: port });
      showToast('Local port saved. Restart client to apply.');
    };
  }
  
  // Subdomain generate random
  const sdGenerate = $('#sd-generate');
  if(sdGenerate) {
    sdGenerate.onclick = async ()=>{
      try {
        const { subdomain } = await generateSubdomain();
        $('#sd-input').value = subdomain;
        $('#sd-current').textContent = subdomain;
        showToast(`Generated random subdomain: ${subdomain}`);
      } catch(e) {
        showToast('Failed to generate subdomain');
      }
    };
  }
  
  // Subdomain save
  const sdSave = $('#sd-save');
  if(sdSave) {
    sdSave.onclick = async ()=>{
      const subdomain = $('#sd-input').value ? $('#sd-input').value.trim().toLowerCase() : null;
      await updateSettings({ selected_subdomain: subdomain });
      $('#sd-current').textContent = subdomain || '—';
      if(subdomain) {
        showToast(`Subdomain set to '${subdomain}'. Tunnel will reconnect...`);
      } else {
        showToast('Subdomain cleared. Tunnel will reconnect...');
      }
    };
  }
  
  // Rate limit save
  const rlSave = $('#rl-save');
  if(rlSave) {
    rlSave.onclick = async ()=>{
      const rpm = $('#rl-input').value ? parseInt($('#rl-input').value, 10) : null;
      await updateSettings({ rate_limit_per_minute: rpm });
      $('#rl-current').textContent = rpm || '—';
    };
  }
  
  // Rate limit clear
  const rlClear = $('#rl-clear');
  if(rlClear) {
    rlClear.onclick = async ()=>{
      $('#rl-input').value = '';
      await updateSettings({ rate_limit_per_minute: null });
      $('#rl-current').textContent = '—';
    };
  }
  
  // Custom response save
  const crSave = $('#cr-save');
  if(crSave) {
    crSave.onclick = async ()=>{
      await updateSettings({
        custom_response_enabled: $('#cr-enabled').checked,
        custom_response_status: parseInt($('#cr-status').value || '200', 10),
        custom_response_headers: $('#cr-headers').value || '{}',
        custom_response_body: $('#cr-body').value || ''
      });
    };
  }
}

// Tab switching function
async function updateConnectionStatus() {
  const statusEl = $('#conn-status');
  const publicUrlContainer = $('#conn-public-url-container');
  const publicUrlLink = $('#conn-public-url');
  
  if (!statusEl) return;
  
  try {
    const statusData = await getConnectionStatus();
    const status = statusData.status || 'unknown';
    const connected = statusData.connected || false;
    
    let statusText = 'Unknown';
    let statusColor = 'var(--text-tertiary)';
    
    if (connected || status === 'connected') {
      statusText = 'Connected';
      statusColor = 'var(--success)';
      if (statusData.subdomain) {
        statusText += ` (${statusData.subdomain})`;
      }
    } else if (status === 'connecting') {
      statusText = 'Connecting...';
      statusColor = 'var(--warning)';
    } else {
      statusText = 'Not connected';
      statusColor = 'var(--error)';
    }
    
    statusEl.textContent = statusText;
    statusEl.style.color = statusColor;
    statusEl.style.fontWeight = '600';
    
    // Show/hide public URL
    if (statusData.public_url && statusData.subdomain) {
      if (publicUrlContainer) {
        publicUrlContainer.style.display = 'block';
      }
      if (publicUrlLink) {
        publicUrlLink.href = statusData.public_url;
        publicUrlLink.textContent = statusData.public_url;
      }
    } else {
      if (publicUrlContainer) {
        publicUrlContainer.style.display = 'none';
      }
    }
  } catch (e) {
    statusEl.textContent = 'Error checking status';
    statusEl.style.color = 'var(--error)';
    if (publicUrlContainer) {
      publicUrlContainer.style.display = 'none';
    }
  }
}

// Poll connection status every 2 seconds when on connection tab
let statusPollInterval = null;

export function switchTab(tabName) {
  // Update tab buttons
  document.querySelectorAll('.tab-button').forEach(btn => {
    btn.classList.remove('active');
  });
  
  // Find and activate the clicked tab button
  const clickedButton = Array.from(document.querySelectorAll('.tab-button')).find(btn => 
    btn.textContent.toLowerCase().includes(tabName.toLowerCase())
  );
  if (clickedButton) {
    clickedButton.classList.add('active');
  }
  
  // Update tab content
  document.querySelectorAll('.tab-content').forEach(content => {
    content.classList.remove('active');
  });
  const targetTab = document.getElementById(`tab-${tabName}`);
  if(targetTab) {
    targetTab.classList.add('active');
  }
  
  // Stop status polling if was running
  if (statusPollInterval) {
    clearInterval(statusPollInterval);
    statusPollInterval = null;
  }
  
  // Load settings if switching to settings tabs
  if (tabName !== 'dashboard') {
    mountSettings();
    
    // Start status polling when on connection tab
    if (tabName === 'connection') {
      updateConnectionStatus();
      statusPollInterval = setInterval(updateConnectionStatus, 2000);
    }
  }
  if (tabName === 'tcp') {
    mountTcp();
  }
  if (tabName === 'udp') {
    mountUdp();
  }
}

// TCP Tab
let _selectedStream = null;
async function mountTcp(){
  const data = await fetchTcpStreams();
  const list = (data.items||[]).map(s=>`
    <div class="request-item ${_selectedStream===s.stream_id?'active':''}" data-id="${s.stream_id}">
      <span class="method-badge">TCP</span>
      <span class="request-path">${escapeHtml(s.stream_id)}</span>
      <span class="status-badge ${s.closed_at?'status-4xx':'status-2xx'}">${s.closed_at?'closed':'open'}</span>
      <span class="time-badge">in ${s.bytes_in} / out ${s.bytes_out}</span>
    </div>
  `).join('');
  document.getElementById('tcp-streams').innerHTML = list || '<div class="empty-state"><div class="empty-text">No streams</div></div>';
  document.querySelectorAll('#tcp-streams .request-item').forEach(el => el.onclick = async ()=>{
    _selectedStream = el.dataset.id;
    await renderTcpDetails();
    await mountTcp();
  });
  // Bind send/close
  const sendBtn = document.getElementById('tcp-send');
  const closeBtn = document.getElementById('tcp-close');
  if(sendBtn){
    sendBtn.onclick = async ()=>{
      if(!_selectedStream) return;
      const data = document.getElementById('tcp-input').value;
      const mode = document.getElementById('tcp-mode').value;
      try{ await tcpSend(_selectedStream, data, mode); showToast('Sent'); } catch{ showToast('Send failed'); }
    };
  }
  if(closeBtn){
    closeBtn.onclick = async ()=>{
      if(!_selectedStream) return;
      try{ await tcpClose(_selectedStream); showToast('Closed'); await renderTcpDetails(); } catch{ showToast('Close failed'); }
    };
  }
}

let _selectedEvent = null;
async function renderTcpDetails(){
  if(!_selectedStream){
    document.getElementById('tcp-details').innerHTML = '<div class="empty-state"><div class="empty-text">Select a stream</div></div>';
    return;
  }
  const ev = await fetchTcpEvents(_selectedStream);
  const html = (ev.items||[]).map(e=>`
    <div class="request-item ${_selectedEvent===e.id?'active':''}" data-id="${e.id}" onclick="selectTcpEvent(${e.id})">
      <span class="method-badge ${e.direction==='in'?'method-GET':'method-POST'}">${e.direction}</span>
      <span class="request-path">${e.size} bytes</span>
      <span class="time-badge">${escapeHtml(e.timestamp)}</span>
    </div>
  `).join('');
  const detailsPanel = document.getElementById('tcp-details');
  detailsPanel.innerHTML = `
    <div style="max-height:400px;overflow-y:auto;margin-bottom:16px;">
      ${html || '<div class="empty-state"><div class="empty-text">No events</div></div>'}
    </div>
    ${_selectedEvent ? renderTcpEventContent(ev.items?.find(x=>x.id===_selectedEvent)) : ''}
  `;
}

window.selectTcpEvent = function(id){
  _selectedEvent = id;
  renderTcpDetails();
};

let _currentTcpEvent = null;

window.showTcpEventTab = function(mode){
  if(!_currentTcpEvent) return;
  document.querySelectorAll('#tab-tcp .language-tab').forEach(t=>t.classList.remove('active'));
  event.target.classList.add('active');
  const pre = document.getElementById('tcp-event-content');
  if(mode==='hex'){
    pre.textContent = _currentTcpEvent.sample_hex || '';
  } else {
    pre.textContent = _currentTcpEvent.sample_text || '';
  }
};

function renderTcpEventContent(e){
  if(!e) return '';
  const hex = e.sample_hex || '';
  const text = e.sample_text || '';
  const isTextClean = /^[\x20-\x7E\s]*$/.test(text);
  _currentTcpEvent = e;
  return `
    <div class="detail-section">
      <div class="detail-header">
        <div class="detail-title">Event Content (${e.size} bytes)</div>
        <button class="btn btn-sm" onclick="copyText('${escapeHtml(hex)}')">📋 Copy Hex</button>
        ${isTextClean ? `<button class="btn btn-sm" onclick="copyText('${escapeHtml(text)}')">📋 Copy Text</button>` : ''}
      </div>
      <div class="language-tabs" style="margin-bottom:12px;">
        <button class="language-tab active" onclick="showTcpEventTab('hex')">Hex</button>
        <button class="language-tab" onclick="showTcpEventTab('text')">Text</button>
      </div>
      <pre id="tcp-event-content">${escapeHtml(hex)}</pre>
    </div>
  `;
}

let _selectedUdpEvent = null;
let _currentUdpEvent = null;

window.showUdpEventTab = function(mode){
  if(!_currentUdpEvent) return;
  document.querySelectorAll('#tab-udp .language-tab').forEach(t=>t.classList.remove('active'));
  event.target.classList.add('active');
  const pre = document.getElementById('udp-event-content');
  if(mode==='hex'){
    pre.textContent = _currentUdpEvent.sample_hex || '';
  } else {
    pre.textContent = _currentUdpEvent.sample_text || '';
  }
};

async function mountUdp(){
  const data = await fetchUdpEvents();
  const list = (data.items||[]).map(e=>`
    <div class="request-item ${_selectedUdpEvent===e.id?'active':''}" data-id="${e.id}" onclick="selectUdpEvent(${e.id})">
      <span class="method-badge ${e.direction==='in'?'method-GET':'method-POST'}">${e.direction}</span>
      <span class="request-path">${escapeHtml(e.addr)} / ${e.size} bytes</span>
      <span class="time-badge">${escapeHtml(e.timestamp)}</span>
    </div>
  `).join('');
  const eventsContainer = document.getElementById('udp-events');
  const selected = data.items?.find(x=>x.id===_selectedUdpEvent);
  eventsContainer.innerHTML = `
    <div style="max-height:400px;overflow-y:auto;margin-bottom:16px;">
      ${list || '<div class="empty-state"><div class="empty-text">No events</div></div>'}
    </div>
    ${selected ? renderUdpEventContent(selected) : ''}
  `;
  const btn = document.getElementById('udp-send');
  if(btn){
    btn.onclick = async ()=>{
      const ip = document.getElementById('udp-ip').value;
      const port = parseInt(document.getElementById('udp-port').value, 10);
      const data = document.getElementById('udp-data').value;
      const mode = document.getElementById('udp-mode').value;
      try{ await udpSend(ip, port, data, mode); showToast('Sent'); await mountUdp(); } catch{ showToast('Send failed'); }
    };
  }
}

window.selectUdpEvent = function(id){
  _selectedUdpEvent = id;
  mountUdp();
};

function renderUdpEventContent(e){
  if(!e) return '';
  const hex = e.sample_hex || '';
  const text = e.sample_text || '';
  const isTextClean = /^[\x20-\x7E\s]*$/.test(text);
  _currentUdpEvent = e;
  return `
    <div class="detail-section">
      <div class="detail-header">
        <div class="detail-title">Event Content (${e.size} bytes)</div>
        <button class="btn btn-sm" onclick="copyText('${escapeHtml(hex)}')">📋 Copy Hex</button>
        ${isTextClean ? `<button class="btn btn-sm" onclick="copyText('${escapeHtml(text)}')">📋 Copy Text</button>` : ''}
      </div>
      <div class="language-tabs" style="margin-bottom:12px;">
        <button class="language-tab active" onclick="showUdpEventTab('hex')">Hex</button>
        <button class="language-tab" onclick="showUdpEventTab('text')">Text</button>
      </div>
      <pre id="udp-event-content">${escapeHtml(hex)}</pre>
    </div>
  `;
}
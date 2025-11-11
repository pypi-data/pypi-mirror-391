import { fetchList, fetchDetails, clearAll, connectWS } from './api.js';
import { $, showToast, copyText } from './utils.js';
import { bindFilters, renderList, renderDetails, updateStats, showCodeModal, closeCodeModal, mountSettings, switchTab } from './ui.js';

let items = [];
let selectedId = null;

async function loadAndRender(){
  const method = $('#methodFilter')?.value || '';
  const statusBand = $('#statusFilter')?.value || '';
  // Convert status band to range: '2xx' -> status between 200-299
  let status = '';
  if (statusBand === '2xx') status = '2xx'; // We'll filter on client side
  else if (statusBand === '3xx') status = '3xx';
  else if (statusBand === '4xx') status = '4xx';
  else if (statusBand === '5xx') status = '5xx';
  const path = $('#pathFilter')?.value || '';
  let fetchedItems = await fetchList({ method, status: '', path }); // Always fetch all, filter on client
  // Apply status filter on client side
  if (statusBand) {
    const statusNum = parseInt(statusBand[0]);
    fetchedItems = fetchedItems.filter(item => {
      const itemStatus = item.status || item.response_status || 0;
      if (!itemStatus) return false;
      return Math.floor(itemStatus / 100) === statusNum;
    });
  }
  items = fetchedItems;
  renderList(items, onSelect, selectedId);
  updateStats(items);
}

async function onSelect(id){
  selectedId = id;
  const d = await fetchDetails(id);
  renderDetails(d);
}

function setup(){
  // Bind dashboard filters
  bindFilters(loadAndRender);
  
  // Modal handling
  $('#codeModal')?.addEventListener('click', (e)=>{ if(e.target.id==='codeModal') closeCodeModal(); });
  
  // Initial button state
  $('#curlBtn').style.display = 'none';
  $('#codeBtn').style.display = 'none';
  $('#codeBtn').onclick = ()=> selectedId && showCodeModal(items.find(x=>x.id===selectedId));
  $('#curlBtn').onclick = ()=> {/* handled in renderDetails with actual payload */};
  
  // Clear button
  document.querySelector('button.btn.btn-danger')?.addEventListener('click', async ()=>{
    if(!confirm('Clear all requests?')) return;
    await clearAll();
    await loadAndRender();
    showToast('Cleared');
  });
  
  // Export button
  document.querySelector('button.btn:not(.btn-danger)')?.addEventListener('click', ()=>{
    const dataStr = JSON.stringify(items, null, 2);
    const blob = new Blob([dataStr], {type:'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `tunnel-requests-${Date.now()}.json`; a.click();
    showToast('Exported');
  });
  
  // WebSocket connection for live updates
  connectWS(()=> loadAndRender());
  
  // Initial load
  loadAndRender();
  
  // Make switchTab available globally for HTML onclick handlers
  window.switchTab = switchTab;
  
  // Load settings on initialization
  mountSettings();
}

// Wait for DOM to be ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', setup);
} else {
  setup();
}
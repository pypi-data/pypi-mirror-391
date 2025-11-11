export function $(sel) { return document.querySelector(sel); }
export function $all(sel) { return Array.from(document.querySelectorAll(sel)); }

export function showToast(message) {
  const el = $('#toast');
  if (!el) return;
  $('#toastMessage').textContent = message;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), 2000);
}

export function copyText(text) {
  return navigator.clipboard.writeText(text).then(() => showToast('Copied'));
}

export function formatJSONMaybe(text) {
  try { return JSON.stringify(JSON.parse(text), null, 2); } catch { return text || ''; }
}

export function statusClass(code) { return `status-${Math.floor((code || 0)/100)}xx`; }

export function prettyTime(iso) { try { return new Date(iso).toLocaleString(); } catch { return iso; } }

export function relativeTime(iso) {
  try {
    const date = new Date(iso);
    if (isNaN(date.getTime())) return iso;
    
    const now = new Date();
    const diffMs = now - date;
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHour / 24);
    
    if (diffSec < 10) return 'just now';
    if (diffSec < 60) return `${diffSec}s ago`;
    if (diffMin < 60) return `${diffMin}${diffMin === 1 ? ' min' : ' min'} ago`;
    if (diffHour < 24) return `${diffHour}${diffHour === 1 ? ' hr' : ' hr'} ago`;
    
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const requestDay = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    const timeStr = date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
    
    if (requestDay.getTime() === today.getTime()) {
      return `today ${timeStr}`;
    }
    if (requestDay.getTime() === yesterday.getTime()) {
      return `yesterday ${timeStr}`;
    }
    if (diffDay < 7) {
      return `${diffDay}${diffDay === 1 ? ' day' : ' days'} ago`;
    }
    
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) + ' ' + timeStr;
  } catch {
    return iso || '';
  }
}

export function shellQuote(s){
  if(typeof s !== 'string') s = String(s);
  return `'${s.replace(/'/g, "'\\''")}'`;
}

export function escapeHtml(text) {
  if (!text) return '';
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return String(text).replace(/[&<>"']/g, m => map[m]);
}
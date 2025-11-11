import { shellQuote } from './utils.js';

export function buildCurl(d){
  const url = d.url || d.path || '/';
  const headers = safeHeaders(d.request_headers);
  const h = Object.entries(headers).map(([k,v])=>`-H ${shellQuote(`${k}: ${v}`)}`).join(' \\\n  ');
  const body = d.request_body ? ` \\\n+  --data ${shellQuote(d.request_body)}` : '';
  return `curl -X ${d.method} \\\n+  ${h}${body} \\\n+  ${shellQuote(url)}`.replace(/\s+$/,'');
}

export function buildJS(d){
  const url = d.url || d.path || '/';
  const headers = JSON.stringify(safeHeaders(d.request_headers), null, 2);
  const body = d.request_body ? `,\n  body: ${JSON.stringify(d.request_body)}` : '';
  return `fetch(${JSON.stringify(url)}, {\n  method: ${JSON.stringify(d.method)},\n  headers: ${headers}${body}\n}).then(r=>r.text()).then(console.log).catch(console.error);`;
}

export function buildPY(d){
  const url = d.url || d.path || '/';
  const headers = JSON.stringify(safeHeaders(d.request_headers), null, 2);
  const body = d.request_body ? `data=${JSON.stringify(d.request_body)}, ` : '';
  return `import requests\nresp = requests.request(${JSON.stringify(d.method)}, ${JSON.stringify(url)}, headers=${headers}, ${body}allow_redirects=True)\nprint(resp.status_code)\nprint(resp.text)`;
}

function safeHeaders(h){
  if(typeof h === 'string') { try { return JSON.parse(h); } catch { return {}; } }
  return h || {};
}
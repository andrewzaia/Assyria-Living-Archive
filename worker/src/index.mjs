// Cloudflare Worker for private editorial email delivery. No personal recipient address in site assets.
const ALLOWED_ORIGIN = 'https://andrewzaia.github.io';
const MAX_REQUEST_BYTES = 24000;
const KINDS = new Set(['Article suggestion', 'Correction to an article', 'Personal or family history', 'Language or cultural knowledge', 'Image or media offer']);
const FIELDS = { name: 120, email: 254, subject: 180, body: 10000, sources: 5000, permissions: 3000 };

function response(payload, status = 200, origin = '') {
  const headers = { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', 'Vary': 'Origin', 'X-Content-Type-Options': 'nosniff' };
  if (origin === ALLOWED_ORIGIN) {
    headers['Access-Control-Allow-Origin'] = ALLOWED_ORIGIN;
    headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS';
    headers['Access-Control-Allow-Headers'] = 'Content-Type';
  }
  return new Response(JSON.stringify(payload), { status, headers });
}
function readField(value, max) {
  if (value !== undefined && typeof value !== 'string') return null;
  const text = (value || '').trim();
  return text.length <= max && !/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/.test(text) ? text : null;
}
function validEmail(value) {
  return !value || (value.length <= 254 && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) && !/[\r\n]/.test(value));
}
function markdown(data) {
  return [
    '# Assyria | The Living Archive',
    '',
    'Status: Submitted for editorial review, not approved or published.',
    '',
    '## Contributor',
    '',
    'Name: ' + (data.name || 'Not supplied'),
    'Contact email: ' + (data.email || 'Not supplied'),
    '',
    '## Submission',
    '',
    'Type: ' + data.type,
    'Subject: ' + data.subject,
    '',
    '### Contribution',
    '',
    data.body,
    '',
    '### Sources or supporting records',
    '',
    data.sources || 'Not supplied',
    '',
    '### Attribution and permissions',
    '',
    data.permissions || 'To be discussed',
    ''
  ].join('\n');
}
async function verifyTurnstile(token, env, request) {
  const fields = new URLSearchParams({ secret: env.TURNSTILE_SECRET, response: token });
  const ip = request.headers.get('CF-Connecting-IP');
  if (ip) fields.set('remoteip', ip);
  const check = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
    method: 'POST', body: fields, headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  });
  if (!check.ok) return false;
  const result = await check.json();
  return result.success === true && result.hostname === 'andrewzaia.github.io' && result.action === 'contribution';
}
export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    const path = new URL(request.url).pathname;
    if (path === '/status' && request.method === 'GET') return response({ available: Boolean(env.EMAIL && env.CONTRIBUTION_INBOX && env.CONTRIBUTION_FROM && env.TURNSTILE_SECRET) }, 200, origin);
    if (path !== '/submit') return response({ error: 'Not found.' }, 404, origin);
    if (origin !== ALLOWED_ORIGIN) return response({ error: 'Forbidden.' }, 403);
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: response({}, 200, origin).headers });
    if (request.method !== 'POST') return response({ error: 'Method not allowed.' }, 405, origin);
    if (!(request.headers.get('Content-Type') || '').toLowerCase().startsWith('application/json')) return response({ error: 'Expected JSON.' }, 415, origin);
    if (Number(request.headers.get('Content-Length') || 0) > MAX_REQUEST_BYTES) return response({ error: 'Submission too large.' }, 413, origin);
    if (!env.EMAIL || !env.CONTRIBUTION_INBOX || !env.CONTRIBUTION_FROM || !env.TURNSTILE_SECRET) return response({ error: 'Submission service is not configured.' }, 503, origin);
    let data;
    try {
      const raw = await request.text();
      if (new TextEncoder().encode(raw).length > MAX_REQUEST_BYTES) return response({ error: 'Submission too large.' }, 413, origin);
      data = JSON.parse(raw);
      if (!data || typeof data !== 'object' || Array.isArray(data)) throw new Error('Invalid JSON object');
    } catch {
      return response({ error: 'Invalid submission.' }, 400, origin);
    }
    // Do not acknowledge honeypot spam with a message about bot detection.
    if (data.website) return response({ ok: true }, 200, origin);
    if (typeof data.type !== 'string' || !KINDS.has(data.type)) return response({ error: 'Choose a valid contribution type.' }, 400, origin);
    const fields = {};
    for (const [name, length] of Object.entries(FIELDS)) {
      const value = readField(data[name], length);
      if (value === null) return response({ error: 'Please check the length and format of your entries.' }, 400, origin);
      fields[name] = value;
    }
    if (!fields.subject || !fields.body || !validEmail(fields.email)) return response({ error: 'A subject and contribution are required. Check your contact email.' }, 400, origin);
    if (/[\r\n]/.test(fields.subject) || /[\r\n]/.test(fields.name)) return response({ error: 'Subject and contributor name must use a single line.' }, 400, origin);
    if (typeof data.turnstileToken !== 'string' || data.turnstileToken.length < 10 || data.turnstileToken.length > 2048) return response({ error: 'Complete the security check.' }, 400, origin);
    try {
      if (!(await verifyTurnstile(data.turnstileToken, env, request))) return response({ error: 'Security verification expired or failed. Please try again.' }, 403, origin);
    } catch {
      return response({ error: 'Security verification is temporarily unavailable.' }, 503, origin);
    }
    const draft = markdown({ ...fields, type: data.type });
    const slug = fields.subject.toLowerCase().normalize('NFKD').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 48) || 'draft';
    const message = {
      from: { email: env.CONTRIBUTION_FROM, name: 'Assyria Living Archive' },
      to: env.CONTRIBUTION_INBOX,
      subject: 'Assyria contribution: ' + fields.subject,
      text: 'A new contribution was submitted for editorial review.\n\n' + draft,
      html: '<p>A new contribution was submitted for editorial review. See the attached Markdown draft.</p>',
      attachments: [{ filename: 'assyria-contribution-' + slug + '.md', type: 'text/markdown', disposition: 'attachment', content: draft }]
    };
    if (fields.email) message.replyTo = fields.email;
    try {
      await env.EMAIL.send(message);
      return response({ ok: true }, 200, origin);
    } catch (error) {
      // Do not log raw form fields, recipient addresses or contact details.
      console.error('Editorial email delivery failed', error?.code || 'unknown');
      return response({ error: 'We could not deliver your contribution. Please download your draft and try again later.' }, 502, origin);
    }
  }
};

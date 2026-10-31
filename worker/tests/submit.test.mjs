import test from 'node:test';
import assert from 'node:assert/strict';
import worker from '../src/index.mjs';

const origin = 'https://www.assyrialivingarchive.org';
const createRequest = (data, options = {}) => new Request('https://assyria-archive-contributions.example/submit', {
  method: options.method || 'POST',
  headers: { Origin: options.origin || origin, 'Content-Type': options.contentType || 'application/json' },
  body: options.method === 'OPTIONS' ? undefined : JSON.stringify(data),
});
const good = {
  type: 'Article suggestion', name: 'Researcher', email: 'reader@example.net',
  subject: 'Ashur trade', body: 'A source-led summary', sources: 'Tablet reference',
  permissions: 'Original text', turnstileToken: 'a-valid-looking-token'
};
const env = { EMAIL: { async send() {} }, TURNSTILE_SECRET: 'server-secret', CONTRIBUTION_INBOX: 'private@example.org', CONTRIBUTION_FROM: 'notices@example.org' };

test('rejects cross-origin submission before delivery', async () => {
  const response = await worker.fetch(createRequest(good, { origin: 'https://evil.example' }), env);
  assert.equal(response.status, 403);
  assert.equal(response.headers.get('Access-Control-Allow-Origin'), null);
});
test('does not deliver without configured backend', async () => {
  const response = await worker.fetch(createRequest(good), {});
  assert.equal(response.status, 503);
});
test('rejects invalid input and does not send email', async () => {
  let sends = 0;
  const response = await worker.fetch(createRequest({ ...good, subject: '', turnstileToken: 'valid-looking-token' }), { ...env, EMAIL: { async send() { sends++; } } });
  assert.equal(response.status, 400);
  assert.equal(sends, 0);
});
test('requires verified Turnstile action and hostname', async () => {
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async () => Response.json({ success: true, hostname: 'untrusted.example', action: 'contribution' });
  try {
    const response = await worker.fetch(createRequest(good), env);
    assert.equal(response.status, 403);
  } finally { globalThis.fetch = originalFetch; }
});
test('sends validated form with exact Markdown attachment and private destination', async () => {
  const originalFetch = globalThis.fetch;
  let sent;
  globalThis.fetch = async () => Response.json({ success: true, hostname: 'www.assyrialivingarchive.org', action: 'contribution' });
  try {
    const response = await worker.fetch(createRequest(good), { ...env, EMAIL: { async send(message) { sent = message; } } });
    assert.equal(response.status, 200);
    assert.equal((await response.json()).ok, true);
    assert.equal(sent.to, env.CONTRIBUTION_INBOX);
    assert.equal(sent.replyTo, 'reader@example.net');
    assert.match(sent.attachments[0].filename, /\.md$/);
    assert.match(sent.attachments[0].content, /Tablet reference/);
    assert.match(sent.attachments[0].content, /Original text/);
    assert.equal(response.headers.get('Access-Control-Allow-Origin'), origin);
    assert.doesNotMatch(JSON.stringify(await worker.fetch(new Request('https://assyria-archive-contributions.example/submit'), env)), /private@example.org/);
  } finally { globalThis.fetch = originalFetch; }
});
test('rejects oversized requests', async () => {
  const response = await worker.fetch(createRequest({ ...good, body: 'A'.repeat(25000) }), env);
  assert.equal(response.status, 413);
});
test('preflight does not disclose private settings', async () => {
  const response = await worker.fetch(createRequest({}, { method: 'OPTIONS' }), env);
  assert.equal(response.status, 204);
  assert.equal(response.headers.get('Access-Control-Allow-Origin'), origin);
});

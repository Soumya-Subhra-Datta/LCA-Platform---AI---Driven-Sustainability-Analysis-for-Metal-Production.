import http from 'http';
import https from 'https';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import express from 'express';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DIST_DIR = path.join(__dirname, '..', 'dist');

const app = express();
const PORT = process.env.PORT || 3000;

function normalizeTarget(raw) {
  if (!raw) return 'http://localhost:8000';
  const value = String(raw).trim().replace(/\/+$/, '');
  if (/^https?:\/\//.test(value)) return value;
  return `https://${value}`;
}

const API_PROXY_TARGET = normalizeTarget(
  process.env.API_PROXY_TARGET || process.env.VITE_API_BASE_URL,
);

function proxyRequest(req, res) {
  const target = new URL(API_PROXY_TARGET);
  const isHttps = target.protocol === 'https:';
  const client = isHttps ? https : http;

  const headers = { ...req.headers };
  headers.host = target.host;

  const proxyReq = client.request(
    {
      hostname: target.hostname,
      port: target.port || (isHttps ? 443 : 80),
      path: req.originalUrl,
      method: req.method,
      headers,
    },
    (proxyRes) => {
      res.writeHead(proxyRes.statusCode || 500, proxyRes.headers);
      proxyRes.pipe(res);
    },
  );

  proxyReq.on('error', (err) => {
    res.status(502).json({
      detail: 'The API service is temporarily unavailable. Please try again later.',
    });
  });

  req.pipe(proxyReq);
}

app.use('/api', (req, res) => proxyRequest(req, res));
app.use('/health', (req, res) => proxyRequest(req, res));

if (fs.existsSync(DIST_DIR)) {
  app.use(express.static(DIST_DIR));
  app.get(/^(?!\/api|\/health).*/, (req, res) => {
    res.sendFile(path.join(DIST_DIR, 'index.html'));
  });
} else {
  app.get('/', (req, res) => {
    res
      .status(200)
      .send(
        '<h1>LCA Platform Frontend</h1><p>Production build not found. Run <code>npm run build</code> first.</p>',
      );
  });
}

app.listen(PORT, () => {
  console.log(`LCA Platform frontend serving on port ${PORT}`);
  console.log(`Proxying /api to ${API_PROXY_TARGET}`);
});

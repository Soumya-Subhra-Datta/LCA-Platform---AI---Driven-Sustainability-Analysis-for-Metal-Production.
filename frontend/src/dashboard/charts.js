import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

const instances = {};

export function destroyChart(id) {
  if (instances[id]) {
    instances[id].destroy();
    delete instances[id];
  }
}

function getCtx(canvasId) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;
  destroyChart(canvasId);
  return ctx;
}

export function createBarChart(canvasId, labels, datasets, options = {}) {
  const ctx = getCtx(canvasId);
  if (!ctx) return;
  instances[canvasId] = new Chart(ctx, {
    type: 'bar',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'top' } },
      scales: { y: { beginAtZero: true } },
      ...options,
    },
  });
}

export function createLineChart(canvasId, labels, datasets, options = {}) {
  const ctx = getCtx(canvasId);
  if (!ctx) return;
  instances[canvasId] = new Chart(ctx, {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'top' } },
      scales: { y: { beginAtZero: true } },
      ...options,
    },
  });
}

const defaultColors = ['#1a73e8', '#34a853', '#fbbc04', '#ea4335', '#9334e6', '#ff6d01', '#185abc', '#137333'];

export function createDoughnutChart(canvasId, labels, data, colors = null) {
  const ctx = getCtx(canvasId);
  if (!ctx) return;
  instances[canvasId] = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{ data, backgroundColor: colors || defaultColors.slice(0, data.length), borderWidth: 0 }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'right' } },
    },
  });
}

export function createRadarChart(canvasId, labels, datasets, options = {}) {
  const ctx = getCtx(canvasId);
  if (!ctx) return;
  instances[canvasId] = new Chart(ctx, {
    type: 'radar',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { r: { beginAtZero: true, max: 100 } },
      ...options,
    },
  });
}

export function createHorizontalBarChart(canvasId, labels, data, color = '#1a73e8') {
  const ctx = getCtx(canvasId);
  if (!ctx) return;
  instances[canvasId] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{ label: 'Value', data, backgroundColor: color, borderWidth: 0 }],
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { x: { beginAtZero: true } },
    },
  });
}

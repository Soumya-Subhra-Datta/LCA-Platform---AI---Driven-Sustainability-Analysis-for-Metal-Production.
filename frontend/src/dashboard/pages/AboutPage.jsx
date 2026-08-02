import { useState } from 'react';

const PDF_URL = `${import.meta.env.BASE_URL}digital_twins_lca_review.pdf`;
const PAGE1_URL = `${import.meta.env.BASE_URL}paper-page-1.png`;
const PAPER_NAME = 'Digital Twins in Sustainability Initiatives: A Review From Life Cycle Assessment Perspective';

export default function AboutPage() {
  const [imgLoaded, setImgLoaded] = useState(false);

  const openPaper = () => window.open(PDF_URL, '_blank');

  return (
    <>
      <div className="card">
        <div className="card-header"><h3>About the Project</h3></div>
        <p style={{ marginBottom: 12, color: 'var(--text-secondary)' }}>
          <strong style={{ color: 'var(--text)' }}>LCA Platform — AI-Driven Sustainability Analysis for Metal Production</strong>{' '}
          is an end-to-end analytics platform that turns open global mining datasets into actionable environmental insight.
          It ingests real-world data on rare earth element projects, global coal and metal mining, and world mining
          commodities; trains machine learning models to predict deposit type, resource size, heavy rare earth content and
          Dy2O3 grade; and then evaluates the full life-cycle, circularity and sustainability profile of a mining or
          processing facility.
        </p>
        <p style={{ marginBottom: 0, color: 'var(--text-secondary)' }}>
          The platform combines a FastAPI backend (Python) with a React + Chart.js dashboard. Every assessment is
          explainable, benchmarked against industry data, stored in a database, and exportable as a report — making it
          suitable for researchers, analysts and sustainability teams.
        </p>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-header"><h3>Motivation</h3></div>
          <p style={{ fontSize: 14, color: 'var(--text-secondary)', marginBottom: 0 }}>
            Metal and rare earth production is one of the most resource- and carbon-intensive industrial activities, yet
            sustainability assessment for mining remains fragmented, spreadsheet-driven and hard to repeat. Regulatory and
            investor pressure is growing, and teams need fast, defensible answers to questions like: <em>How much CO2 does
            this facility emit? How circular is its material flow? Which deposits are worth developing?</em> Our motivation
            is to make rigorous life-cycle thinking practical and data-driven — replacing manual, one-off analyses with a
            reusable platform grounded in open scientific datasets.
          </p>
        </div>
        <div className="card">
          <div className="card-header"><h3>Novelty</h3></div>
          <ul style={{ paddingLeft: 20, fontSize: 14, color: 'var(--text-secondary)' }}>
            <li style={{ marginBottom: 8 }}>One unified pipeline from raw open datasets (REE projects, coal &amp; metal mining, world commodities) to prediction and impact assessment.</li>
            <li style={{ marginBottom: 8 }}>Trained ML models (Gradient Boosting, Random Forest) for deposit classification, resource estimation and REE content prediction, with SHAP-based explanations.</li>
            <li style={{ marginBottom: 8 }}>A factor-driven LCA engine calibrated per ore type and processing route, with industry benchmark comparison and impact grading.</li>
            <li style={{ marginBottom: 8 }}>Circularity metrics and a multi-pillar ESG sustainability score with automated recommendations.</li>
            <li style={{ marginBottom: 0 }}>Everything accessible through an authenticated, deployable web dashboard with reporting.</li>
          </ul>
        </div>
      </div>

      <div className="card">
        <div className="card-header"><h3>Base Paper</h3></div>
        <p style={{ fontSize: 14, color: 'var(--text-secondary)', marginBottom: 16 }}>
          This project is inspired by the review paper{' '}
          <strong>{PAPER_NAME}</strong>. The paper surveys how digital twin technologies support sustainability
          initiatives, particularly when combined with Life Cycle Assessment (LCA) — using live, data-driven representations
          of physical systems to continuously evaluate environmental performance. Our platform operationalizes that
          vision for metal production: real global datasets, predictive models and repeatable LCA-driven assessments replace
          static, one-off analyses with a continuously queryable view of a facility's environmental footprint.
        </p>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 24, alignItems: 'flex-start' }}>
          <div
            onClick={openPaper}
            title="Click to open the PDF"
            style={{ cursor: 'pointer', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: 12, background: '#fff', boxShadow: 'var(--shadow)', maxWidth: 420 }}
          >
            <div style={{ textAlign: 'center', color: 'var(--text-secondary)', fontSize: 12, marginBottom: 8 }}>
              First page preview — click to open the full paper
            </div>
            <div style={{ overflow: 'hidden', display: 'flex', justifyContent: 'center' }}>
              {!imgLoaded && <div style={{ padding: 40, textAlign: 'center' }}><div className="spinner" /><p style={{ marginTop: 8, color: 'var(--text-secondary)' }}>Loading preview...</p></div>}
              <img
                src={PAGE1_URL}
                alt={`First page of ${PAPER_NAME}`}
                onLoad={() => setImgLoaded(true)}
                style={{ maxWidth: '100%', height: 'auto', display: imgLoaded ? 'block' : 'none' }}
              />
            </div>
            <div style={{ textAlign: 'center', marginTop: 10 }}>
              <span className="btn btn-primary btn-sm">Open PDF</span>
            </div>
          </div>
          <div style={{ flex: '1', minWidth: 280 }}>
            <div className="result-item" style={{ marginBottom: 12 }}>
              <div className="label">Title</div>
              <div className="value" style={{ fontSize: 14 }}>{PAPER_NAME}</div>
            </div>
            <div className="result-item" style={{ marginBottom: 12 }}>
              <div className="label">Role in this project</div>
              <div className="value" style={{ fontSize: 14 }}>Conceptual foundation: digital twins + LCA for sustainability</div>
            </div>
            <div className="result-item" style={{ marginBottom: 0 }}>
              <div className="label">Full text</div>
              <div className="value" style={{ fontSize: 14 }}>17 pages · 2.1 MB · bundled with the deployment</div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

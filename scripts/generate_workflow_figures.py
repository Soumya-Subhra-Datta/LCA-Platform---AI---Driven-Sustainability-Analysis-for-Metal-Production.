import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import os

OUT = 'C:/Users/soumy/OneDrive/Desktop/Project/lca_platform/scripts/figures'
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 9,
    'figure.dpi': 200,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.2,
})

# ============ FIG 9: System Architecture ============
fig, ax = plt.subplots(figsize=(10, 7))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')
ax.set_title('Fig. 9. System Architecture of the AI-Driven LCA Platform', fontsize=12, fontweight='bold', pad=15)

def draw_box(ax, x, y, w, h, text, color='#e8f0fe', edge='#1a73e8', fontsize=8, bold=False):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1", facecolor=color, edgecolor=edge, linewidth=1.2)
    ax.add_patch(box)
    weight = 'bold' if bold else 'normal'
    ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=fontsize, fontweight=weight, wrap=True)

def draw_arrow(ax, x1, y1, x2, y2, color='#5f6368'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.5))

# === Layer 1: Data Sources (top) ===
ax.text(5, 9.6, 'DATA LAYER', ha='center', fontsize=11, fontweight='bold', color='#1a73e8')
draw_box(ax, 0.2, 9.0, 2.2, 0.5, 'Global REE\nProjects', '#e8f0fe', '#1a73e8', 7)
draw_box(ax, 2.8, 9.0, 2.4, 0.5, 'Open Database\nCoal & Metal Mining', '#e8f0fe', '#1a73e8', 7)
draw_box(ax, 5.6, 9.0, 2.2, 0.5, 'World Mining\nCommodities', '#e8f0fe', '#1a73e8', 7)
draw_box(ax, 8.2, 9.0, 1.6, 0.5, 'User\nInput', '#e8f0fe', '#1a73e8', 7)

# Arrows down
draw_arrow(ax, 1.3, 9.0, 1.3, 8.3)
draw_arrow(ax, 4.0, 9.0, 4.0, 8.3)
draw_arrow(ax, 6.7, 9.0, 6.7, 8.3)
draw_arrow(ax, 9.0, 9.0, 9.0, 8.3)

# === Layer 2: Data Pipeline ===
ax.text(5, 8.5, 'DATA PIPELINE', ha='center', fontsize=10, fontweight='bold', color='#34a853')
draw_box(ax, 0.5, 7.7, 2.0, 0.55, 'Data Loading\n& Validation', '#e6f4ea', '#34a853', 7)
draw_box(ax, 2.8, 7.7, 2.2, 0.55, 'Feature\nEngineering', '#e6f4ea', '#34a853', 7)
draw_box(ax, 5.3, 7.7, 2.2, 0.55, 'Preprocessing\n& Scaling', '#e6f4ea', '#34a853', 7)
draw_box(ax, 7.8, 7.7, 1.9, 0.55, 'KNN\nImputation', '#e6f4ea', '#34a853', 7)

draw_arrow(ax, 1.3, 7.7, 1.3, 7.55)
draw_arrow(ax, 2.5, 7.97, 2.8, 7.97)
draw_arrow(ax, 5.0, 7.97, 5.3, 7.97)
draw_arrow(ax, 7.5, 7.97, 7.8, 7.97)

# Arrows down to processing
draw_arrow(ax, 3.9, 7.7, 3.9, 7.0)

# === Layer 3: Processing Engines ===
ax.text(5, 7.2, 'PROCESSING LAYER', ha='center', fontsize=10, fontweight='bold', color='#ea4335')

# ML Engine
draw_box(ax, 0.2, 6.1, 2.8, 0.8, 'ML ENGINE\n4 Models (GBM, RF)\nStandardScaler + CV', '#fce8e6', '#ea4335', 7, bold=True)

# LCA Engine
draw_box(ax, 3.3, 6.1, 3.0, 0.8, 'LCA ENGINE\n5 Calculators\n14 Ore Types', '#fce8e6', '#ea4335', 7, bold=True)

# Circular Economy
draw_box(ax, 6.6, 6.1, 3.2, 0.8, 'CIRCULARITY &\nSUSTAINABILITY\nESG+E Scoring', '#fce8e6', '#ea4335', 7, bold=True)

# Arrows down
draw_arrow(ax, 1.6, 6.1, 1.6, 5.5)
draw_arrow(ax, 4.8, 6.1, 4.8, 5.5)
draw_arrow(ax, 8.2, 6.1, 8.2, 5.5)

# === Layer 4: Explainability ===
ax.text(5, 5.7, 'EXPLAINABILITY LAYER', ha='center', fontsize=10, fontweight='bold', color='#fbbc04')
draw_box(ax, 1.5, 4.9, 3.5, 0.55, 'SHAP TreeExplainer\nShapley Value Computation', '#fef7e0', '#fbbc04', 7)
draw_box(ax, 5.3, 4.9, 3.5, 0.55, 'Natural Language\nExplanation Generator', '#fef7e0', '#fbbc04', 7)

draw_arrow(ax, 3.25, 4.9, 3.25, 4.4)
draw_arrow(ax, 7.05, 4.9, 7.05, 4.4)

# === Layer 5: Storage ===
ax.text(5, 4.6, 'STORAGE LAYER', ha='center', fontsize=10, fontweight='bold', color='#9334e6')
draw_box(ax, 1.0, 3.8, 3.5, 0.55, 'SQLite Database\n10 Tables (ORM)', '#f3e8fd', '#9334e6', 7)
draw_box(ax, 5.0, 3.8, 4.0, 0.55, 'Model Artifacts\njoblib Serialisation', '#f3e8fd', '#9334e6', 7)

draw_arrow(ax, 2.75, 3.8, 2.75, 3.2)
draw_arrow(ax, 7.0, 3.8, 7.0, 3.2)

# === Layer 6: API ===
ax.text(5, 3.4, 'API LAYER', ha='center', fontsize=10, fontweight='bold', color='#1a73e8')
draw_box(ax, 0.5, 2.5, 9.0, 0.65, 'FastAPI REST Endpoints  |  JWT Auth  |  7 Routers  |  CORS  |  OpenAPI /docs', '#e8f0fe', '#1a73e8', 8, bold=True)

draw_arrow(ax, 5.0, 2.5, 5.0, 2.0)

# === Layer 7: Frontend ===
ax.text(5, 2.2, 'PRESENTATION LAYER', ha='center', fontsize=10, fontweight='bold', color='#34a853')
draw_box(ax, 0.5, 1.1, 2.0, 0.75, 'SPA Router\nHash-based', '#e6f4ea', '#34a853', 7)
draw_box(ax, 2.8, 1.1, 2.2, 0.75, 'Interactive\nForms', '#e6f4ea', '#34a853', 7)
draw_box(ax, 5.3, 1.1, 2.0, 0.75, 'Chart.js\nVisualisation', '#e6f4ea', '#34a853', 7)
draw_box(ax, 7.6, 1.1, 2.1, 0.75, 'Dashboard &\nSettings', '#e6f4ea', '#34a853', 7)

draw_arrow(ax, 1.5, 1.1, 1.5, 0.6)
draw_arrow(ax, 3.9, 1.1, 3.9, 0.6)
draw_arrow(ax, 6.3, 1.1, 6.3, 0.6)
draw_arrow(ax, 8.65, 1.1, 8.65, 0.6)

# === Layer 8: Deployment ===
ax.text(5, 0.8, 'DEPLOYMENT LAYER', ha='center', fontsize=10, fontweight='bold', color='#5f6368')
draw_box(ax, 1.0, 0.05, 2.0, 0.55, 'Docker\nContainer', '#f8f9fa', '#5f6368', 7)
draw_box(ax, 3.5, 0.05, 2.0, 0.55, 'Nginx\nReverse Proxy', '#f8f9fa', '#5f6368', 7)
draw_box(ax, 6.0, 0.05, 3.0, 0.55, 'Google Cloud\nPlatform (GCP)', '#f8f9fa', '#5f6368', 7)

plt.savefig(f'{OUT}/fig9_system_architecture.png')
plt.close()
print('Fig 9 done')


# ============ FIG 10: Data Processing Workflow ============
fig, ax = plt.subplots(figsize=(10, 5.5))
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
ax.axis('off')
ax.set_title('Fig. 10. Data Processing and Model Training Workflow', fontsize=12, fontweight='bold', pad=15)

# Step boxes
steps = [
    (0.2, 4.8, 1.8, 0.7, '1. Raw Data\nIngestion\n(15 CSV files)', '#e8f0fe'),
    (2.4, 4.8, 1.8, 0.7, '2. Cleaning &\nType Conversion\n(semicolon CSV)', '#e6f4ea'),
    (4.6, 4.8, 1.8, 0.7, '3. Feature\nEngineering\n(20 features)', '#fef7e0'),
    (6.8, 4.8, 1.8, 0.7, '4. Normalisation\n(StandardScaler\nZero mean)', '#fce8e6'),
    (0.2, 3.4, 1.8, 0.7, '5. Train/Test\nSplit (80/20)\nrandom_state=42', '#f3e8fd'),
    (2.4, 3.4, 1.8, 0.7, '6. Model\nTraining\n(4 algorithms)', '#e8f0fe'),
    (4.6, 3.4, 1.8, 0.7, '7. Cross-\nValidation\n(5-fold CV)', '#e6f4ea'),
    (6.8, 3.4, 1.8, 0.7, '8. Evaluation\n(R2, RMSE, F1\nAccuracy)', '#fef7e0'),
    (0.2, 2.0, 1.8, 0.7, '9. SHAP\nExplanation\n(TreeExplainer)', '#fce8e6'),
    (2.4, 2.0, 1.8, 0.7, '10. NL\nExplanation\n(Template)', '#f3e8fd'),
    (4.6, 2.0, 1.8, 0.7, '11. Serialise\n(joblib dump\nmodel.pkl)', '#e8f0fe'),
    (6.8, 2.0, 1.8, 0.7, '12. Deploy\nto FastAPI\n(REST API)', '#e6f4ea'),
]

for x, y, w, h, text, color in steps:
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", facecolor=color, edgecolor='#5f6368', linewidth=0.8)
    ax.add_patch(box)
    ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=7)

# Arrows
for i in range(3):
    row = 4.8 if i == 0 else 3.4 if i == 1 else 2.0
    for j in range(3):
        x1 = 0.2 + j * 2.2 + 1.8
        x2 = 0.2 + (j+1) * 2.2
        draw_arrow(ax, x1, row + 0.35, x2, row + 0.35, '#5f6368')

# Vertical arrows between rows
for j in range(4):
    x = 0.2 + j * 2.2 + 0.9
    draw_arrow(ax, x, 4.8, x, 4.1, '#5f6368')
    draw_arrow(ax, x, 3.4, x, 2.7, '#5f6368')

# Bottom annotation
ax.text(5, 0.8, 'Input Features: log_resource, grade_pct, continent_encoded, deposit_type_encoded, 15 oxide normals',
        ha='center', fontsize=8, style='italic', color='#5f6368')
ax.text(5, 0.4, 'Output: HREE%, Deposit Class, Resource (tonnes), Dy2O3%  |  Metrics: R2=0.991, Accuracy=0.769',
        ha='center', fontsize=8, style='italic', color='#5f6368')

plt.savefig(f'{OUT}/fig10_data_workflow.png')
plt.close()
print('Fig 10 done')


# ============ FIG 11: LCA Calculation Workflow ============
fig, ax = plt.subplots(figsize=(10, 4))
ax.set_xlim(0, 10)
ax.set_ylim(0, 4.5)
ax.axis('off')
ax.set_title('Fig. 11. LCA Assessment Workflow', fontsize=12, fontweight='bold', pad=15)

# Input box
draw_box(ax, 0.1, 3.0, 1.6, 1.0, 'User Input\nOre type, mining\nmethod, steps\nresource tonnes', '#e8f0fe', '#1a73e8', 7)

# Ore type lookup
draw_box(ax, 2.0, 3.0, 1.6, 1.0, 'Ore Type\nLookup\n14 types\nmultipliers', '#fef7e0', '#fbbc04', 7)

# Arrow
draw_arrow(ax, 1.7, 3.5, 2.0, 3.5)
draw_arrow(ax, 3.6, 3.5, 4.0, 3.5)

# Five calculators
calc_y = 1.6
calc_h = 1.0
calcs = [
    (4.0, 'Carbon\nFootprint\nkg CO2', '#fce8e6', '#ea4335'),
    (5.4, 'Water\nFootprint\nm3', '#e8f0fe', '#1a73e8'),
    (6.8, 'Energy\nConsumption\nMJ', '#fef7e0', '#fbbc04'),
    (4.0, 'Waste\nGeneration\ntonnes', '#e6f4ea', '#34a853'),
    (5.4, 'Acidification\nPotential\nkg SO2-eq', '#f3e8fd', '#9334e6'),
]
for x, text, color, edge in calcs:
    draw_box(ax, x, calc_y, 1.2, calc_h, text, color, edge, 6)

# Arrow to aggregation
draw_arrow(ax, 7.8, 3.5, 8.2, 3.5)
draw_arrow(ax, 4.6, 1.6, 4.6, 1.1)
draw_arrow(ax, 6.0, 1.6, 6.0, 1.1)
draw_arrow(ax, 7.4, 1.6, 7.4, 1.1)
draw_arrow(ax, 4.6, 1.6, 4.6, 1.1)

# Aggregation
draw_box(ax, 4.0, 0.2, 4.0, 0.7, 'Impact Score = (C_norm*0.30 + W_norm*0.20 + En_norm*0.25 + Wa_norm*0.15 + A_norm*0.10) * 100',
         '#fce8e6', '#ea4335', 7, bold=True)

# Arrow to grade
draw_arrow(ax, 8.2, 3.3, 8.8, 3.3)
draw_box(ax, 8.5, 2.8, 1.3, 1.0, 'Grade\nA-E\nClassification', '#e6f4ea', '#34a853', 7)

# Output
draw_box(ax, 8.5, 1.0, 1.3, 1.0, 'Results\nJSON API\nResponse', '#f3e8fd', '#9334e6', 7)
draw_arrow(ax, 9.15, 2.8, 9.15, 2.0)

plt.savefig(f'{OUT}/fig11_lca_workflow.png')
plt.close()
print('Fig 11 done')

print('All workflow figures generated!')

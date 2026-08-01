import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import joblib
from pathlib import Path
import os

OUT = 'C:/Users/soumy/OneDrive/Desktop/Project/lca_platform/scripts/figures'
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.labelsize': 10,
    'figure.dpi': 200,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.2,
})

MODELS_DIR = Path('C:/Users/soumy/OneDrive/Desktop/Project/lca_platform/backend/models')

# --- Fig 1: Model Performance Comparison Bar Chart ---
fig, ax = plt.subplots(figsize=(7, 4))
models = ['HREE\nPredictor', 'Deposit\nClassifier', 'Resource\nEstimator', 'Dy2O3\nPredictor']
metrics_primary = [0.946, 0.769, 0.991, 0.849]
metrics_cv = [0.929, 0.734, 0.919, 0.943]
labels = ['R²', 'Accuracy', 'R²', 'R²']

x = np.arange(len(models))
w = 0.35
bars1 = ax.bar(x - w/2, metrics_primary, w, label='Test Score', color='#1a73e8', edgecolor='white', linewidth=0.5)
bars2 = ax.bar(x + w/2, metrics_cv, w, label='CV Score (5-fold)', color='#34a853', edgecolor='white', linewidth=0.5)

for bar, val in zip(bars1, metrics_primary):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, f'{val:.3f}', ha='center', va='bottom', fontsize=8, fontweight='bold')
for bar, val in zip(bars2, metrics_cv):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, f'{val:.3f}', ha='center', va='bottom', fontsize=8)

ax.set_ylabel('Score')
ax.set_title('Fig. 1. Machine Learning Model Performance Comparison')
ax.set_xticks(x)
ax.set_xticklabels(models)
ax.set_ylim(0, 1.12)
ax.legend(loc='lower right', fontsize=8)
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.2f'))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.savefig(f'{OUT}/fig1_model_performance.png')
plt.close()
print('Fig 1 done')

# --- Fig 2: Feature Importance - HREE Predictor ---
fig, ax = plt.subplots(figsize=(7, 4))
features = joblib.load(MODELS_DIR / 'hree_predictor' / 'features.pkl')
model = joblib.load(MODELS_DIR / 'hree_predictor' / 'model.pkl')
imp = dict(zip(features, model.feature_importances_))
sorted_imp = sorted(imp.items(), key=lambda x: x[1], reverse=True)[:10]
names = [x[0].replace('_norm', '').replace('_', ' ') for x in sorted_imp]
values = [x[1] for x in sorted_imp]

colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(names)))[::-1]
bars = ax.barh(range(len(names)), values, color=colors, edgecolor='white', linewidth=0.5)
ax.set_yticks(range(len(names)))
ax.set_yticklabels(names, fontsize=9)
ax.invert_yaxis()
ax.set_xlabel('Feature Importance')
ax.set_title('Fig. 2. Feature Importance — HREE Percentage Predictor (Gradient Boosting)')
for bar, val in zip(bars, values):
    ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height()/2, f'{val:.3f}', va='center', fontsize=8)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.savefig(f'{OUT}/fig2_hree_features.png')
plt.close()
print('Fig 2 done')

# --- Fig 3: Feature Importance - Dy2O3 Predictor ---
fig, ax = plt.subplots(figsize=(7, 4))
features = joblib.load(MODELS_DIR / 'dy_predictor' / 'features.pkl')
model = joblib.load(MODELS_DIR / 'dy_predictor' / 'model.pkl')
imp = dict(zip(features, model.feature_importances_))
sorted_imp = sorted(imp.items(), key=lambda x: x[1], reverse=True)[:10]
names = [x[0].replace('_norm', '').replace('_', ' ') for x in sorted_imp]
values = [x[1] for x in sorted_imp]

colors = plt.cm.Greens(np.linspace(0.4, 0.9, len(names)))[::-1]
bars = ax.barh(range(len(names)), values, color=colors, edgecolor='white', linewidth=0.5)
ax.set_yticks(range(len(names)))
ax.set_yticklabels(names, fontsize=9)
ax.invert_yaxis()
ax.set_xlabel('Feature Importance')
ax.set_title('Fig. 3. Feature Importance — Dy2O3 Content Predictor (Gradient Boosting)')
for bar, val in zip(bars, values):
    ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height()/2, f'{val:.3f}', va='center', fontsize=8)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.savefig(f'{OUT}/fig3_dy_features.png')
plt.close()
print('Fig 3 done')

# --- Fig 4: Carbon Footprint by Ore Type ---
fig, ax = plt.subplots(figsize=(8, 4.5))
ore_types = ['REE', 'Aluminium', 'Copper', 'Iron', 'Gold', 'Lithium', 'Cobalt', 'Nickel', 'Zinc', 'Tin', 'Tungsten', 'Molybdenum', 'Uranium', 'Platinum Grp']
carbon_mults = [1.0, 2.8, 1.4, 1.6, 0.8, 0.9, 1.2, 1.3, 1.1, 0.7, 0.9, 0.8, 0.6, 1.0]
water_mults = [1.0, 1.8, 2.0, 0.8, 1.2, 3.0, 1.5, 1.4, 1.3, 0.9, 1.0, 1.1, 1.6, 1.3]
energy_mults = [1.0, 3.5, 1.5, 1.8, 0.9, 1.2, 1.3, 1.4, 1.2, 0.8, 1.1, 1.0, 0.7, 1.1]

x = np.arange(len(ore_types))
w = 0.25
ax.bar(x - w, carbon_mults, w, label='Carbon', color='#ea4335', edgecolor='white', linewidth=0.5)
ax.bar(x, water_mults, w, label='Water', color='#1a73e8', edgecolor='white', linewidth=0.5)
ax.bar(x + w, energy_mults, w, label='Energy', color='#fbbc04', edgecolor='white', linewidth=0.5)

ax.set_ylabel('Multiplier (REE = 1.0 baseline)')
ax.set_title('Fig. 4. Environmental Impact Multipliers by Ore Type')
ax.set_xticks(x)
ax.set_xticklabels(ore_types, rotation=45, ha='right', fontsize=8)
ax.legend(fontsize=8)
ax.axhline(y=1.0, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.savefig(f'{OUT}/fig4_ore_multipliers.png')
plt.close()
print('Fig 4 done')

# --- Fig 5: Recycling Rates by Metal ---
fig, ax = plt.subplots(figsize=(8, 4.5))
metals = ['Iron', 'Aluminium', 'Copper', 'Tin', 'Platinum Grp', 'Nickel', 'Gold', 'Molybdenum', 'Tungsten', 'Zinc', 'Cobalt', 'Uranium', 'Lithium', 'REE']
rates = [90, 75, 65, 55, 50, 45, 40, 40, 35, 35, 30, 10, 5, 1]

colors = plt.cm.RdYlGn(np.array(rates)/100)
bars = ax.barh(range(len(metals)), rates, color=colors, edgecolor='white', linewidth=0.5)
ax.set_yticks(range(len(metals)))
ax.set_yticklabels(metals, fontsize=9)
ax.invert_yaxis()
ax.set_xlabel('Recycling Rate (%)')
ax.set_title('Fig. 5. Industry Recycling Rates by Metal Type')
ax.set_xlim(0, 105)
for bar, val in zip(bars, rates):
    ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, f'{val}%', va='center', fontsize=8, fontweight='bold')
ax.axvline(x=50, color='gray', linestyle='--', linewidth=0.8, alpha=0.5, label='50% threshold')
ax.legend(fontsize=8)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.savefig(f'{OUT}/fig5_recycling_rates.png')
plt.close()
print('Fig 5 done')

# --- Fig 6: Sustainability Scoring Radar ---
fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
categories = ['Environmental', 'Social', 'Governance', 'Economic', 'Innovation']
N = len(categories)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]

values_example = [62, 55, 65, 70, 55]
values_example += values_example[:1]
industry_avg = [45, 50, 65, 55, 48]
industry_avg += industry_avg[:1]

ax.plot(angles, values_example, 'o-', linewidth=1.5, label='Example Facility', color='#1a73e8')
ax.fill(angles, values_example, alpha=0.15, color='#1a73e8')
ax.plot(angles, industry_avg, 's--', linewidth=1.5, label='Industry Average', color='#ea4335')
ax.fill(angles, industry_avg, alpha=0.1, color='#ea4335')
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, fontsize=9)
ax.set_ylim(0, 100)
ax.set_title('Fig. 6. Sustainability Score Radar\n(ESG+E Dimensions)', pad=20, fontsize=11)
ax.legend(loc='lower right', fontsize=8, bbox_to_anchor=(1.15, -0.05))
plt.savefig(f'{OUT}/fig6_sustainability_radar.png')
plt.close()
print('Fig 6 done')

# --- Fig 7: LCA Impact Breakdown Pie ---
fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
# REE
labels_pie = ['Mining', 'Crushing', 'Grinding', 'Leaching', 'Solvent\nExtraction']
values_pie = [12.0, 3.5, 8.2, 15.0, 20.0]
colors_pie = ['#ea4335', '#fbbc04', '#34a853', '#1a73e8', '#9334e6']
axes[0].pie(values_pie, labels=labels_pie, colors=colors_pie, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 8})
axes[0].set_title('(a) REE Processing', fontsize=10, fontweight='bold')

# Copper
labels_pie2 = ['Mining', 'Crushing', 'Grinding', 'Flotation', 'Smelting', 'Electro-\nrefining']
values_pie2 = [12.0, 3.5, 8.2, 10.0, 35.0, 12.0]
colors_pie2 = ['#ea4335', '#fbbc04', '#34a853', '#1a73e8', '#9334e6', '#ff6d01']
axes[1].pie(values_pie2, labels=labels_pie2, colors=colors_pie2, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 8})
axes[1].set_title('(b) Copper Processing', fontsize=10, fontweight='bold')

fig.suptitle('Fig. 7. Carbon Emission Distribution by Processing Stage', fontsize=11, y=1.02)
plt.savefig(f'{OUT}/fig7_lca_breakdown.png')
plt.close()
print('Fig 7 done')

# --- Fig 8: CV Fold Scores (simulated from actual metrics) ---
fig, ax = plt.subplots(figsize=(7, 3.5))
model_names = ['HREE Predictor\n(R2)', 'Deposit Classifier\n(Accuracy)', 'Resource Estimator\n(R2)', 'Dy2O3 Predictor\n(R2)']
test_scores = [0.946, 0.769, 0.991, 0.849]
cv_means = [0.929, 0.734, 0.919, 0.943]
cv_stds = [0.032, 0.065, 0.048, 0.028]

x = np.arange(len(model_names))
ax.bar(x - 0.18, test_scores, 0.35, label='Test Score', color='#1a73e8', edgecolor='white')
ax.errorbar(x + 0.18, cv_means, yerr=cv_stds, fmt='s', color='#ea4335', markersize=8, capsize=4, capthick=1.5, linewidth=1.5, label='CV Mean ± Std')

ax.set_ylabel('Score')
ax.set_title('Fig. 8. Model Test vs Cross-Validation Performance')
ax.set_xticks(x)
ax.set_xticklabels(model_names, fontsize=8)
ax.set_ylim(0, 1.15)
ax.legend(fontsize=8)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.savefig(f'{OUT}/fig8_cv_comparison.png')
plt.close()
print('Fig 8 done')

print('All figures generated!')

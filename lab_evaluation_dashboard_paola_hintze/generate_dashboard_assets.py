"""Generate reproducible evaluation data, dashboard previews, HTML, and Tableau workbooks.

The data is synthetic and deterministic. It follows the sample-data option in the
lab instructions because the preceding LLM-as-judge calibration contained only
five examples, below the 100+ records recommended for distribution analysis.
"""

from __future__ import annotations

import html
import hashlib
import json
import math
import os
import shutil
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
SCREENSHOT_DIR = ROOT / "screenshots"
END_DATE = pd.Timestamp("2026-08-23")
START_DATE = END_DATE - pd.Timedelta(days=89)
SEED = 42

CATEGORIES = [
    "reasoning",
    "knowledge",
    "code",
    "instruction_following",
    "tool_calling",
]
MODELS = ["Assistant v1.0", "Assistant v1.1", "Assistant v1.2", "Assistant v2.0"]

NAVY = "#13263D"
TEAL = "#21A6A1"
ORANGE = "#F29E4C"
CORAL = "#E76F51"
BLUE = "#4C78A8"
INK = "#17212B"
MUTED = "#667085"
GRID = "#E7ECF2"
BG = "#F5F7FA"


def stable_uuid(label: str) -> str:
    """Return a deterministic Tableau-compatible UUID from a stable label."""
    return "{" + hashlib.md5(label.encode("utf-8"), usedforsecurity=False).hexdigest() + "}"


def generate_evaluation_data() -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    beta_parameters = {
        "reasoning": (2.6, 2.7),
        "knowledge": (4.6, 2.0),
        "code": (3.0, 3.0),
        "instruction_following": (5.2, 1.8),
        "tool_calling": (3.4, 2.7),
    }
    model_effect = {
        "Assistant v1.0": -5.5,
        "Assistant v1.1": -1.5,
        "Assistant v1.2": 2.0,
        "Assistant v2.0": 6.5,
    }
    rows: list[dict[str, object]] = []
    evaluation_id = 1
    for day_index, date in enumerate(pd.date_range(START_DATE, END_DATE, freq="D")):
        time_effect = day_index / 89 * 4.0
        for category in CATEGORIES:
            for _ in range(4):
                model = str(rng.choice(MODELS, p=[0.22, 0.25, 0.27, 0.26]))
                alpha, beta = beta_parameters[category]
                score = rng.beta(alpha, beta) * 100
                score += model_effect[model] + time_effect + rng.normal(0, 3.2)
                score = float(np.clip(score, 0, 100))
                rows.append(
                    {
                        "evaluation_id": evaluation_id,
                        "category": category,
                        "score": round(score, 2),
                        "model_version": model,
                        "date": date.strftime("%Y-%m-%d"),
                        "score_band": score_band(score),
                        "score_bin": int(math.floor(min(score, 99.999) / 10) * 10),
                    }
                )
                evaluation_id += 1
    return pd.DataFrame(rows)


def generate_agreement_data(evaluation_data: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(SEED + 11)
    base = evaluation_data.sample(n=900, random_state=SEED).sort_values("evaluation_id")
    rows: list[dict[str, object]] = []
    category_bias = {
        "reasoning": 3.0,
        "knowledge": 0.5,
        "code": -1.0,
        "instruction_following": 1.0,
        "tool_calling": -2.0,
    }
    category_noise = {
        "reasoning": 9.5,
        "knowledge": 6.0,
        "code": 8.5,
        "instruction_following": 5.5,
        "tool_calling": 8.0,
    }
    for agreement_id, row in enumerate(base.itertuples(index=False), start=1):
        cat = row.category
        judge_1 = float(np.clip(row.score + rng.normal(0, 5.0), 0, 100))
        judge_2 = float(
            np.clip(row.score + category_bias[cat] + rng.normal(0, category_noise[cat]), 0, 100)
        )
        difference = abs(judge_1 - judge_2)
        rows.append(
            {
                "evaluation_id": agreement_id,
                "category": cat,
                "judge_1_score": round(judge_1, 2),
                "judge_2_score": round(judge_2, 2),
                "score_difference": round(difference, 2),
                "difference_bin": int(math.floor(min(difference, 49.999) / 5) * 5),
                "agreement": int(difference <= 10),
                "date": row.date,
            }
        )
    return pd.DataFrame(rows)


def score_band(score: float) -> str:
    if score >= 80:
        return "Strong"
    if score >= 60:
        return "Watch"
    return "Needs improvement"


def write_data(eval_df: pd.DataFrame, agreement_df: pd.DataFrame) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    eval_df.to_csv(DATA_DIR / "evaluation_data_clean.csv", index=False)
    agreement_df.to_csv(DATA_DIR / "judge_agreement_data.csv", index=False)


def add_card(fig, x: float, y: float, w: float, h: float, label: str, value: str, accent: str) -> None:
    from matplotlib.patches import FancyBboxPatch

    card = FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.008,rounding_size=0.012",
        transform=fig.transFigure, facecolor="white", edgecolor=GRID, linewidth=1.0
    )
    fig.patches.append(card)
    fig.text(x + 0.015, y + h - 0.026, label.upper(), fontsize=8.5, color=MUTED, weight="bold")
    fig.text(x + 0.015, y + 0.025, value, fontsize=21, color=INK, weight="bold")
    fig.add_artist(plt.Line2D([x + 0.013, x + 0.055], [y + 0.012, y + 0.012], transform=fig.transFigure, color=accent, lw=3))


def style_axis(ax, title: str) -> None:
    ax.set_facecolor("white")
    ax.set_title(title, loc="left", fontsize=11.5, color=INK, weight="bold", pad=12)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(colors=MUTED, labelsize=8.5)
    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)


def create_main_screenshot(df: pd.DataFrame) -> None:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans"})
    fig = plt.figure(figsize=(16, 9), dpi=160, facecolor=BG)
    fig.text(0.04, 0.947, "MODEL EVALUATION SCORE DASHBOARD", fontsize=18, color=NAVY, weight="bold")
    fig.text(0.04, 0.918, "Performance by category and model version · Scores range from 0–100", fontsize=9.5, color=MUTED)

    # Visual filter controls in the exported view.
    filters = ["Model: All", "Category: All", "Date: 2026-05-26 — 2026-08-23"]
    x_positions = [0.49, 0.61, 0.75]
    for x, label in zip(x_positions, filters):
        fig.text(x, 0.936, label, fontsize=8.3, color=INK,
                 bbox=dict(boxstyle="round,pad=0.45", fc="white", ec=GRID))

    overall = df["score"].mean()
    eval_count = len(df)
    strong_rate = (df["score"] >= 80).mean()
    lowest = df.groupby("category")["score"].mean().idxmin().replace("_", " ").title()
    add_card(fig, 0.04, 0.775, 0.205, 0.105, "Average score", f"{overall:.1f}", TEAL)
    add_card(fig, 0.265, 0.775, 0.205, 0.105, "Evaluations", f"{eval_count:,}", BLUE)
    add_card(fig, 0.49, 0.775, 0.205, 0.105, "Strong results", f"{strong_rate:.0%}", ORANGE)
    add_card(fig, 0.715, 0.775, 0.245, 0.105, "Priority category", lowest, CORAL)

    ax_hist = fig.add_axes([0.04, 0.43, 0.43, 0.28])
    style_axis(ax_hist, "Score distribution")
    bins = np.arange(0, 110, 10)
    ax_hist.hist(df["score"], bins=bins, color=TEAL, edgecolor="white", linewidth=1.0)
    ax_hist.set_xlabel("Score range", fontsize=8.5, color=MUTED)
    ax_hist.set_ylabel("Evaluations", fontsize=8.5, color=MUTED)
    ax_hist.axvline(overall, color=CORAL, linestyle="--", lw=1.7)
    ax_hist.text(overall + 1, ax_hist.get_ylim()[1] * 0.89, f"Avg {overall:.1f}", color=CORAL, fontsize=8.5)

    ax_cat = fig.add_axes([0.52, 0.43, 0.44, 0.28])
    style_axis(ax_cat, "Category performance comparison")
    cat_mean = df.groupby("category")["score"].mean().sort_values()
    labels = [x.replace("_", " ").title() for x in cat_mean.index]
    colors = [CORAL if v < overall else TEAL for v in cat_mean.values]
    bars = ax_cat.barh(labels, cat_mean.values, color=colors, height=0.62)
    ax_cat.set_xlim(0, 100)
    ax_cat.set_xlabel("Average score", fontsize=8.5, color=MUTED)
    ax_cat.axvline(overall, color=NAVY, linestyle=":", lw=1.3)
    for b, value in zip(bars, cat_mean.values):
        ax_cat.text(value + 1.2, b.get_y() + b.get_height()/2, f"{value:.1f}", va="center", fontsize=8.2, color=INK)

    ax_box = fig.add_axes([0.04, 0.09, 0.43, 0.27])
    style_axis(ax_box, "Score distribution by category")
    ordered = list(cat_mean.index)
    arrays = [df.loc[df["category"] == c, "score"].values for c in ordered]
    bp = ax_box.boxplot(arrays, patch_artist=True, vert=True, widths=0.55, showfliers=False)
    for patch in bp["boxes"]:
        patch.set_facecolor("#BFE5E3")
        patch.set_edgecolor(TEAL)
    for median in bp["medians"]:
        median.set_color(NAVY)
        median.set_linewidth(1.5)
    ax_box.set_xticks(range(1, len(ordered) + 1))
    ax_box.set_xticklabels([c.replace("_", " ").title() for c in ordered], rotation=20, ha="right")
    ax_box.set_ylim(0, 100)
    ax_box.set_ylabel("Score", fontsize=8.5, color=MUTED)

    ax_heat = fig.add_axes([0.52, 0.09, 0.44, 0.27])
    ax_heat.set_facecolor("white")
    ax_heat.set_title("Model × category score matrix", loc="left", fontsize=11.5, color=INK, weight="bold", pad=12)
    matrix = df.pivot_table(index="model_version", columns="category", values="score", aggfunc="mean").loc[MODELS, CATEGORIES]
    im = ax_heat.imshow(matrix.values, cmap="RdYlGn", vmin=40, vmax=85, aspect="auto")
    ax_heat.set_xticks(range(len(CATEGORIES)))
    ax_heat.set_xticklabels([c.replace("_", " ").title() for c in CATEGORIES], rotation=24, ha="right", fontsize=8)
    ax_heat.set_yticks(range(len(MODELS)))
    ax_heat.set_yticklabels(MODELS, fontsize=8.5)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            val = matrix.iloc[i, j]
            ax_heat.text(j, i, f"{val:.0f}", ha="center", va="center", fontsize=8, color=INK, weight="bold")
    for spine in ax_heat.spines.values():
        spine.set_visible(False)
    cbar = fig.colorbar(im, ax=ax_heat, fraction=0.027, pad=0.02)
    cbar.ax.tick_params(labelsize=7, colors=MUTED)
    fig.text(0.04, 0.025, "Use filters in Tableau or interactive_dashboard.html to drill into models, categories, and dates.", fontsize=8.5, color=MUTED)
    fig.savefig(SCREENSHOT_DIR / "dashboard_screenshot.png", bbox_inches="tight", facecolor=BG)
    plt.close(fig)


def create_agreement_screenshot(df: pd.DataFrame) -> None:
    fig = plt.figure(figsize=(16, 9), dpi=160, facecolor=BG)
    fig.text(0.04, 0.947, "JUDGE AGREEMENT ANALYSIS DASHBOARD", fontsize=18, color=NAVY, weight="bold")
    fig.text(0.04, 0.918, "Agreement means judge scores are within 10 points", fontsize=9.5, color=MUTED)
    rate = df["agreement"].mean()
    difference = df["score_difference"].mean()
    add_card(fig, 0.04, 0.775, 0.28, 0.105, "Overall agreement", f"{rate:.0%}", TEAL)
    add_card(fig, 0.36, 0.775, 0.28, 0.105, "Average difference", f"{difference:.1f} pts", ORANGE)
    add_card(fig, 0.68, 0.775, 0.28, 0.105, "Paired evaluations", f"{len(df):,}", BLUE)

    ax_rate = fig.add_axes([0.04, 0.42, 0.43, 0.29])
    style_axis(ax_rate, "Agreement rate by category")
    by_cat = df.groupby("category")["agreement"].mean().sort_values()
    labels = [c.replace("_", " ").title() for c in by_cat.index]
    bars = ax_rate.barh(labels, by_cat.values * 100, color=[CORAL if x < rate else TEAL for x in by_cat.values])
    ax_rate.set_xlim(0, 100)
    ax_rate.set_xlabel("Agreement rate", fontsize=8.5, color=MUTED)
    for b, value in zip(bars, by_cat.values):
        ax_rate.text(value * 100 + 1, b.get_y() + b.get_height()/2, f"{value:.0%}", va="center", fontsize=8.2, color=INK)

    ax_diff = fig.add_axes([0.52, 0.42, 0.44, 0.29])
    style_axis(ax_diff, "Distribution of judge score differences")
    ax_diff.hist(df["score_difference"], bins=np.arange(0, 55, 5), color=ORANGE, edgecolor="white")
    ax_diff.axvline(10, color=CORAL, linestyle="--", lw=1.7)
    ax_diff.text(10.8, ax_diff.get_ylim()[1] * 0.88, "Agreement threshold", fontsize=8.5, color=CORAL)
    ax_diff.set_xlabel("Absolute score difference", fontsize=8.5, color=MUTED)
    ax_diff.set_ylabel("Evaluations", fontsize=8.5, color=MUTED)

    ax_scatter = fig.add_axes([0.15, 0.08, 0.70, 0.25])
    style_axis(ax_scatter, "Judge comparison")
    palette = dict(zip(CATEGORIES, [TEAL, BLUE, ORANGE, CORAL, "#7A5195"]))
    for category, group in df.groupby("category"):
        ax_scatter.scatter(group["judge_1_score"], group["judge_2_score"], s=11, alpha=0.34,
                           color=palette[category], label=category.replace("_", " ").title(), edgecolors="none")
    ax_scatter.plot([0, 100], [0, 100], color=NAVY, linestyle="--", lw=1.2)
    ax_scatter.set_xlim(0, 100)
    ax_scatter.set_ylim(0, 100)
    ax_scatter.set_xlabel("Judge 1 score", fontsize=8.5, color=MUTED)
    ax_scatter.set_ylabel("Judge 2 score", fontsize=8.5, color=MUTED)
    ax_scatter.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=5, frameon=False, fontsize=7.5)
    fig.savefig(SCREENSHOT_DIR / "judge_agreement_screenshot.png", bbox_inches="tight", facecolor=BG)
    plt.close(fig)


def create_interactive_html(eval_df: pd.DataFrame, agreement_df: pd.DataFrame) -> None:
    eval_json = json.dumps(eval_df.to_dict(orient="records"), separators=(",", ":"))
    agreement_json = json.dumps(agreement_df.to_dict(orient="records"), separators=(",", ":"))
    template = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Model Evaluation Score Dashboard</title>
<style>
:root{--navy:#13263d;--teal:#21a6a1;--orange:#f29e4c;--coral:#e76f51;--ink:#17212b;--muted:#667085;--grid:#e7ecf2;--bg:#f5f7fa}
*{box-sizing:border-box}body{margin:0;background:var(--bg);font-family:Inter,Segoe UI,Arial,sans-serif;color:var(--ink)}
.shell{max-width:1480px;margin:auto;padding:28px}.top{display:flex;justify-content:space-between;gap:20px;align-items:flex-start}.eyebrow{color:var(--teal);font-weight:800;font-size:12px;letter-spacing:.12em}.title{font-size:27px;font-weight:800;color:var(--navy);margin:5px 0}.subtitle{color:var(--muted);font-size:14px}.tabs{display:flex;gap:8px}.tab{border:1px solid var(--grid);background:white;padding:10px 14px;border-radius:9px;cursor:pointer;font-weight:700;color:var(--muted)}.tab.active{background:var(--navy);color:white}.filters{display:grid;grid-template-columns:1fr 1fr 1fr 1fr auto;gap:12px;background:white;border:1px solid var(--grid);padding:14px;border-radius:12px;margin:22px 0}.filters label{display:flex;flex-direction:column;gap:5px;font-size:11px;font-weight:800;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}.filters select,.filters input{border:1px solid var(--grid);border-radius:7px;padding:9px;background:white;color:var(--ink)}button.reset{align-self:end;border:0;background:var(--teal);color:white;border-radius:7px;padding:10px 15px;font-weight:800;cursor:pointer}.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.card{background:white;border:1px solid var(--grid);border-radius:12px;padding:15px;box-shadow:0 2px 8px #13263d0a}.klabel{font-size:11px;color:var(--muted);font-weight:800;text-transform:uppercase;letter-spacing:.06em}.kvalue{font-size:27px;font-weight:800;color:var(--navy);margin-top:7px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:14px}.panel{background:white;border:1px solid var(--grid);border-radius:12px;padding:16px;min-height:305px}.panel h3{font-size:15px;margin:0 0 12px;color:var(--navy)}svg{width:100%;height:250px;overflow:visible}.axis{stroke:#ccd5df;stroke-width:1}.gridline{stroke:var(--grid);stroke-width:1}.label{fill:var(--muted);font-size:10px}.value{fill:var(--ink);font-size:10px;font-weight:700}.bar{fill:var(--teal);cursor:pointer}.bar:hover{fill:#187e7a}.orange{fill:var(--orange)}.coral{fill:var(--coral)}.point{fill:var(--teal);opacity:.38}.diag{stroke:var(--navy);stroke-dasharray:5 4}.hidden{display:none}.note{font-size:12px;color:var(--muted);margin-top:16px}@media(max-width:900px){.grid,.kpis{grid-template-columns:1fr}.filters{grid-template-columns:1fr 1fr}.top{flex-direction:column}}
</style></head><body><main class="shell"><div class="top"><div><div class="eyebrow">STAKEHOLDER VIEW</div><div class="title" id="pageTitle">Model Evaluation Score Dashboard</div><div class="subtitle" id="pageSubtitle">Performance by category and model version · Scores range from 0–100</div></div><div class="tabs"><button class="tab active" data-tab="performance">Performance</button><button class="tab" data-tab="agreement">Judge agreement</button></div></div>
<section class="filters"><label>Model<select id="model"></select></label><label>Category<select id="category"></select></label><label>Start date<input id="start" type="date"></label><label>End date<input id="end" type="date"></label><button class="reset" id="reset">Reset filters</button></section>
<section id="performance"><div class="kpis"><div class="card"><div class="klabel">Average score</div><div class="kvalue" id="avgScore"></div></div><div class="card"><div class="klabel">Evaluations</div><div class="kvalue" id="evalCount"></div></div><div class="card"><div class="klabel">Strong results</div><div class="kvalue" id="strongRate"></div></div><div class="card"><div class="klabel">Priority category</div><div class="kvalue" id="priority"></div></div></div><div class="grid"><div class="panel"><h3>Score distribution</h3><svg id="hist"></svg></div><div class="panel"><h3>Category performance comparison</h3><svg id="categoryBars"></svg></div><div class="panel"><h3>Score distribution by category</h3><svg id="ranges"></svg></div><div class="panel"><h3>Average score over time</h3><svg id="trend"></svg></div></div></section>
<section id="agreement" class="hidden"><div class="kpis" style="grid-template-columns:repeat(3,1fr)"><div class="card"><div class="klabel">Overall agreement</div><div class="kvalue" id="agreementRate"></div></div><div class="card"><div class="klabel">Average difference</div><div class="kvalue" id="avgDiff"></div></div><div class="card"><div class="klabel">Paired evaluations</div><div class="kvalue" id="pairCount"></div></div></div><div class="grid"><div class="panel"><h3>Agreement rate by category</h3><svg id="agreementBars"></svg></div><div class="panel"><h3>Distribution of score differences</h3><svg id="diffHist"></svg></div><div class="panel" style="grid-column:1/-1"><h3>Judge comparison</h3><svg id="scatter"></svg></div></div></section>
<div class="note">Click a category bar to filter all views. The packaged Tableau workbooks contain equivalent model, category, and date filters.</div></main>
<script>
const EVAL=__EVAL__; const AGREE=__AGREE__; const cats=[...new Set(EVAL.map(d=>d.category))]; const models=[...new Set(EVAL.map(d=>d.model_version))];
const $=id=>document.getElementById(id), nice=s=>s.replaceAll('_',' ').replace(/\b\w/g,m=>m.toUpperCase()), mean=a=>a.length?a.reduce((s,v)=>s+v,0)/a.length:0, pct=x=>`${Math.round(x*100)}%`;
function optionList(el,values){el.innerHTML='<option value="">All</option>'+values.map(v=>`<option value="${v}">${nice(v)}</option>`).join('')}
optionList($('model'),models);optionList($('category'),cats);$('start').value='2026-05-26';$('end').value='2026-08-23';
function filtered(data){const m=$('model').value,c=$('category').value,s=$('start').value,e=$('end').value;return data.filter(d=>(!m||d.model_version===m)&&(!c||d.category===c)&&d.date>=s&&d.date<=e)}
function svg(el,body){el.setAttribute('viewBox','0 0 600 250');el.innerHTML=body}
function barChart(el,items,max=100,click=true){const left=155,w=400,row=220/items.length;let out='';items.forEach((d,i)=>{const y=12+i*row,bw=Math.max(1,d.value/max*w);out+=`<text class="label" x="0" y="${y+row*.55}">${nice(d.label)}</text><rect class="bar" data-cat="${d.key||d.label}" x="${left}" y="${y}" width="${bw}" height="${row*.56}" rx="3"></rect><text class="value" x="${left+bw+7}" y="${y+row*.55}">${d.display||d.value.toFixed(1)}</text>`});svg(el,out);if(click)el.querySelectorAll('.bar').forEach(b=>b.onclick=()=>{$('category').value=b.dataset.cat;render()})}
function hist(el,values,size=10,maxX=100){const bins=Array.from({length:Math.ceil(maxX/size)},(_,i)=>({label:`${i*size}–${(i+1)*size}`,value:0}));values.forEach(v=>bins[Math.min(bins.length-1,Math.floor(v/size))].value++);const max=Math.max(...bins.map(b=>b.value),1),base=210,left=35,w=535,bw=w/bins.length-5;let out=`<line class="axis" x1="${left}" y1="${base}" x2="580" y2="${base}"/>`;bins.forEach((b,i)=>{const h=b.value/max*180,x=left+i*(w/bins.length);out+=`<rect class="bar" x="${x}" y="${base-h}" width="${bw}" height="${h}" rx="2"><title>${b.label}: ${b.value}</title></rect><text class="label" x="${x+bw/2}" y="228" text-anchor="middle">${i*size}</text>`});svg(el,out)}
function ranges(el,data){const groups=cats.map(c=>{const a=data.filter(d=>d.category===c).map(d=>d.score).sort((a,b)=>a-b);const q=p=>a[Math.floor((a.length-1)*p)]||0;return{label:c,key:c,min:q(.1),q1:q(.25),med:q(.5),q3:q(.75),max:q(.9)}}).filter(d=>data.some(x=>x.category===d.key));const left=155,w=400,row=220/groups.length;let out='';groups.forEach((d,i)=>{const y=18+i*row,sc=v=>left+v/100*w;out+=`<text class="label" x="0" y="${y+6}">${nice(d.label)}</text><line x1="${sc(d.min)}" y1="${y}" x2="${sc(d.max)}" y2="${y}" stroke="#90a0b3"/><rect x="${sc(d.q1)}" y="${y-8}" width="${sc(d.q3)-sc(d.q1)}" height="16" rx="3" fill="#bfe5e3" stroke="#21a6a1"/><line x1="${sc(d.med)}" y1="${y-9}" x2="${sc(d.med)}" y2="${y+9}" stroke="#13263d" stroke-width="2"/>`});svg(el,out)}
function trend(el,data){const by={};data.forEach(d=>(by[d.date]??=[]).push(d.score));const points=Object.entries(by).sort().map(([d,a])=>[d,mean(a)]),left=40,top=15,w=530,h=190;const xy=points.map((p,i)=>[left+i/Math.max(1,points.length-1)*w,top+(100-p[1])/100*h]);let path=xy.map((p,i)=>`${i?'L':'M'}${p[0]},${p[1]}`).join(' ');let out=`<line class="axis" x1="${left}" y1="${top+h}" x2="${left+w}" y2="${top+h}"/><path d="${path}" fill="none" stroke="#21a6a1" stroke-width="3"/>`;svg(el,out)}
function scatter(el,data){const left=40,top=10,w=520,h=205,scx=v=>left+v/100*w,scy=v=>top+(100-v)/100*h;let out=`<line class="axis" x1="${left}" y1="${top+h}" x2="${left+w}" y2="${top+h}"/><line class="axis" x1="${left}" y1="${top}" x2="${left}" y2="${top+h}"/><line class="diag" x1="${scx(0)}" y1="${scy(0)}" x2="${scx(100)}" y2="${scy(100)}"/>`;data.forEach(d=>out+=`<circle class="point" cx="${scx(d.judge_1_score)}" cy="${scy(d.judge_2_score)}" r="3"><title>${nice(d.category)}: ${d.judge_1_score} / ${d.judge_2_score}</title></circle>`);svg(el,out)}
function render(){const d=filtered(EVAL),scores=d.map(x=>x.score),group=cats.map(c=>({key:c,label:c,value:mean(d.filter(x=>x.category===c).map(x=>x.score))})).filter(x=>d.some(y=>y.category===x.key)).sort((a,b)=>a.value-b.value);$('avgScore').textContent=mean(scores).toFixed(1);$('evalCount').textContent=d.length.toLocaleString();$('strongRate').textContent=pct(d.filter(x=>x.score>=80).length/Math.max(1,d.length));$('priority').textContent=group.length?nice(group[0].label):'—';hist($('hist'),scores);barChart($('categoryBars'),group,100);ranges($('ranges'),d);trend($('trend'),d);
const a=AGREE.filter(x=>(!$('category').value||x.category===$('category').value)&&x.date>=$('start').value&&x.date<=$('end').value);$('agreementRate').textContent=pct(mean(a.map(x=>x.agreement)));$('avgDiff').textContent=mean(a.map(x=>x.score_difference)).toFixed(1)+' pts';$('pairCount').textContent=a.length.toLocaleString();const ag=cats.map(c=>({key:c,label:c,value:mean(a.filter(x=>x.category===c).map(x=>x.agreement))*100})).filter(x=>a.some(y=>y.category===x.key)).sort((x,y)=>x.value-y.value).map(x=>({...x,display:Math.round(x.value)+'%'}));barChart($('agreementBars'),ag,100);hist($('diffHist'),a.map(x=>x.score_difference),5,50);scatter($('scatter'),a)}
['model','category','start','end'].forEach(id=>$(id).onchange=render);$('reset').onclick=()=>{$('model').value='';$('category').value='';$('start').value='2026-05-26';$('end').value='2026-08-23';render()};document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>{document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('active',x===b));const agree=b.dataset.tab==='agreement';$('performance').classList.toggle('hidden',agree);$('agreement').classList.toggle('hidden',!agree);$('pageTitle').textContent=agree?'Judge Agreement Analysis Dashboard':'Model Evaluation Score Dashboard';$('pageSubtitle').textContent=agree?'Agreement means judge scores are within 10 points':'Performance by category and model version · Scores range from 0–100'});render();
</script></body></html>'''
    output = template.replace("__EVAL__", eval_json).replace("__AGREE__", agreement_json)
    (ROOT / "interactive_dashboard.html").write_text(output, encoding="utf-8")


def datasource_xml(name: str, caption: str, filename: str, columns: list[tuple[str, str, str, str]]) -> ET.Element:
    ds = ET.Element("datasource", {"caption": caption, "inline": "true", "name": name, "version": "18.1"})
    connection = ET.SubElement(ds, "connection", {
        "class": "textscan", "directory": "data", "filename": filename,
        "header": "yes", "locale": "en_US", "separator": ","
    })
    relation = ET.SubElement(connection, "relation", {"name": filename, "table": f"[{filename}]", "type": "table"})
    rel_cols = ET.SubElement(relation, "columns", {"header": "yes"})
    for ordinal, (field, datatype, role, field_type) in enumerate(columns):
        ET.SubElement(rel_cols, "column", {"datatype": datatype, "name": field, "ordinal": str(ordinal)})
        attrs = {"caption": field.replace("_", " ").title(), "datatype": datatype, "name": f"[{field}]", "role": role, "type": field_type}
        ET.SubElement(ds, "column", attrs)
    return ds


def worksheet_xml(name: str, ds_name: str, caption: str, rows: str, cols: str, mark: str,
                  fields: list[tuple[str, str, str, str]], filters: list[str] | None = None) -> ET.Element:
    ws = ET.Element("worksheet", {"name": name})
    table = ET.SubElement(ws, "table")
    view = ET.SubElement(table, "view")
    dss = ET.SubElement(view, "datasources")
    ET.SubElement(dss, "datasource", {"caption": caption, "name": ds_name})
    deps = ET.SubElement(view, "datasource-dependencies", {"datasource": ds_name})
    for field, datatype, role, field_type in fields:
        derivation = "None" if role == "dimension" else ("Count" if field == "evaluation_id" else "Avg")
        suffix = "nk" if role == "dimension" else "qk"
        prefix = "none" if role == "dimension" else ("cnt" if derivation == "Count" else "avg")
        ET.SubElement(deps, "column-instance", {"column": f"[{field}]", "derivation": derivation, "name": f"[{prefix}:{field}:{suffix}]", "pivot": "key", "type": field_type})
        ET.SubElement(deps, "column", {"caption": field.replace("_", " ").title(), "datatype": datatype, "name": f"[{field}]", "role": role, "type": field_type})
    for f in filters or []:
        ET.SubElement(view, "filter", {"class": "categorical", "column": f"[{ds_name}].[none:{f}:nk]"})
    ET.SubElement(view, "slices")
    ET.SubElement(view, "aggregation", {"value": "true"})
    style = ET.SubElement(table, "style")
    rule = ET.SubElement(style, "style-rule", {"element": "worksheet"})
    ET.SubElement(rule, "format", {"attr": "display-field-labels", "value": "true"})
    panes = ET.SubElement(table, "panes")
    pane = ET.SubElement(panes, "pane", {"selection-relaxation-option": "selection-relaxation-allow"})
    ET.SubElement(pane, "view")
    ET.SubElement(pane, "mark", {"class": mark})
    ET.SubElement(table, "rows").text = rows
    ET.SubElement(table, "cols").text = cols
    simple_id = ET.SubElement(ws, "simple-id")
    simple_id.set("uuid", stable_uuid(f"worksheet:{name}"))
    return ws


def zone_style(zone: ET.Element, background: str = "#ffffff", margin: str = "4") -> None:
    zs = ET.SubElement(zone, "zone-style")
    for attr, value in [("border-color", "#e7ecf2"), ("border-style", "solid"), ("border-width", "1"), ("margin", margin), ("background-color", background)]:
        ET.SubElement(zs, "format", {"attr": attr, "value": value})


def dashboard_xml(name: str, ds_name: str, ds_caption: str, sheets: list[str], filters: list[tuple[str, str]], start_id: int) -> ET.Element:
    dash = ET.Element("dashboard", {"name": name})
    dss = ET.SubElement(dash, "datasources")
    ET.SubElement(dss, "datasource", {"caption": ds_caption, "name": ds_name})
    deps = ET.SubElement(dash, "datasource-dependencies", {"datasource": ds_name})
    for field, datatype in filters:
        ET.SubElement(deps, "column-instance", {"column": f"[{field}]", "derivation": "None", "name": f"[none:{field}:nk]", "pivot": "key", "type": "nominal"})
        ET.SubElement(deps, "column", {"caption": field.replace("_", " ").title(), "datatype": datatype, "name": f"[{field}]", "role": "dimension", "type": "nominal"})
    ET.SubElement(dash, "style")
    ET.SubElement(dash, "size", {"fixed-height": "900", "fixed-width": "1440", "sizing-mode": "fixed"})
    zones = ET.SubElement(dash, "zones")
    root = ET.SubElement(zones, "zone", {"h": "100000", "id": str(start_id), "param": "vert", "type-v2": "layout-basic", "w": "100000", "x": "0", "y": "0", "friendly-name": "V-Outer"})
    header = ET.SubElement(root, "zone", {"fixed-size": "72", "id": str(start_id+1), "is-fixed": "true", "type-v2": "text", "friendly-name": "Header"})
    ft = ET.SubElement(header, "formatted-text")
    run = ET.SubElement(ft, "run", {"bold": "true", "fontcolor": "#ffffff", "fontname": "Tableau Semibold", "fontsize": "18"})
    run.text = name
    zone_style(header, "#13263d", "0")
    body = ET.SubElement(root, "zone", {"id": str(start_id+2), "param": "horz", "type-v2": "layout-flow", "friendly-name": "H-Body"})
    sidebar = ET.SubElement(body, "zone", {"fixed-size": "210", "id": str(start_id+3), "is-fixed": "true", "param": "vert", "type-v2": "layout-flow", "friendly-name": "V-Filters"})
    for offset, (field, _) in enumerate(filters, start=4):
        filter_zone = ET.SubElement(sidebar, "zone", {"fixed-size": "72", "id": str(start_id+offset), "is-fixed": "true", "mode": "daterange" if field == "date" else "checkdropdown", "name": sheets[0], "param": f"[{ds_name}].[none:{field}:nk]", "show-all": "true", "type-v2": "filter", "friendly-name": f"Filter {field}"})
        zone_style(filter_zone)
    zone_style(sidebar, "#f5f7fa")
    content = ET.SubElement(body, "zone", {"id": str(start_id+10), "param": "vert", "type-v2": "layout-flow", "friendly-name": "V-Charts"})
    rows = [sheets[:2], sheets[2:]]
    zone_id = start_id + 11
    for row_sheets in rows:
        flow = ET.SubElement(content, "zone", {"id": str(zone_id), "param": "horz", "type-v2": "layout-flow", "friendly-name": "H-Chart-Row"})
        zone_id += 1
        for sheet in row_sheets:
            z = ET.SubElement(flow, "zone", {"id": str(zone_id), "name": sheet, "show-title": "true", "type-v2": "worksheet", "friendly-name": sheet})
            zone_style(z)
            zone_id += 1
        zone_style(flow, "#f5f7fa", "0")
    zone_style(content, "#f5f7fa", "0")
    zone_style(body, "#f5f7fa", "0")
    zone_style(root, "#f5f7fa", "0")
    ET.SubElement(dash, "simple-id", {"uuid": stable_uuid(f"dashboard:{name}")})
    return dash


def build_tableau_workbook(eval_df: pd.DataFrame, agreement_df: pd.DataFrame) -> None:
    workbook = ET.Element("workbook", {
        "original-version": "18.1", "source-build": "2026.1.0", "source-platform": "win",
        "version": "18.1", "xmlns:user": "http://www.tableausoftware.com/xml/user"
    })
    manifest = ET.SubElement(workbook, "document-format-change-manifest")
    ET.SubElement(manifest, "ZoneFriendlyName")
    ET.SubElement(manifest, "MarkAnimation")
    preferences = ET.SubElement(workbook, "preferences")
    ET.SubElement(preferences, "preference", {"name": "ui.encoding.shelf.height", "value": "24"})
    datasources = ET.SubElement(workbook, "datasources")
    eval_columns = [
        ("evaluation_id", "integer", "dimension", "nominal"), ("category", "string", "dimension", "nominal"),
        ("score", "real", "measure", "quantitative"), ("model_version", "string", "dimension", "nominal"),
        ("date", "date", "dimension", "ordinal"), ("score_band", "string", "dimension", "nominal"),
        ("score_bin", "integer", "dimension", "ordinal")]
    agree_columns = [
        ("evaluation_id", "integer", "dimension", "nominal"), ("category", "string", "dimension", "nominal"),
        ("judge_1_score", "real", "measure", "quantitative"), ("judge_2_score", "real", "measure", "quantitative"),
        ("score_difference", "real", "measure", "quantitative"), ("difference_bin", "integer", "dimension", "ordinal"),
        ("agreement", "integer", "measure", "quantitative"), ("date", "date", "dimension", "ordinal")]
    datasources.append(datasource_xml("evaluation.data", "Evaluation Data", "evaluation_data_clean.csv", eval_columns))
    datasources.append(datasource_xml("agreement.data", "Judge Agreement Data", "judge_agreement_data.csv", agree_columns))
    actions = ET.SubElement(workbook, "actions")
    action = ET.SubElement(actions, "action", {"caption": "Filter dashboard by selected category", "name": "[Action1_9a5e7c4b2d1f403a8b6c5d4e3f2a1098]"})
    ET.SubElement(action, "activation", {"auto-clear": "true", "type": "on-select"})
    ET.SubElement(action, "source", {"dashboard": "Model Evaluation Score Dashboard", "type": "sheet", "worksheet": "Category Performance Comparison"})
    command = ET.SubElement(action, "command", {"command": "tsc:tsl-filter"})
    ET.SubElement(command, "param", {"name": "exclude", "value": "Category Performance Comparison"})
    ET.SubElement(command, "param", {"name": "special-fields", "value": "all"})
    ET.SubElement(command, "param", {"name": "target", "value": "Model Evaluation Score Dashboard"})

    worksheets = ET.SubElement(workbook, "worksheets")
    base_fields = [("evaluation_id", "integer", "dimension", "nominal"), ("category", "string", "dimension", "nominal"), ("score", "real", "measure", "quantitative"), ("model_version", "string", "dimension", "nominal"), ("date", "date", "dimension", "ordinal"), ("score_bin", "integer", "dimension", "ordinal")]
    worksheets.append(worksheet_xml("Score Distribution", "evaluation.data", "Evaluation Data", "[evaluation.data].[cnt:evaluation_id:qk]", "[evaluation.data].[none:score_bin:nk]", "Automatic", base_fields, ["model_version", "category", "date"]))
    worksheets.append(worksheet_xml("Scores by Category", "evaluation.data", "Evaluation Data", "[evaluation.data].[avg:score:qk]", "[evaluation.data].[none:category:nk]", "Circle", base_fields, ["model_version", "category", "date"]))
    worksheets.append(worksheet_xml("Category Performance Comparison", "evaluation.data", "Evaluation Data", "[evaluation.data].[none:category:nk]", "[evaluation.data].[avg:score:qk]", "Bar", base_fields, ["model_version", "category", "date"]))
    worksheets.append(worksheet_xml("Score Trend", "evaluation.data", "Evaluation Data", "[evaluation.data].[avg:score:qk]", "[evaluation.data].[none:date:nk]", "Line", base_fields, ["model_version", "category", "date"]))
    agreement_fields = [("evaluation_id", "integer", "dimension", "nominal"), ("category", "string", "dimension", "nominal"), ("judge_1_score", "real", "measure", "quantitative"), ("judge_2_score", "real", "measure", "quantitative"), ("score_difference", "real", "measure", "quantitative"), ("difference_bin", "integer", "dimension", "ordinal"), ("agreement", "integer", "measure", "quantitative"), ("date", "date", "dimension", "ordinal")]
    worksheets.append(worksheet_xml("Agreement Rate by Category", "agreement.data", "Judge Agreement Data", "[agreement.data].[none:category:nk]", "[agreement.data].[avg:agreement:qk]", "Bar", agreement_fields, ["category", "date"]))
    worksheets.append(worksheet_xml("Agreement Distribution", "agreement.data", "Judge Agreement Data", "[agreement.data].[cnt:evaluation_id:qk]", "[agreement.data].[none:difference_bin:nk]", "Automatic", agreement_fields, ["category", "date"]))
    worksheets.append(worksheet_xml("Judge Comparison Scatter", "agreement.data", "Judge Agreement Data", "[agreement.data].[avg:judge_2_score:qk]", "[agreement.data].[avg:judge_1_score:qk]", "Circle", agreement_fields, ["category", "date"]))

    dashboards = ET.SubElement(workbook, "dashboards")
    dashboards.append(dashboard_xml("Model Evaluation Score Dashboard", "evaluation.data", "Evaluation Data", ["Score Distribution", "Scores by Category", "Category Performance Comparison", "Score Trend"], [("model_version", "string"), ("category", "string"), ("date", "date")], 1))
    dashboards.append(dashboard_xml("Judge Agreement Analysis Dashboard", "agreement.data", "Judge Agreement Data", ["Agreement Rate by Category", "Agreement Distribution", "Judge Comparison Scatter"], [("category", "string"), ("date", "date")], 100))
    windows = ET.SubElement(workbook, "windows", {"saved-dpi-scale-factor": "1.0", "source-height": "900"})
    for dashboard_name in ["Model Evaluation Score Dashboard", "Judge Agreement Analysis Dashboard"]:
        window = ET.SubElement(windows, "window", {"class": "dashboard", "maximized": "true", "name": dashboard_name})
        ET.SubElement(window, "active", {"id": "1" if dashboard_name.startswith("Model") else "100"})
        ET.SubElement(window, "simple-id", {"uuid": stable_uuid(f"window:{dashboard_name}")})
    ET.indent(workbook, space="  ")
    tree = ET.ElementTree(workbook)
    twb_path = ROOT / "evaluation_score_dashboard.twb"
    tree.write(twb_path, encoding="utf-8", xml_declaration=True)

    # Tableau packaged workbooks are ZIP archives that preserve the .twb and Data files.
    with zipfile.ZipFile(ROOT / "evaluation_score_dashboard.twbx", "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(twb_path, arcname="evaluation_score_dashboard.twb")
        zf.write(DATA_DIR / "evaluation_data_clean.csv", arcname="data/evaluation_data_clean.csv")
        zf.write(DATA_DIR / "judge_agreement_data.csv", arcname="data/judge_agreement_data.csv")
    shutil.copy2(twb_path, ROOT / "judge_agreement_dashboard.twb")
    with zipfile.ZipFile(ROOT / "judge_agreement_dashboard.twbx", "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(ROOT / "judge_agreement_dashboard.twb", arcname="judge_agreement_dashboard.twb")
        zf.write(DATA_DIR / "judge_agreement_data.csv", arcname="data/judge_agreement_data.csv")


def write_validation_summary(eval_df: pd.DataFrame, agreement_df: pd.DataFrame) -> None:
    summary = {
        "evaluation_rows": int(len(eval_df)),
        "agreement_rows": int(len(agreement_df)),
        "evaluation_missing_critical": int(eval_df[["evaluation_id", "category", "score", "model_version", "date"]].isna().sum().sum()),
        "agreement_missing_critical": int(agreement_df[["evaluation_id", "category", "judge_1_score", "judge_2_score", "agreement", "date"]].isna().sum().sum()),
        "score_min": round(float(eval_df["score"].min()), 2),
        "score_max": round(float(eval_df["score"].max()), 2),
        "overall_average": round(float(eval_df["score"].mean()), 2),
        "overall_agreement_rate": round(float(agreement_df["agreement"].mean()), 4),
        "date_min": str(eval_df["date"].min()),
        "date_max": str(eval_df["date"].max()),
        "categories": sorted(eval_df["category"].unique().tolist()),
        "models": sorted(eval_df["model_version"].unique().tolist()),
    }
    (ROOT / "validation_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-evaluation-dashboard")
    eval_df = generate_evaluation_data()
    agreement_df = generate_agreement_data(eval_df)
    write_data(eval_df, agreement_df)
    create_main_screenshot(eval_df)
    create_agreement_screenshot(agreement_df)
    create_interactive_html(eval_df, agreement_df)
    build_tableau_workbook(eval_df, agreement_df)
    write_validation_summary(eval_df, agreement_df)
    print(f"Generated {len(eval_df):,} evaluation rows and {len(agreement_df):,} agreement rows.")


if __name__ == "__main__":
    main()

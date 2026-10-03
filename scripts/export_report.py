"""Generate standalone scientific plots from saved results, never fresh inference."""
import json
import shutil
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from meaningci_code.dataset import ROOT

def export(directory):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    directory=Path(directory)
    out=ROOT/'reports'
    out.mkdir(exist_ok=True)
    shutil.copy2(directory/'report.md',out/'benchmark_report.md')
    summary=json.loads((directory/'summary.json').read_text())
    selected=['ci-tests-full','tests-budget-3','jev-direct','ast-change','meaningci-jsd','meaningci-label','text-change']
    data=summary['splits']['test']
    selected=[m for m in selected if m in data]
    labels={'ci-tests-full':'CI execution: full','tests-budget-3':'Execution: 3 inputs','jev-direct':'Jev: direct question','ast-change':'AST change','meaningci-jsd':'MeaningCI: distributions','meaningci-label':'MeaningCI: label flips','text-change':'Any text change'}
    fig,ax=plt.subplots(figsize=(9,4.6))
    colors=['#176b56' if 'tests' in m else '#243b76' if m=='jev-direct' else '#b34c40' if m.startswith('meaningci') else '#737b85' for m in selected]
    ax.barh(range(len(selected)),[100*data[m]['accuracy'] for m in selected],color=colors)
    ax.set_yticks(range(len(selected)),[labels[m] for m in selected]);ax.invert_yaxis();ax.set_xlim(0,116)
    for i,m in enumerate(selected):ax.text(100*data[m]['accuracy']+1,i,'%d/24' % data[m]['correct'],va='center')
    ax.set_xlabel('Conservative accuracy (%) — abstentions count as incorrect')
    ax.set_title('QuixBugs held-out: 8 defects + 16 controls (8 program clusters)')
    ax.spines[['top','right']].set_visible(False)
    fig.tight_layout();fig.savefig(out/'heldout_accuracy.svg');plt.close(fig)
    comparisons=summary['paired_test']
    fig,ax=plt.subplots(figsize=(9,4))
    for i,c in enumerate(comparisons):
        low,high=c['cluster_bootstrap_95_ci'];point=c['accuracy_difference']
        ax.errorbar(100*point,i,xerr=[[100*(point-low)],[100*(high-point)]],fmt='o',color='#b34c40',capsize=4)
    ax.axvline(0,color='#737b85',linestyle='--');ax.set_yticks(range(len(comparisons)),['vs '+c['b'] for c in comparisons]);ax.invert_yaxis()
    ax.set_xlabel('MeaningCI JSD accuracy difference (percentage points)')
    ax.set_title('95% program-cluster bootstrap intervals (5,000 resamples)')
    ax.spines[['top','right']].set_visible(False);fig.tight_layout();fig.savefig(out/'paired_intervals.svg');plt.close(fig)
    with (out/'benchmark_report.md').open('a',encoding='utf-8') as file:
        file.write('\n## Figures\n\n![Held-out accuracy](heldout_accuracy.svg)\n\n![Paired cluster intervals](paired_intervals.svg)\n')
    print('Exported report and figures:',out)

if __name__=='__main__':export(sys.argv[1] if len(sys.argv)>1 else ROOT/'runs/main')


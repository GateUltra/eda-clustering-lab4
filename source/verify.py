"""Independent partition oracle plus Python/JavaScript trace comparison."""
import itertools,json,random,subprocess
from pathlib import Path
from reference import solve,metrics
ROOT=Path(__file__).resolve().parents[1]
graphs=json.loads((ROOT/'source/graphs.json').read_text())
def partitions(nodes):
    if not nodes:yield [];return
    first,*rest=nodes
    for p in partitions(rest):
        yield [[first]]+p
        for i in range(len(p)):yield p[:i]+[[first]+p[i]]+p[i+1:]
def oracle(g,k,cap):
    ps=[metrics(g,p,k,cap) for p in partitions(g['nodes']) if len(p)==k]
    ps=[p for p in ps if p['capacity_compliant']]
    return min((p['cutsize'] for p in ps),default=None)
cases=[];goldens=[]
for k,c,groups,cut,reached in [(2,2,[['A','B'],['C'],['D','E']],8,False),(2,3,[['A','B','C'],['D','E']],3,True),(2,None,[['A','B','C'],['D','E']],3,True),(3,2,[['A','B'],['C'],['D','E']],8,True)]:
    r=solve(graphs['original'],k,c);assert (r['clusters'],r['cutsize'],r['target_reached'])==(groups,cut,reached)
    assert r['steps'][0]['cutsize']==18
    assert r['steps'][1]['candidates'][0]['affinity']==5
    cases.append([graphs['original'],k,c]);goldens.append(dict(case='original',result=r))
assert oracle(graphs['original'],2,2) is None
trap=solve(graphs['greedy_trap'],2,3);assert trap['actual_count']==3 and oracle(graphs['greedy_trap'],2,3)==10
sub=solve(graphs['suboptimal'],2,2);assert sub['cutsize']==18 and oracle(graphs['suboptimal'],2,2)==11
for name,c in [('greedy_trap',3),('suboptimal',2)]:
    cases.append([graphs[name],2,c]);goldens.append(dict(case=name,result=solve(graphs[name],2,c),optimal_cutsize_at_k=oracle(graphs[name],2,c)))
# Zero affinity must not be forced; a lower-ranked legal pair must not be skipped.
cases.append([dict(nodes=['A','B'],sizes={'A':1,'B':1},edges=[['A','B',0]]),1,2])
assert not solve(*cases[-1])['target_reached']
random.seed(4)
for _ in range(40):
    ns=list('ABCDE');g=dict(nodes=ns,sizes={n:random.choice([1,2]) for n in ns},edges=[[u,v,random.randrange(6)] for u,v in itertools.combinations(ns,2)])
    cases.append([g,random.choice([2,3]),random.choice([2,3,4,None])])
py=[solve(*c) for c in cases]
for r in py:
    assert r['capacity_compliant']
    for prev,cur in zip(r['steps'],r['steps'][1:]):assert prev['cutsize']-cur['cutsize']==cur['merge']['affinity']
    if not r['target_reached']:assert not any(c['legal'] for c in r['steps'][-1]['candidates'])
js=json.loads(subprocess.check_output(['node','-e',"const fs=require('fs'),e=require('./assets/engine.js');process.stdout.write(JSON.stringify(JSON.parse(fs.readFileSync(0,'utf8')).map(x=>e.solve(...x))));"],input=json.dumps(cases).encode(),cwd=ROOT))
assert js==py,'Python / JS trace mismatch'
(ROOT/'source/goldens.json').write_text(json.dumps(goldens,indent=2))
(ROOT/'qa/algorithm-verification.json').write_text(json.dumps(dict(passed=True,python_js_cases=len(cases),oracle='exhaustive set partitions',counterexamples=dict(infeasible_target=True,feasible_greedy_trap=True,suboptimal_greedy=True)),indent=2))
print('PASS:',len(cases),'Python/JS trace comparisons, four required settings, three independent partition-oracle checks')

"""New Lab 4 reference implementation. Standard library only, Python 3.10+.

Domain: nonempty undirected graphs, unique ASCII alphanumeric labels starting
with a letter, finite nonnegative edge weights, finite positive node sizes.
Parallel edges add; self-loops are rejected. Capacity=None means unbounded.
Tie-break: lexicographic pair of sorted member tuples, after affinity descending.
All capacity comparisons are exact floating-point <= (no hidden tolerance).
"""
import argparse, itertools, json, math, re
from pathlib import Path

def validate(g,k,capacity):
    nodes=g['nodes'];sizes=g['sizes']
    if not nodes or len(set(nodes))!=len(nodes):raise ValueError('Nodes must be nonempty and unique')
    if any(not isinstance(n,str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*',n) for n in nodes):raise ValueError('Use ASCII node labels')
    if isinstance(k,bool) or not isinstance(k,int) or not 1<=k<=len(nodes):raise ValueError('K must be an integer from 1 to node count')
    if capacity is not None and (not math.isfinite(capacity) or capacity<=0):raise ValueError('Capacity must be positive or None')
    for n in nodes:
        if not math.isfinite(sizes[n]) or sizes[n]<=0:raise ValueError('Sizes must be positive and finite')
        if capacity is not None and sizes[n]>capacity:raise ValueError('A singleton already exceeds capacity')
    for u,v,w in g['edges']:
        if u not in nodes or v not in nodes or u==v or not math.isfinite(w) or w<0:raise ValueError('Invalid edge')

def affinity(g,x,y):
    return sum(w for u,v,w in g['edges'] if (u in x and v in y) or (u in y and v in x))

def metrics(g,groups,k,capacity):
    owner={n:i for i,c in enumerate(groups) for n in c}
    sizes=[sum(g['sizes'][n] for n in c) for c in groups]
    return dict(clusters=[list(c) for c in groups],actual_count=len(groups),
                cutsize=sum(w for u,v,w in g['edges'] if owner[u]!=owner[v]),
                sizes=sizes,capacity_compliant=capacity is None or all(s<=capacity for s in sizes),
                target_reached=len(groups)==k)

def candidates(g,groups,capacity):
    out=[]
    for x,y in itertools.combinations(sorted(groups),2):
        a=affinity(g,x,y);size=sum(g['sizes'][n] for n in x+y)
        if a>0:out.append(dict(left=list(x),right=list(y),affinity=a,size=size,legal=capacity is None or size<=capacity))
    return sorted(out,key=lambda c:(-c['affinity'],tuple(c['left']),tuple(c['right'])))

def solve(g,k=2,capacity=2):
    validate(g,k,capacity)
    groups=[(n,) for n in sorted(g['nodes'])]
    steps=[dict(**metrics(g,groups,k,capacity),candidates=candidates(g,groups,capacity),merge=None)]
    while len(groups)>k:
        picked=next((c for c in candidates(g,groups,capacity) if c['legal']),None)
        if picked is None:break
        x=tuple(picked['left']);y=tuple(picked['right'])
        groups=sorted([c for c in groups if c!=x and c!=y]+[tuple(sorted(x+y))])
        steps.append(dict(**metrics(g,groups,k,capacity),candidates=candidates(g,groups,capacity),merge=picked))
    result=metrics(g,groups,k,capacity)
    return dict(**result,target_k=k,capacity=capacity,
                stop_reason='target_reached' if result['target_reached'] else 'no_legal_positive_merge',steps=steps)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('graph',nargs='?',default=str(Path(__file__).parent/'graphs.json'));p.add_argument('--case',default='original');p.add_argument('--k',type=int,default=2);p.add_argument('--capacity',default='2');a=p.parse_args()
    data=json.loads(Path(a.graph).read_text());g=data[a.case] if 'nodes' not in data else data
    print(json.dumps(solve(g,a.k,None if a.capacity.lower()=='none' else float(a.capacity)),indent=2))

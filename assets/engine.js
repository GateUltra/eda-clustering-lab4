/* New implementation; canonical tie-break is sorted member tuples, not synthetic IDs. */
(function(root){
'use strict';
function cmp(a,b){return a<b?-1:a>b?1:0;}
function tuple(a,b){for(let i=0;i<Math.min(a.length,b.length);i++){let c=cmp(a[i],b[i]);if(c)return c;}return a.length-b.length;}
function validate(g,k,capacity){
 const ns=g.nodes;if(!ns.length||new Set(ns).size!==ns.length)throw Error('Nodes must be nonempty and unique');
 if(ns.some(n=>typeof n!=='string'||!/^[A-Za-z][A-Za-z0-9_-]*$/.test(n)))throw Error('Use ASCII node labels');
 if(!Number.isInteger(k)||k<1||k>ns.length)throw Error('K must be an integer from 1 to node count');
 if(capacity!==null&&(!Number.isFinite(capacity)||capacity<=0))throw Error('Capacity must be positive or null');
 for(const n of ns){if(!Number.isFinite(g.sizes[n])||g.sizes[n]<=0)throw Error('Sizes must be positive and finite');if(capacity!==null&&g.sizes[n]>capacity)throw Error('A singleton already exceeds capacity');}
 for(const [u,v,w] of g.edges)if(!ns.includes(u)||!ns.includes(v)||u===v||!Number.isFinite(w)||w<0)throw Error('Invalid edge');
}
function affinity(g,x,y){return g.edges.reduce((a,[u,v,w])=>a+((x.includes(u)&&y.includes(v)||x.includes(v)&&y.includes(u))?w:0),0);}
function metrics(g,groups,k,capacity){const owner=Object.fromEntries(groups.flatMap((c,i)=>c.map(n=>[n,i])));const sizes=groups.map(c=>c.reduce((s,n)=>s+g.sizes[n],0));return {clusters:groups.map(c=>[...c]),actual_count:groups.length,cutsize:g.edges.reduce((s,[u,v,w])=>s+(owner[u]!==owner[v]?w:0),0),sizes,capacity_compliant:capacity===null||sizes.every(s=>s<=capacity),target_reached:groups.length===k};}
function candidates(g,groups,capacity){const out=[];groups=[...groups].sort(tuple);for(let i=0;i<groups.length;i++)for(let j=i+1;j<groups.length;j++){const left=groups[i],right=groups[j];const a=affinity(g,left,right),size=[...left,...right].reduce((s,n)=>s+g.sizes[n],0);if(a>0)out.push({left:[...left],right:[...right],affinity:a,size,legal:capacity===null||size<=capacity});}return out.sort((a,b)=>b.affinity-a.affinity||tuple(a.left,b.left)||tuple(a.right,b.right));}
function solve(g,k=2,capacity=2){validate(g,k,capacity);let groups=[...g.nodes].sort(cmp).map(n=>[n]);const steps=[{...metrics(g,groups,k,capacity),candidates:candidates(g,groups,capacity),merge:null}];while(groups.length>k){const picked=candidates(g,groups,capacity).find(c=>c.legal);if(!picked)break;groups=groups.filter(c=>tuple(c,picked.left)!==0&&tuple(c,picked.right)!==0).concat([[...picked.left,...picked.right].sort(cmp)]).sort(tuple);steps.push({...metrics(g,groups,k,capacity),candidates:candidates(g,groups,capacity),merge:picked});}const result=metrics(g,groups,k,capacity);return {...result,target_k:k,capacity,stop_reason:result.target_reached?'target_reached':'no_legal_positive_merge',steps};}
const api={solve,affinity,candidates,metrics};if(typeof module!=='undefined')module.exports=api;root.Clustering=api;
})(typeof window!=='undefined'?window:globalThis);

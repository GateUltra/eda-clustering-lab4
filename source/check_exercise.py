import argparse, importlib.util, json
from pathlib import Path
from reference import solve as reference
root=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--impl',default=str(root/'source/exercise.py'));a=ap.parse_args()
spec=importlib.util.spec_from_file_location('student',a.impl);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
graphs=json.loads((root/'source/graphs.json').read_text())
cases=[('original',2,2),('original',2,3),('original',2,None),('original',3,2),('greedy_trap',2,3),('suboptimal',2,2)]
for name,k,cap in cases:
    expected=reference(graphs[name],k,cap);actual=m.solve(graphs[name],k,cap)
    for field in ['clusters','actual_count','cutsize','sizes','capacity_compliant','target_reached']:
        assert actual[field]==expected[field],f'{name}, K={k}, cap={cap}, {field}: {actual[field]} != {expected[field]}'
    print('PASS',name,'K',k,'capacity',cap)

"""Editable lesson authoring source. Run from any working directory."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
slides=[]
def slide(title, subtitle, kind, points, cues, **extra):
    slides.append(dict(id=len(slides)+1,title=title,subtitle=subtitle,kind=kind,points=points,
                       cues=[dict(en=en,zh=zh) for en,zh in cues],**extra))

slide('Size-constrained\nagglomerative clustering','CLUSTERING FOR EDA / LAB 4','cover',
      ['Strong connections guide merges.','Capacity decides which merges are legal.'],[
('How can we group connected cells without making any cluster too large?','如何把连接紧密的电路单元分组，同时避免任何簇过大？'),
('This lesson explains size-constrained agglomerative clustering through one small graph.','本课通过一个小图，讲解带大小约束的凝聚式聚类。'),
('We will follow merges, measure cutsize, and explain why the algorithm can stop early.','我们将跟踪合并过程、计算割边权重总和，并解释算法为何有时提前停止。'),
('By the end, you should be able to reproduce the result and report its limitations.','学完后，你应能复现结果，并说明它的局限。')])

slide('The EDA graph model','CELLS, CONNECTIVITY AND AREA','graph',[
 'Node → cell', 'Edge weight → connectivity', 'Node size → area', 'Example: every node has size 1'],[
('In this simplified E D A model, each node represents a cell.','在这个简化的电子设计自动化模型中，每个节点代表一个电路单元。'),
('An edge weight describes connectivity: a larger weight means a stronger connection.','边权表示连接强度：权重越大，连接越强。'),
('A node also has a size, which can represent cell area rather than node count.','节点还有大小属性，可以代表单元面积，而不只是节点个数。'),
('Here every node has size one, so cluster size equals its number of members.','这里每个节点的大小都是一，因此簇大小等于成员个数。'),
('Real netlists may use hypergraphs; this lab deliberately uses an undirected weighted graph.','真实网表可能使用超图；本实验特意采用无向加权图。')], groups=['A','B','C','D','E'])

slide('Target K and capacity','A GOAL AND A HARD CONSTRAINT','definitions',[
 'target K = desired number of clusters', 'capacity = maximum total size per cluster',
 'A legal merge must satisfy size(X) + size(Y) ≤ capacity', 'K is a target, not a guarantee'],[
('Target K is the desired number of clusters at the end.','目标 K 表示最终期望得到的簇数。'),
('Capacity is a hard upper limit on the total size inside each cluster.','容量是每个簇内总大小不可超过的上限。'),
('With capacity two, two unit-size cells fit together, but a third cell does not.','容量为二时，两个大小为一的单元可以合并，但不能再加入第三个。'),
('A small cutsize does not make an oversized cluster legal.','割边权重总和较小，并不能让超容量的簇变得合法。'),
('We must report whether the algorithm actually reaches K while respecting capacity.','我们必须报告算法在遵守容量约束的同时，是否真的达到目标 K。')])

slide('Affinity and cutsize','TWO DIFFERENT SUMS','graph',[
 'affinity(X, Y): sum of edges between X and Y',
 'cutsize: sum of all cross-cluster edge weights',
 'A merge with affinity w reduces cutsize by w'],[
('Affinity measures how strongly two current clusters are connected.','亲和度衡量当前两个簇之间的连接强度。'),
('Add every original edge weight that connects one cluster to the other.','将连接这两个簇的所有原始边权相加。'),
('Cutsize adds all edges whose endpoints belong to different clusters, counting each edge once.','割边权重总和统计端点位于不同簇的全部边，每条边只计一次。'),
('When two clusters merge, their connecting edges become internal.','两个簇合并后，它们之间的边就变成簇内边。'),
('So cutsize falls by exactly their affinity; no other partition boundary changes.','因此割边权重总和恰好减少两簇的亲和度，其他分组边界不变。')],groups=['AB','C','DE'],highlight=['AC','BC'], metric='affinity(AB, C) = 1 + 4 = 5')

slide('The deterministic greedy rule','REPEAT UNTIL K OR NO LEGAL POSITIVE MERGE','rules',[
 '1. Start with singleton clusters.', '2. Rank legal positive-affinity pairs by descending affinity.',
 '3. Break ties by sorted member labels, then merge.', '4. Update sizes and affinities after contraction.',
 'Tie key: (sorted members of X, sorted members of Y)'],[
('Start with one cluster per node, then consider pairs with positive affinity.','从每个节点各自成簇开始，只考虑亲和度为正的簇对。'),
('Discard pairs that would exceed capacity, and choose the strongest remaining pair.','排除合并后超容量的簇对，再选择剩余候选中亲和度最高的。'),
('For ties, sort the members within each cluster, then order the two clusters lexicographically.','出现平局时，先对每个簇的成员标签排序，再按字典序排列簇对。'),
('Compare the first member list, then the second; the smallest pair wins.','先比较第一个成员列表，再比较第二个，字典序最小的簇对优先。'),
('Our slides and code share this rule; upstream instead uses synthetic cluster identifiers.','本课幻灯片与两种实现统一使用这条规则；上游则使用生成的簇编号。')])

slide('Start with five singleton clusters','STEP 0 → STEP 1','graph',[
 'Initial cutsize = 5 + 1 + 4 + 2 + 1 + 5 = 18',
 'AB and DE tie at affinity 5', 'Tie-break chooses A + B', 'After AB: size 2, cutsize 13'],[
('Initially, all five nodes are separate, so every edge crosses a cluster boundary.','初始时五个节点各自成簇，因此每条边都跨越簇边界。'),
('The six edge weights add to eighteen, which is our initial cutsize.','六条边的权重之和为十八，这就是初始割边权重总和。'),
('Nodes A and B, and nodes D and E, each have affinity five.','A 与 B、D 与 E 的亲和度都是五。'),
('Our tie-break first merges nodes A and B, with combined size two.','按照平局规则，先合并 A 与 B，合并后的大小为二。'),
('Their edge becomes internal, reducing cutsize from eighteen to thirteen.','它们之间的边变为簇内边，使割边权重总和从十八降到十三。')],groups=['A','B','C','D','E'],highlight=['AB'],metric='18 − 5 = 13')

slide('Contraction updates affinity','AFTER MERGING A + B','contract',[
 'AB has size 2', 'affinity(AB, C) = AC + BC = 1 + 4 = 5',
 'DE still has affinity 5', 'The internal AB edge is no longer a candidate'],[
('Contraction replaces A and B by one current cluster while retaining both original members.','收缩操作将 A 和 B 替换为一个当前簇，同时保留两个原始成员。'),
('The new connection to C combines the old A to C and B to C edges.','新簇与 C 的连接需要合并原来的 A 到 C、B 到 C 两条边。'),
('Their weights are one and four, giving affinity five.','两条边的权重分别为一和四，因此亲和度为五。'),
('Do not keep only the largest edge, and do not reuse a stale candidate ranking.','不能只保留最大的那条边，也不能继续使用过时的候选排序。'),
('The next choice must use these updated affinities and the updated cluster sizes.','下一次选择必须使用更新后的亲和度与簇大小。')],metric='1 + 4 = 5')

slide('Capacity 2 blocks AB + C','K = 2 / CAPACITY = 2','graph',[
 'AB + C: affinity 5, size 3 → illegal', 'D + E: affinity 5, size 2 → legal',
 'Merge D + E; cutsize becomes 8', 'Partition: {A, B}   {C}   {D, E}'],[
('Now set target K to two and capacity to two.','现在将目标 K 设为二，容量也设为二。'),
('Although the A B cluster connects strongly to C, combining them would create size three.','虽然 A、B 所在簇与 C 的连接很强，合并后大小却会达到三。'),
('That merge is illegal, so we skip it and consider the next candidate.','这次合并不合法，因此跳过它，继续检查下一个候选。'),
('D and E can merge legally, reducing cutsize by another five to eight.','D 与 E 可以合法合并，割边权重总和再减少五，变为八。'),
('Nodes A and B form one cluster, C remains alone, and nodes D and E form another.','A 与 B 组成一簇，C 单独成簇，D 与 E 组成另一簇。')],groups=['AB','C','DE'],highlight=['AC','BC','CD','CE'],metric='cutsize = 1 + 4 + 2 + 1 = 8')

slide('Stopping early can be unavoidable','LEGAL RESULT / TARGET NOT REACHED','infeasible',[
 'Actual cluster count: 3', 'All cluster sizes: 2, 1, 2 ≤ capacity 2',
 'No legal positive-affinity pair remains', 'Five units cannot fit into two clusters of capacity two'],[
('We now have three clusters, and none of the remaining positive-affinity merges is legal.','现在有三个簇，剩余亲和度为正的合并都不合法。'),
('The algorithm stops even though target K is two.','虽然目标 K 为二，算法仍必须停止。'),
('This target is fundamentally infeasible: two clusters of capacity two hold only four units.','这个目标本身不可行：两个容量为二的簇最多容纳四个大小单位。'),
('Our graph contains five units, so no algorithm can satisfy both requirements.','图中共有五个大小单位，因此任何算法都无法同时满足这两个要求。'),
('The result respects capacity, but target reached must be reported as false.','结果符合容量约束，但“是否达到目标”必须报告为否。')])

slide('Capacity 3 allows ABC','K = 2 / CAPACITY = 3','graph',[
 'A + B → AB, affinity 5', 'AB + C → ABC, affinity 5 (tie-break before DE)',
 'D + E → DE, affinity 5', 'ABC and DE: sizes 3 and 2; cutsize 3'],[
('Restart from singletons, keeping target K at two but increasing capacity to three.','重新从单节点簇开始，保持目标 K 为二，把容量提高到三。'),
('After merging nodes A and B, their cluster can now legally absorb node C.','合并 A 与 B 后，它们所在的簇现在可以合法吸收 C。'),
('This ties with D and E, but our rule first merges the A B cluster with C.','它的亲和度与 D、E 簇对相同，成员标签规则优先选择前者。'),
('Then D and E merge, leaving two clusters: A with B and C, and D with E.','随后合并 D 与 E，最终得到 A、B、C 一簇和 D、E 一簇。'),
('Only the C to D and C to E edges cross, so cutsize is three.','只有 C 到 D、C 到 E 两条边跨簇，因此割边权重总和为三。')],groups=['ABC','DE'],highlight=['CD','CE'],metric='cutsize = 2 + 1 = 3')

slide('Four settings, two partitions','THE REQUIRED COMPARISON','comparison',[
 'The difference is AC + BC = 1 + 4 = 5',
 'Capacity 2 keeps C separate from AB', 'With K = 3, the same three-cluster partition reaches the target'],[
('Without a capacity limit, target K of two produces the same partition and cutsize three.','没有容量限制时，目标 K 为二仍得到相同分组，割边权重总和为三。'),
('With capacity two, the result has three clusters and cutsize eight.','容量为二时，结果有三个簇，割边权重总和为八。'),
('The difference of five comes exactly from A to C and B to C becoming cross-cluster edges.','多出的五，恰好来自 A 到 C 和 B 到 C 两条边变成跨簇边。'),
('If target K is three instead, that same capacity-two result successfully reaches the target.','如果目标 K 改为三，那么同一个容量为二的结果就成功达到目标。')])

slide('A reproducible implementation','THE SAME RULE IN PYTHON AND THE BROWSER','code',[
 'Recompute affinity from original edges and current membership.',
 'Check capacity before contraction.', 'Stop only after checking all candidates.',
 'Report count, cutsize, sizes, capacity compliance and target reached.'],[
('For a small teaching graph, recomputing affinities from original edges is a clear implementation.','对于教学小图，从原始边重新计算亲和度是一种清晰的实现方式。'),
('After each merge, update membership and sizes, then rebuild the candidate list.','每次合并后，更新成员关系和大小，再重建候选列表。'),
('One blocked candidate does not justify stopping; another legal pair may still exist.','一个候选被容量阻止，并不意味着可以停止；可能还有其他合法簇对。'),
('Stop at K, or when every positive-affinity candidate is illegal.','达到 K 时停止，或者在所有正亲和度候选都不合法时停止。'),
('Our reference rejects invalid sizes and never forces a zero-affinity merge just to reach K.','参考实现拒绝无效大小，也不会为了凑够 K 而强行合并零亲和度簇对。')])

slide('A feasible target can defeat greedy','COUNTEREXAMPLE / CAPACITY = 3 / K = 2','trap',[
 'Sizes: A = 2, B = 2, C = 1, D = 1', 'Edges: CD = 10, AC = 4, BD = 4',
 'Greedy: {A} {B} {C, D} → stuck (sizes 2, 2, 2)',
 'Feasible alternative: {A, C} {B, D} (sizes 3, 3)'],[
('Now consider a different graph with sizes two, two, one, and one.','现在看另一个图，四个节点大小分别为二、二、一、一。'),
('The strongest edge joins C and D, so greedy merges them first.','最强的边连接 C 与 D，因此贪心算法先合并它们。'),
('All three remaining clusters have size two, and capacity three blocks every further merge.','剩下的三个簇大小都为二，容量三使后续任何合并都不合法。'),
('Yet pairing node A with C, and node B with D, gives two legal clusters of size three.','但 A 与 C、B 与 D 分别成簇，就能得到两个大小为三的合法簇。'),
('Here the target is feasible; the greedy history, not total available capacity, causes the failure.','这里目标是可行的；失败源于贪心选择的历史，而不是总容量不足。')])

slide('A legal result may be suboptimal','COUNTEREXAMPLE / UNIT SIZES / CAPACITY = 2 / K = 2','optimal',[
 'Edges: AB = 10, AC = 9, BD = 9, CD = 1',
 'Greedy {A, B} {C, D}: internal 11, cutsize 18',
 'Alternative {A, C} {B, D}: internal 18, cutsize 11',
 'Choosing the best immediate merge does not guarantee the best partition'],[
('In this four-node example, every size is one and capacity is two.','在这个四节点例子中，每个节点大小为一，容量为二。'),
('Greedy takes the weight-ten A B edge, then the weight-one C D edge.','贪心先选择权重十的 A、B 边，再选择权重一的 C、D 边。'),
('The result reaches K legally, but its cross-cluster edges sum to eighteen.','结果合法达到 K，但跨簇边的权重总和为十八。'),
('Pairing node A with C, and node B with D, instead gives cutsize eleven.','如果改为 A 与 C、B 与 D 分别成簇，割边权重总和只有十一。'),
('This better legal partition proves that greedy does not guarantee global optimality.','这个更好的合法分组说明：贪心算法不保证全局最优。')])

slide('Your experiment and implementation','PREDICT → RUN → EXPLAIN','exercise',[
 'Run all four settings on the original graph.', 'Predict the next legal merge before stepping.',
 'Implement affinity, legality and contraction.', 'Submit the trace and a complete metric report.'],[
('In the interactive lab, predict the next merge before revealing it.','在交互实验中，先预测下一次合并，再查看结果。'),
('Run all four parameter settings and explain each stopping condition.','运行四组参数，并解释每组为什么停止。'),
('Then complete the Python exercise and compare it with the reference traces.','随后完成 Python 实现练习，并与参考轨迹比较。'),
('Report actual cluster count, cutsize, sizes, capacity compliance, and whether K was reached.','记录实际簇数、割边权重总和、各簇大小、容量是否合规，以及是否达到 K。'),
('Passing a quiz checks understanding, but does not replace implementation or maintenance.','测验通过可以检验理解，但本身不能替代实现任务或课程维护交付。')])

slide('What a correct result tells us','LAB 4 / RECAP','recap',[
 'Affinity chooses among legal merges.', 'Contraction changes the next decision.',
 'Capacity compliance and reaching K are separate outcomes.', 'Greedy is reproducible, not globally optimal.'],[
('Affinity guides the choice, while capacity determines which choices are legal.','亲和度指导选择，容量决定哪些选择合法。'),
('Contraction changes the graph, so every later decision must use updated information.','收缩会改变图，因此后续决策必须使用更新后的信息。'),
('A legal partition, reaching the target, and global optimality are three different outcomes.','始终区分分组合法、达到目标和全局最优这三件事。'),
('The five-node example comes from Yongfu Li\'s E D A learning course.','本课的五节点例子来自 Yongfu Li 的 EDA learning 课程。'),
('This lesson adds new explanations, narration, bilingual captions, and reproducible exercises.','本课新增讲解、配音、双语字幕与可复现实验。')])

(ROOT/'source/lesson.json').write_text(json.dumps(slides,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'{len(slides)} slides; {sum(len(c["en"].split()) for s in slides for c in s["cues"])} spoken words')

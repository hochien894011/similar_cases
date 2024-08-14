from collections import defaultdict

def build_graph(edges):
    graph = defaultdict(set)
    for edge in edges:
        graph[edge[0]].add(edge[1])
        graph[edge[1]].add(edge[0])
    return graph

def bron_kerbosch(R, P, X, graph, cliques):
    if not P and not X:
        cliques.append(R)
        return
    pivot = next(iter(P.union(X)))
    for v in P.difference(graph[pivot]):
        bron_kerbosch(R.union({v}), P.intersection(graph[v]), X.intersection(graph[v]), graph, cliques)
        P.remove(v)
        X.add(v)

def find_cliques(edges):
    graph = build_graph(edges)
    P = set(graph.keys())
    R = set()
    X = set()
    cliques = []
    bron_kerbosch(R, P, X, graph, cliques)
    cliques_tuples = [tuple(clique) for clique in cliques]
    return cliques_tuples


"""Deterministic maximum-weight assignment with an explicit foreign-player cap."""
from collections import deque


def assign(roles, candidates, cap, score):
    # Source -> eligibility gate -> player -> position -> sink.
    players = sorted(candidates, key=lambda pair: pair[0])
    first_player = 2
    first_slot = first_player + len(players)
    sink = first_slot + len(roles)
    graph = [[] for _ in range(sink+1)]

    def edge(start, end, capacity, cost=0):
        forward=[end,len(graph[end]),capacity,cost]
        graph[start].append(forward)
        graph[end].append([start,len(graph[start])-1,0,-cost])
        return forward

    edge(0,1,min(cap,len(roles)))
    bindings=[]
    for i,(pid,domestic) in enumerate(players,first_player):
        edge(0 if domestic else 1,i,1)
        for j,role in enumerate(roles):
            weight=score(pid,role)
            if weight is not None:
                bindings.append((j,pid,edge(i,first_slot+j,1,-weight)))
    for j in range(len(roles)):
        edge(first_slot+j,sink,1)

    # Each shortest residual path adds one selection and may reassign earlier players.
    # Unit slot edges bound the number of augmentations by the number of positions.
    for _ in roles:
        distances=[float('inf')]*len(graph)
        predecessor=[None]*len(graph)
        waiting=[False]*len(graph)
        queue=deque([0])
        distances[0]=0
        while queue:
            start=queue.popleft()
            waiting[start]=False
            for index,(end,_,capacity,cost) in enumerate(graph[start]):
                distance=distances[start]+cost
                if capacity and distance<distances[end]:
                    distances[end]=distance
                    predecessor[end]=(start,index)
                    if not waiting[end]:
                        queue.append(end)
                        waiting[end]=True
        if predecessor[sink] is None:
            break
        end=sink
        while end:
            start,index=predecessor[end]
            forward=graph[start][index]
            forward[2]-=1
            graph[end][forward[1]][2]+=1
            end=start
    return [(roles[j],pid) for j,pid,e in sorted(bindings) if e[2]==0]

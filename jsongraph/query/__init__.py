import time

from jsongraph.query.parser import QueryNode
from jsongraph.query.query import Query


def query(context, q):
    q = Query(context, None, QueryNode(None, None, q))
    t = time.time()
    result = q.query()
    return {
        'status': 'ok',
        'query': q.node.to_dict(),
        'result': result,
        'time': (time.time() - t) * 1000
    }

import time

from jsongraph.query.parser import QueryNode
from jsongraph.query.builder import QueryBuilder


def execute_query(q):
    qb = QueryBuilder(None, QueryNode(None, None, q))
    t = time.time()
    result = qb.query()
    duration = (time.time() - t) * 1000
    return {
        'status': 'ok',
        'query': qb.node.to_dict(),
        'result': result,
        'time': duration
    }

from collections import OrderedDict

from normality import normalize
# from sqlalchemy import exists, or_, func
# from sqlalchemy.orm import aliased

from jsongraph.query.util import OP_EQ, OP_LIKE, OP_IN, OP_NOT
from jsongraph.query.util import OP_SIM, OP_NIN

# TODO: split out the parts that affect graph filtering and
# results processing / reconstruction.


class QueryBuilder(object):

    def __init__(self, parent, node):
        self.parent = parent
        self.node = node
        self.results = {}

    @property
    def children(self):
        if not hasattr(self, '_children'):
            self._children = []
            for child_node in self.node.children:
                qb = QueryBuilder(self, child_node)
                self._children.append(qb)
        return self._children

    def _add_statement(self, q):
        """ Generate a linked statement that can be used in any
        part of the query. """
        stmt = aliased(Statement)
        ctx = aliased(Context)
        q = q.filter(stmt.context_id == ctx.id)
        if len(self.node.assumed):
            q = q.filter(or_(
                ctx.active == True,
                stmt.context_id.in_(self.node.assumed)
            )) # noqa
        else:
            q = q.filter(ctx.active == True) # noqa
        q = q.filter(stmt.deleted_at == None) # noqa
        return stmt, q

    def filter_value(self, q, filter_stmt):
        if self.node.op == OP_EQ:
            q = q.filter(filter_stmt._value == self.node.value)
        elif self.node.op == OP_NOT:
            q = q.filter(filter_stmt._value != self.node.value)
        elif self.node.op == OP_IN:
            q = q.filter(filter_stmt._value.in_(self.node.data))
        elif self.node.op == OP_NIN:
            q = q.filter(~filter_stmt._value.in_(self.node.data))
        elif self.node.op == OP_LIKE:
            value = '%%%s%%' % normalize(self.node.value)
            q = q.filter(filter_stmt.normalized.like(value))
        elif self.node.op == OP_SIM:
            value = normalize(self.node.value)[:254]
            field = func.left(filter_stmt.normalized, 254)

            # calculate the similarity percentage
            rel = func.greatest(max(float(len(self.node.value)), 1.0),
                                func.length(filter_stmt.normalized))
            distance = func.levenshtein(field, value)
            score = ((rel - distance) / rel) * 100.0
            q = q.filter(score > 1)
            score = func.max(score).label('score')

            q = q.add_column(score)
            q = q.order_by(score.desc())
        return q

    def filter_subject(self, q, subject):
        if self.node.op == OP_EQ:
            q = q.filter(subject == self.node.value)
        elif self.node.op == OP_NOT:
            q = q.filter(subject != self.node.value)
        elif self.node.op == OP_IN:
            q = q.filter(subject.in_(self.node.data))
        elif self.node.op == OP_NIN:
            q = q.filter(~subject.in_(self.node.data))
        return q

    def filter(self, q, subject, query_root=False):
        """ Apply filters to the given query recursively. """
        if not self.node.filtered:
            return q

        outer_q = q
        if self.node.forbidden:
            q = db.session.query()

        filter_stmt, q = self._add_statement(q)
        current_subject = subject
        next_subject = filter_stmt._value

        # Query root isn't acting like a normal non-leaf object, as it doesn't
        # join to the previous level via it's own attribute.
        if query_root:
            next_subject = filter_stmt.subject
        elif self.node.specific_attribute:
            attributes = self.node.attributes
            if len(attributes) == 1:
                q = q.filter(filter_stmt.attribute == attributes[0])
            else:
                q = q.filter(filter_stmt.attribute.in_(attributes))

        if self.node.inverted:
            next_subject, current_subject = current_subject, next_subject

        q = q.filter(current_subject == filter_stmt.subject)

        if self.node.leaf:
            # The child will be value-filtered directly.
            q = self.filter_value(q, filter_stmt)
        else:
            for child in self.children:
                if child.node.name == 'id':
                    q = child.filter_subject(q, next_subject)
                else:
                    q = child.filter(q, next_subject)

        if self.node.forbidden:
            q = outer_q.filter(~exists().where(q.whereclause))
        return q

    def filter_query(self, parents=None):
        """ An inner query that is used to apply any filters, limits
        and offset. """
        q = db.session.query()
        stmt, q = self._add_statement(q)
        q = q.add_column(stmt.subject)

        parent_col = None
        if parents is not None:
            parent_stmt, q = self._add_statement(q)
            q = q.filter(stmt.subject == parent_stmt._value)
            q = q.filter(parent_stmt.attribute.in_(self.node.attributes))
            q = q.filter(parent_stmt.subject.in_(parents))
            parent_col = parent_stmt.subject.label('parent_id')
            q = q.add_column(parent_col)

        q = self.filter(q, stmt.subject, query_root=True)
        q = q.group_by(stmt.subject)
        if parents is not None:
            q = q.group_by(parent_col)

        # TODO: implement other sorts
        if self.node.sort == 'random':
            q = q.order_by(func.random())

        q = q.order_by(stmt.subject.asc())

        if self.node.root and self.node.limit is not None:
            q = q.limit(self.node.limit)
            q = q.offset(self.node.offset)

        return q

    def nested(self):
        """ A list of all sub-entities for which separate queries will
        be conducted. """
        for child in self.children:
            if child.node.nested:
                yield child

    def project(self):
        """ Figure out which attributes should be returned for the current
        level of the query. """
        attrs = set()
        for child in self.children:
            if not child.node.nested:
                attrs.update(child.node.attributes)
        if not len(attrs):
            attrs.update(types.qualified.keys())
        return list(attrs)

    def base_object(self, data):
        """ Make sure to return all the existing filter fields
        for query results. """
        obj = {
            'id': data.get('id'),
            'parent_id': data.get('parent_id')
        }

        if 'score' in data:
            obj['score'] = data.get('score')

        for child in self.children:
            if self.node.blank:
                obj[child.node.name] = child.node.data
        return obj

    def get_node(self, name):
        """ Get the node for a given name. """
        for child in self.children:
            if child.node.name == name:
                return child.node
        return None if name == '*' else self.get_node('*')

    def data_query(self, parents=None):
        """ Generate a query for any statement which matches the criteria
        specified through the filter query. """
        q = db.session.query()
        stmt, q = self._add_statement(q)

        filter_sq = self.filter_query(parents=parents).subquery()
        q = q.filter(stmt.subject == filter_sq.c.subject)

        q = q.filter(stmt.attribute.in_(self.project()))

        q = q.add_column(stmt.subject.label('id'))
        q = q.add_column(stmt.attribute.label('attribute'))
        q = q.add_column(stmt._value.label('value'))

        if self.node.scored:
            score = filter_sq.c.score.label('score')
            q = q.add_column(score)
            q = q.order_by(score.desc())

        if parents is not None:
            q = q.add_column(filter_sq.c.parent_id.label('parent_id'))

        q = q.order_by(filter_sq.c.subject.desc())
        # q = q.order_by(stmt.created_at.asc())
        return q

    def execute(self, parents=None):
        """ Run the data query and construct entities from it's results. """
        results = OrderedDict()
        for row in self.data_query(parents=parents):
            data = row._asdict()
            id = data.get('id')
            if id not in results:
                results[id] = self.base_object(data)

            value = data.get('value')
            attr = types.qualified[data.get('attribute')]
            value = attr.type.deserialize_safe(value)

            node = self.get_node(attr.name)
            if attr.many if node is None else node.many:
                if attr.name not in results[id]:
                    results[id][attr.name] = []
                results[id][attr.name].append(value)
            else:
                results[id][attr.name] = value
        return results

    def collect(self, parents=None):
        """ Given re-constructed entities, conduct queries for child
        entities and merge them into the current level's object graph. """
        results = self.execute(parents=parents)
        ids = results.keys()
        for child in self.nested():
            attr = child.node.name
            for child_data in child.collect(parents=ids).values():
                parent_id = child_data.pop('parent_id')
                if child.node.many:
                    if attr not in results[parent_id]:
                        results[parent_id][attr] = []
                    results[parent_id][attr].append(child_data)
                else:
                    results[parent_id][attr] = child_data
        return results

    def query(self):
        results = []
        for result in self.collect().values():
            result.pop('parent_id')
            if not self.node.many:
                return result
            results.append(result)
        return results

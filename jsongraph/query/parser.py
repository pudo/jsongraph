import copy

from jsongraph.query.util import parse_name, is_list


class QueryNode(object):

    def __init__(self, parent, name, data):
        self.parent = parent
        self.data = value = copy.deepcopy(data)

        parts = parse_name(name)
        self.name, self.inverted, self._op = parts

        self.many = is_list(value)
        if self.many:
            value = None if not len(value) else value[0]

        self.optional, self.sort, self.assume = None, None, []
        if isinstance(value, dict):
            self.sort = value.pop('sort', None)
            self.optional = value.pop('optional', None)
            self.assume = value.pop('assume', [])
            self.limit = value.pop('limit', 15)
            if not self.many:
                self.limit = 1
            self.offset = value.pop('offset', 0)

        if value is not None and \
                not isinstance(value, (dict, list, tuple, set)):
            value = unicode(value)

        self.value = value

    @property
    def specific_attribute(self):
        return self.name not in ['*', 'id']

    @property
    def nested(self):
        if not self.specific_attribute:
            return False
        return isinstance(self.value, dict)

    @property
    def attributes(self):
        if self.name == '*':
            return types.qualified.keys()
        attributes = []
        for qname, attr in types.qualified.items():
            if attr.name == self.name:
                attributes.append(qname)
        return attributes

    @property
    def root(self):
        return self.parent is None

    @property
    def assumed(self):
        if self.root:
            return self.assume
        return self.parent.assumed + self.assume

    @property
    def forbidden(self):
        return self.optional == 'forbidden'

    @property
    def op(self):
        if self.leaf and not self.blank:
            return self._op

    @property
    def blank(self):
        return self.value is None

    @property
    def leaf(self):
        return not isinstance(self.value, dict)

    @property
    def filtered(self):
        if self.forbidden:
            return True
        if self.leaf:
            return self.value is not None
        # for child in self.children:
        #     if child.filtered:
        #         return True
        # return False
        return True

    @property
    def children(self):
        if self.leaf:
            return
        for name, data in self.value.items():
            yield QueryNode(self, name, data)

    def to_dict(self):
        data = {
            'name': self.name,
            'leaf': self.leaf,
            'many': self.many,
            'blank': self.blank,
            'filtered': self.filtered
        }
        if self.root:
            data['limit'] = self.limit
            data['offset'] = self.offset
            del data['name']
        if self.leaf:
            data['value'] = self.value if self.leaf else None
            data['op'] = self.op
        else:
            data['inverted'] = self.inverted
            data['optional'] = self.optional
            data['sort'] = self.sort
            data['children'] = [c.to_dict() for c in self.children]
        return data

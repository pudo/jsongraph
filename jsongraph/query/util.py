
OP_EQ = '=='
OP_IN = '|='
OP_NOT = '!='
OP_NIN = '|!='
OP_LIKE = '~='


def parse_name(name):
    """ Split a query name into field name, operator and whether it is
    inverted. """
    inverted, op = False, OP_EQ
    if name is not None:
        for op_ in (OP_NIN, OP_IN, OP_NOT, OP_LIKE):
            if name.endswith(op_):
                op = op_
                name = name[:len(name) - len(op)]
                break
        if name.startswith('!'):
            inverted = True
            name = name[1:]
    return name, inverted, op


def is_list(list_like):
    return isinstance(list_like, (list, tuple, set))

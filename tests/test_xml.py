import itertools
import random
from scipy.special import comb
from dcop_generator.dcop_instance import create_xml_instance, sanity_check


def generate(nagts, dsize, p1, p2, cost_range=(0, 10), max_arity=2, def_cost=0, int_cost=True):
    assert (0.0 < p1 <= 1.0)
    assert (0.0 <= p2 < 1.0)
    agts = {}
    vars = {}
    doms = {'0': list(range(0, dsize))}
    cons = {}

    for i in range(0, nagts):
        agts[str(i)] = None
        vars[str(i)] = {'dom': '0', 'agt': str(i)}

    ncons = int(p1 * ((nagts * (nagts - 1)) / 2))
    constraint_set = set()

    consumed_constr = 0
    cid = 0
    dset = list(range(0, dsize))

    while consumed_constr < ncons:
        arity = random.randint(*(2, max_arity))
        scope = frozenset(random.sample(range(nagts), arity))
        # Don't duplicate.
        if scope in constraint_set:
            continue

        cons[str(cid)] = {'arity': arity, 'def_cost': def_cost,
                          'scope': [str(x) for x in scope], 'values': []}

        n_C = len(dset) ** arity
        n_forbidden_assignments = int(p2 * n_C)
        forbidden_assignments = frozenset(random.sample(range(n_C), n_forbidden_assignments))
        k = 0
        for assignments in itertools.product(*([dset, ] * arity)):
            val = {'tuple': []}
            val['tuple'] = list(assignments)
            if int_cost:
                val['cost'] = random.randint(*cost_range) if k not in forbidden_assignments else None
            else:
                val['cost'] = random.uniform(*cost_range) if k not in forbidden_assignments else None
            cons[str(cid)]['values'].append(val)
            k += 1

        constraint_set.add(scope)
        consumed_constr += int(comb(arity, 2))
        cid += 1

    return agts, vars, doms, cons


if __name__ == '__main__':
    nagts = 50
    dsize = 10
    p1 = 1.0
    p2 = 0.5
    max_arity = 2
    max_cost = 100
    out_file = 'test'
    name = 'test'
    while True:
        agts, vars, doms, cons = generate(nagts=nagts, dsize=dsize, p1=p1, p2=p2,
                                          cost_range=(0, max_cost),
                                          max_arity=max_arity, def_cost=0)
        if sanity_check(vars, cons):
            break

    print('Creating DCOP instance ' + name)
    create_xml_instance(name, agts, vars, doms, cons, out_file + '.xml')

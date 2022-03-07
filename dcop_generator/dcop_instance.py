import xml.dom.minidom as md
import xml.etree.ElementTree as ET

def create_xml_instance(name, agts, vars, doms, cons, fileout=''):
    """
    Creates an XML instance
    :param name: The name of the instance
    :param agts: Dict of agents:
        key: agt_name, val = null
    :param vars: Dict of variables:
        key: var_name,
        vals: 'dom' = dom_name; 'agt' = agt_name
    :param doms: Dict of domains:
        key: dom_name,
        val: array of values (integers)
    :param cons: Dict of constraints:
        key: con_name,
        vals: 'arity' = int; 'def_cost' = int, values = list of dics {v: values, c: cost}
    """

    def prettify(elem):
        """Return a pretty-printed XML string for the Element.
        """
        # tree = ET.parse(pathToFile, OrderedXMLTreeBuilder())
        rough_string = ET.tostring(elem.getroot(), encoding='utf-8', method='xml')
        reparsed = md.parseString(rough_string)
        return reparsed.toprettyxml(indent="\t")

    def dump_rel(c_values):
        s = ''
        for i, t in enumerate(c_values):
            if t['cost'] is None:
                continue
            s += str(t['cost']) + ':'
            s += ' '.join(str(x) for x in t['tuple'])
            if i < len(c_values) - 1:
                s += ' |'
        return s

    root = ET.Element('instance')
    ET.SubElement(root, 'presentation',
                  name=name,
                  maxConstraintArity=str(max([cons[cid]['arity'] for cid in cons])),
                  maximize="true",
                  format="XCSP 2.1_FRODO")

    xml_agts = ET.SubElement(root, 'agents', nbAgents=str(len(agts)))
    for aname in agts:
        ET.SubElement(xml_agts, 'agent', name='a_' + aname)

    xml_vars = ET.SubElement(root, 'variables', nbVariables=str(len(vars)))
    for vname in vars:
        ET.SubElement(xml_vars, 'variable',
                      name='v_' + vname,
                      domain='d',  # +vars[vname]['dom'],
                      agent='a_' + vars[vname]['agt'])

    xml_doms = ET.SubElement(root, 'domains', nbDomains=str(len(doms)))
    for dname in doms:
        ET.SubElement(xml_doms, 'domain', name='d',  # +dname,
                      nbValues=str(len(doms[dname]))).text \
            = str(doms[dname][0]) + '..' + str(doms[dname][-1])
        # = ' '.join(str(x) for x in doms[dname])

    xml_rels = ET.SubElement(root, 'relations', nbRelations=str(len(cons)))
    xml_cons = ET.SubElement(root, 'constraints', nbConstraints=str(len(cons)))

    for cname in cons:
        X = [x for x in cons[cname]['values'] if x['cost'] is not None]
        # r_3_1
        r_name = 'r';
        for e in cons[cname]['scope']:
            r_name += '_' + str(e)
        ET.SubElement(xml_rels, 'relation', name=r_name, arity=str(cons[cname]['arity']),
                      nbTuples=str(len(X)),
                      semantics='soft',
                      defaultCost="0"  # str(cons[cname]['def_cost'])
                      ).text = dump_rel(cons[cname]['values'])

        ET.SubElement(xml_cons, 'constraint', name='c_' + cname, arity=str(cons[cname]['arity']),
                      scope=' '.join('v_' + str(e) for e in cons[cname]['scope']),
                      reference=r_name)

    tree = ET.ElementTree(root)
    if fileout:
        with open(fileout, "w") as f:
            f.write(prettify(tree))
    else:
        print(prettify(tree))

def sanity_check(vars, cons):
    """ Check all variables participate in some constraint """
    v_con = []
    for c in cons:
        for x in cons[c]['scope']:
            if x not in v_con:
                v_con.append(x)
    for v in vars:
        if v not in v_con:
            return False
    return True
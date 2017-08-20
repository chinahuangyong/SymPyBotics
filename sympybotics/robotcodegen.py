
import sympy

from . import symcode


def _gen_q_dq_ddq_subs(rbtdef, offset=0, brackets=['[',']']):    
    subs = {}
    for i in reversed(range(rbtdef.dof)):
        subs[rbtdef.ddq[i]] = 'ddq' + brackets[0] + str(i+offset) + brackets[1]
        subs[rbtdef.dq[i]] = 'dq' + brackets[0] + str(i+offset) + brackets[1]
        subs[rbtdef.q[i]] = 'q' + brackets[0] + str(i+offset) + brackets[1]
    return subs


def _gen_parms_subs(parms_symbols, name='parms', offset=0, brackets=['[',']']):
    subs = {}
    for i, parm in enumerate(parms_symbols):
        subs[parm] = name + brackets[0] + str(i+offset) + brackets[1]
    return subs


def robot_code_to_func(lang, code, outputname, funcname, rbtdef):
    func_parms = []
    subs_pairs = {}
    
    idxoffset = 1 if lang.lower() in ['julia', 'jl', 'matlab', 'm'] else 0
    brackets = ['(',')'] if lang.lower() in ['matlab','m'] else ['[',']']

    if not isinstance(code[1], list):
        code = (code[0], [code[1]])
    if not isinstance(outputname, list):
        outputname = [outputname]

    code_symbols = set()
    for iv, se in code[0]:
        code_symbols.update(se.free_symbols)
    for e in code[1]:
        for ei in e:
            code_symbols.update(ei.free_symbols)

    if not code_symbols.isdisjoint(set(rbtdef.dynparms())):
        func_parms.append('parms')
        subs_pairs.update(_gen_parms_subs(rbtdef.dynparms(), 'parms',
                                          offset=idxoffset, brackets=brackets))

    qderivlevel = -1
    if not code_symbols.isdisjoint(set(rbtdef.q)):
        qderivlevel = 0
    if not code_symbols.isdisjoint(set(rbtdef.dq)):
        qderivlevel = 1
    if not code_symbols.isdisjoint(set(rbtdef.ddq)):
        qderivlevel = 2

    if qderivlevel >= 0:
        for i in range(qderivlevel + 1):
            func_parms.append('d'*i + 'q')
        subs_pairs.update(_gen_q_dq_ddq_subs(rbtdef, offset=idxoffset, brackets=brackets))

    return symcode.generation.code_to_func(lang, code, outputname, funcname,
                                           func_parms, subs_pairs)

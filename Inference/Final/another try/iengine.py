import re
from utils import *
from extra import *

def tt_check_all(clauses, alpha, symbols, model):
    if not symbols:
        if all(tt_check(clause, model) for clause in clauses):
            return model.get(alpha, False),1
        else:
            return False, 0
    else:
        P, rest = symbols[0], symbols[1:]
        
        true_model = extend(model, P, True)
        false_model = extend(model, P, False)
        
        result_true, count_true = tt_check_all(clauses, alpha, rest, true_model)
        result_false, count_false = tt_check_all(clauses, alpha, rest, false_model)
        
        total_count = 0
        if result_true:
            total_count += count_true
        if result_false:
            total_count += count_false
        
        return (result_true or result_false), total_count


def tt_check(clause, model):
    if '=>' in clause:
        LHS, RHS = clause.split('=>')
        LHS = LHS.split('&')
        if isinstance(LHS, list):
            return all(model.get(symbol.strip(), False) for symbol in LHS) <= model.get(RHS.strip(), False)
        else:
            return model.get(LHS.strip(), False) <= model.get(RHS.strip(), False)
    elif '&' in clause:
        return all(tt_check(part.strip(), model) for part in clause.split('&'))
    elif '|' in clause:
        return any(tt_check(part.strip(), model) for part in clause.split('|'))
    else:
        return model.get(clause.strip(), None)


class InferenceEngine:
    def __init__(self, clauses):
        self.clauses = clauses
        self.symbols = self.get_symbols()

    def get_symbols(self):
        symbols = set()
        for clause in self.clauses:
            symbols.update(re.findall(r'\b[a-zA-Z]\w*', str(clause)))
        return list(symbols)

    def tt_entails(self, alpha):
        symbols = self.symbols
        result, count = tt_check_all(self.clauses, alpha, symbols, {s: None for s in symbols})
        return result, count


    def fc_entails(self, alpha):
        symbols_entailed = []
        agenda = []

        def entail_symbol(symbol):
            if symbol in symbols_entailed:
                return True
            for clause in self.clauses:
                if '=>' in clause:
                    LHS, RHS = clause.split('=>')
                    LHS = LHS.split('&')
                    RHS = RHS.strip()
                    if symbol == RHS:
                        if all(entail_symbol(lhs.strip()) for lhs in LHS):
                            symbols_entailed.append(RHS)
                            agenda.append(RHS)
                            return True
            return False

        for clause in self.clauses:
            if '=>' not in clause:
                if clause == alpha:
                    symbols_entailed.append(clause.strip())
                    return True, symbols_entailed
                agenda.append(clause.strip())
                symbols_entailed.append(clause.strip())

        while agenda:
            p = agenda.pop(0)
            for clause in self.clauses:
                if '=>' in clause:
                    LHS, RHS = clause.split('=>')
                    LHS = LHS.split('&')
                    RHS = RHS.strip()
                    if all(entail_symbol(lhs.strip()) for lhs in LHS):
                        if RHS not in symbols_entailed:
                            symbols_entailed.append(RHS)
                            agenda.append(RHS)
                            if RHS == alpha:
                                return True, symbols_entailed

        return alpha in symbols_entailed, symbols_entailed


    def bc_entails(self, alpha):
        symbols_entailed = []

        def entail_symbol(symbol):
            if symbol in symbols_entailed:
                return True
            if symbol in [clause.strip() for clause in self.clauses if '=>' not in clause]:
                symbols_entailed.append(symbol)
                return True
            for clause in self.clauses:
                if '=>' in clause:
                    LHS, RHS = clause.split('=>')
                    LHS = LHS.split('&')
                    RHS = RHS.strip()
                    if symbol == RHS:
                        if all(entail_symbol(lhs.strip()) for lhs in LHS):
                            symbols_entailed.append(RHS)
                            return True
            return False

        if entail_symbol(alpha):
            return True, symbols_entailed
        else:
            return False, symbols_entailed
        
    # def resolution_entails(self, kb_clauses, alpha):
    #     """
    #     [Figure 7.12]
    #     Propositional-logic resolution: say if alpha follows from KB.
    #     >>> pl_resolution(horn_clauses_KB, A)
    #     True
    #     """
    #     clauses = kb_clauses + conjuncts(to_cnf(~alpha))
    #     new = set()
    #     while True:
    #         n = len(clauses)
    #         pairs = [(clauses[i], clauses[j])
    #                 for i in range(n) for j in range(i + 1, n)]
    #         for (ci, cj) in pairs:
    #             resolvents = pl_resolve(ci, cj)
    #             if False in resolvents:
    #                 return True
    #             new = new.union(set(resolvents))
    #         if new.issubset(set(clauses)):
    #             return False
    #         for c in new:
    #             if c not in clauses:
    #                 clauses.append(c)
        
    def resolution_entails(self, alpha):
        clauses = self.clauses.copy()
        clauses.append(negate_clause(alpha))

        new = set()
        while True:
            n = len(clauses)
            pairs = [(clauses[i], clauses[j]) for i in range(n) for j in range(i + 1, n)]
            for ci, cj in pairs:
                resolvents = resolve(ci, cj)
                if '' in resolvents:
                    return True
                new = new.union(set(resolvents))

            if new.issubset(set(clauses)):
                return False

            for c in new:
                if c not in clauses:
                    clauses.append(c)

def negate_clause(clause):
    if '|' in clause:
        return ' & '.join(['~' + literal.strip() for literal in clause.split('|')])
    else:
        return '~' + clause

def resolve(ci, cj):
    clauses = []

    ci_literals = [literal.strip() for literal in ci.split('|')]
    cj_literals = [literal.strip() for literal in cj.split('|')]

    for ci_literal in ci_literals:
        for cj_literal in cj_literals:
            if ci_literal == '~' + cj_literal or '~' + ci_literal == cj_literal:
                di = remove_literal(ci_literals, ci_literal)
                dj = remove_literal(cj_literals, cj_literal)
                new_clause = unique(di + dj)
                if len(new_clause) == 0:
                    clauses.append('')
                else:
                    clauses.append(' | '.join(new_clause))

    return clauses

def remove_literal(literals, literal):
    return [l for l in literals if l != literal]

def unique(literals):
    return list(set(literals))


# def resolution_entails(kb, alpha):
#     """
#     [Figure 7.12]
#     Propositional-logic resolution: say if alpha follows from KB.
#     >>> pl_resolution(horn_clauses_KB, A)
#     True
#     """
#     clauses = kb.clauses + conjuncts(to_cnf(~alpha))
#     new = set()
#     while True:
#         n = len(clauses)
#         pairs = [(clauses[i], clauses[j])
#                  for i in range(n) for j in range(i + 1, n)]
#         for (ci, cj) in pairs:
#             resolvents = pl_resolve(ci, cj)
#             if False in resolvents:
#                 return True
#             new = new.union(set(resolvents))
#         if new.issubset(set(clauses)):
#             return False
#         for c in new:
#             if c not in clauses:
#                 clauses.append(c)


# def pl_resolve(ci, cj):
#     """Return all clauses that can be obtained by resolving clauses ci and cj."""
#     clauses = []
#     for di in disjuncts(ci):
#         for dj in disjuncts(cj):
#             if di == ~dj or ~di == dj:
#                 clauses.append(associate('|', unique(remove_all(di, disjuncts(ci)) + remove_all(dj, disjuncts(cj)))))
#     return clauses
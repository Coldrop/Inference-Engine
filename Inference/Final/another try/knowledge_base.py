from iengine import *
from extra import *
class knowledge_base:
    def __init__(self, sentence=None):
        if sentence:
            self.tell(sentence)
        self.clauses = []
        self.cnf_clauses = []

    def tell(self, sentence):
        if '||' in sentence:
            sentence = sentence.replace('||', '|')
        converted_horn_sentence = convert_to_horn_form(sentence)
        if converted_horn_sentence == None:
            return False, None
        for sentence in converted_horn_sentence:
            self.clauses.append(sentence)

    def tell_cnf(self, sentence):
        if '||' in sentence:
            sentence = sentence.replace('||', '|')
        cnf_sentence = to_cnf(sentence)
        cnf_sentence = convert_expr_to_str(cnf_sentence)
        self.cnf_clauses.append(cnf_sentence)
        
    
    def ask(self, alpha, method):
        iengine = InferenceEngine(self.clauses)
        # print(f"this is the KB: {self.clauses}")
        print(f"this is the CNF clause: {self.cnf_clauses}")
        if method == 'TT':
            return iengine.tt_entails(alpha)
        elif method == 'FC':
            return iengine.fc_entails(alpha)
        elif method == 'BC':
            return iengine.bc_entails(alpha)
        elif method == 'R':
            iengine = InferenceEngine(self.cnf_clauses)
            return iengine.resolution_entails(alpha)

    def get_clauses(self):
        return self.clauses

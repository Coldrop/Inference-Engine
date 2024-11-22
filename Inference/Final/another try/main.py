import sys
from knowledge_base import * 
from extra import *

def main():
    if len(sys.argv) != 3:
        print("Please follow the following prompt format\nC:> python main.py <filename> <method>")
        return
    filename = sys.argv[1]
    method = sys.argv[2]
    
    with open(filename, 'r') as file:
        lines = file.readlines()

        All_sentences = lines[1].strip()
        KB_sentences = All_sentences.split(';')
        alpha = lines[3].strip()
        # alpha = convert_to_horn_form(alpha)
        # print(f"this is alpha: {alpha}")
        print("TODO: \n1. change algorithms to accommodate an array for alpha\n2. Check to see if the algorithms take negative literals as a value.\n3. Implement PL Resolution\n4. Create heaps and heaps of test cases.")
        KB = knowledge_base()
        if method == 'TT':
            for sentence in KB_sentences:
                if sentence.strip():
                    KB.tell(sentence.strip())
            result, no_of_models = KB.ask(alpha, method)
            if result:
                print(f"YES: {no_of_models}")
            else:
                print("NO")
        elif method == 'FC' or method == 'BC':
            for sentence in KB_sentences:
                if sentence.strip():
                    KB.tell(sentence.strip())
            result, symbols_entailed = KB.ask(alpha, method)
            if result:
                print(f"YES: {', '.join(symbols_entailed)}")
            else:
                print("NO")
        elif method == 'R':
            for sentence in KB_sentences:
                if sentence.strip():
                    # print(f"this is a Sentence: {sentence}")
                    KB.tell_cnf(sentence.strip())
            result = KB.ask(alpha, method)
            if result:
                print("YES")
            else:
                print("NO")
        else:
            print("Please enter a valid method. I.e. either TT, FC or BC")
    
if __name__ == '__main__':
    main()
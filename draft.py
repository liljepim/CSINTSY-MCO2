from pyswip import Prolog
import difflib

prolog = Prolog()
prolog.consult("relationships.pl")

"""
List of basic relationships
Female --> female(Name)
Male --> male(Name)
Parent --> parent(Father/Mother, Child)
"""

#Clean up
prolog.retractall("parent(_,_)")
prolog.retractall("male(_)")
prolog.retractall("female(_)")

#List of Sample Characters (Initialized)

#Penny
prolog.assertz("female(penny)")
#   Children
prolog.assertz("parent(penny, alice)")
prolog.assertz("parent(penny, peter)")
prolog.assertz("parent(penny, jasmine)")

#Manny
prolog.assertz("male(manny)")
#   Children
prolog.assertz("parent(manny, alice)")
prolog.assertz("parent(manny, peter)")
prolog.assertz("parent(manny, jasmine)")

#   Alice
prolog.assertz("female(alice)")
#       Children
prolog.assertz("parent(alice, red)")

#       Hatter - Alice's Spouse
prolog.assertz("male(hatter)")
#       Children
prolog.assertz("parent(hatter, red)")

#           Red Queen
prolog.assertz("female(red)")


#   Peter
prolog.assertz("male(peter)")
#       Children
prolog.assertz("parent(peter, jane)")
prolog.assertz("parent(peter, danny)")

#       Wendy - Peter's Spouse
prolog.assertz("female(wendy)")
#       Children
prolog.assertz("parent(wendy, jane)")
prolog.assertz("parent(wendy, danny)")

#           Jane
prolog.assertz("female(jane)")
#               Children
prolog.assertz("parent(jane, dracula)")

#           Alucard - Jane's Spouse
prolog.assertz("male(alucard)")
#               Children
prolog.assertz("parent(alucard, dracula)")

#                   Dracula
prolog.assertz("male(dracula)")

#           Danny
prolog.assertz("male(danny)")


#   Jasmine
prolog.assertz("female(jasmine)")
#       Children
prolog.assertz("parent(jasmine, ella)")

#       Aladeen - Jasmine's Spouse
prolog.assertz("male(aladeen)")
#       Children
prolog.assertz("parent(aladeen, ella)")
prolog.assertz("parent(aladeen, prince)")

#         Jessica - Aladeen's Ex-Spouse
prolog.assertz("female(jessica)")
#         Children
prolog.assertz("parent(jessica, prince)")

#           Ella
prolog.assertz("female(ella)")
#               Children
prolog.assertz("parent(ella, mimi)")

#           Prince
prolog.assertz("male(prince)")
#               Children
prolog.assertz("parent(prince, mimi)")
prolog.assertz("parent(prince, momo)")
prolog.assertz("parent(prince, mama)")
prolog.assertz("parent(prince, meme)")

#           Anastasia - Prince's Current Spouse
prolog.assertz("female(anastasia)")
#               Children
prolog.assertz("parent(anastasia, momo)")
prolog.assertz("parent(anastasia, mama)")
prolog.assertz("parent(anastasia, meme)")

#                   Mimi
prolog.assertz("female(mimi)")

#                   Momo
prolog.assertz("female(momo)")

#                   Mama
prolog.assertz("female(mama)")

#                   Meme
prolog.assertz("female(meme)")



"""
#SAMPLE RUNS
prolog.assertz("parent(michael, john)")
prolog.assertz("male(michael)")
prolog.assertz("male(john)")

print(list(prolog.query("male(X)")))

father = list(prolog.query("father(X, john)"))
child = list(prolog.query("child(X, michael)"))
son = list(prolog.query("son(X, michael)"))
daughter = bool(list(prolog.query("daughter(john, michael)")))
sonT = bool(list(prolog.query("son(john, michael)")))
print("_________________________________________")
print(father)
print(child)
print(son)
print(list(prolog.query("son(john, michael)")))
print(list(prolog.query("daughter(john, michael)")))
print("_________________________________________")


print(f"The father of John is {father[0]['X']}")
print(f"The child of Michael is {child[0]['X']}")
print(f"The son of Michael is {son[0]['X']}")
print(f"The daughter of Michael: {daughter} but as son: {sonT}")

#print(list(Prolog.query("father(X, john)")))
#print(bool(list(Prolog.query("father(michael, john)"))))

res = list(prolog.query("male(alice)"))
print("Is Alice male?", res)

print("LIST OF FEMALE:")
print(list(prolog.query("female(X)")))
print("\nLIST OF MALE:")
print(list(prolog.query("male(X)")))
print()
"""


def yesNoChatbot(answer: bool):
    if answer:
        print("Chatbot: Yes\n")
    else:
        print("Chatbot: No\n")

def chatbotReply(children: list, answer: bool):
    if answer and children:
        print("Chatbot: Yes\n")
    elif not answer and children:
        if len(children) == 1:
            children_str = children[0]
        elif len(results) == 2:
            children_str = " and ".join(children)
        else:
            children_str = ", ".join(children[:-1]) + ", and " + children[-1]
            
        print(f"Chatbot: Only {children_str}\n")
    else:
        print("Chatbot: No\n")

#https://stackoverflow.com/questions/41192424/python-how-to-correct-misspelled-names
#https://docs.python.org/3/library/difflib.html
def misspelledWordsForQuery(word: str) -> str:
    corrected_queries = ['father', 'mother', 'child', 'children', 'son', 'daughter', 'sibling',
                         'brother', 'sister', 'grandmother', 'grandfather', 'aunt', 'uncle',
                         'grandparent', 'relative', 'parent']
    check_spelling = difflib.get_close_matches(word, corrected_queries, n=1, cutoff=0.7)
    if check_spelling:
        if check_spelling[0] == 'children':
            return 'child'
        return check_spelling[0]
    else: return word

def fixDuplicates(word: list) -> str:
    results = set() #remove duplicates
    for answer in word:
        name = answer['X'].capitalize()
        results.add(name)

    results = list(results) #back to list so I can access them

    if len(results) == 1:
        return "is", results[0]
    elif len(results) == 2:
        return "are", " and ".join(results)

    return "are", ", ".join(results[:-1]) + ", and " + results[-1]

def fixName(name: str) -> str:
    character = name[-1]
    if not character.isalpha():
        name = name[:-1] #remove punctuation character like ","
    return name


starting_questions = ['is', 'are', 'who']

print("   QUESTION PROMPTS")
print("-------------------------------------------------------------------------------")
print("   Is ___ a daughter of ___?       |     Who is the mother of ___?")
print("   Is ___ a son of ___?            |     Who is the father of ___?")
print("   Is ___ a sister of ___?         |     Who are the sisters of ___?")
print("   Is ___ a brother of ___?        |     Who are the brothers of ___?")
print("   Is ___ the mother of ___?       |     Who are the siblings of ___?")
print("   Is ___ the father of ___?       |     Who are the parents of ___?")
print("   Is ___ an aunt of ___?          |     Who are the daughters of ___?")
print("   Is ___ an uncle of ___?         |     Who are the sons of ___?")
print("   Is ___ a grandmother of ___?    |     Who are the children of ___?")
print("   Is ___ a grandfather of ___?    |     Are ___ and ___ relatives?")
print("   Is ___ a child of ___?          |     Are ___ and ___ the parents of ___?")
print("   Are ___ and ___ siblings?       |     Are ___, ___ and ___ children of ___?")
print("-------------------------------------------------------------------------------\n")

go_question = True
while go_question:
    no_error = True
    while no_error:
        question = input("You: ")
        words = question.lower().split(" ") #should query in all lower case
        if words[0] == 'exit':
            go_question = False
            break

        #print(words[-1][:-1])
        if words[0] not in starting_questions or words[-1][-1] != '?':
            print("Chatbot: Statement is not a question. End it with question mark \"?\" too.\n")
        else:
            no_error = False


    if words[0] == starting_questions[0]: #Is questions -> Yes or No answers
        relationship = misspelledWordsForQuery(words[3]) #accounts for misspelling queries for smooth conversation
        if not relationship:
            print("Chatbot: Unknown \"Is\" Question. Kindly refer to the questions prompts for guidance.\n")
            continue
        #print(f"QUERYING: {relationship}({words[1]}, {words[-1][:-1]})")
        answer = bool(list(prolog.query(f"{relationship}({words[1]}, {words[-1][:-1]})")))
        yesNoChatbot(answer)

    elif words[0] == starting_questions[1]: #"Are" questions -> Yes or No answers
        if words[4] == words[-1]: #Questions "siblings" or "relatives"
            relationship = misspelledWordsForQuery(words[4][:-1]) 
            #print(f"QUERYING: {relationship}({words[1]}, {words[3]})")
            answer = bool(list(prolog.query(f"{relationship}({words[1]}, {words[3]})")))
            if not answer: #try switching names
                #print(f"QUERYING: {relationship}({words[3]}, {words[1]})")
                answer = bool(list(prolog.query(f"{relationship}({words[3]}, {words[1]})")))
            yesNoChatbot(answer)

        elif misspelledWordsForQuery(words[5]) == 'parent': #Questions "parents of"
            #print(f"QUERYING: parents_of({words[1]}, {words[3]}, {words[-1][:-1]})")
            answer = bool(list(prolog.query(f"parents_of({words[1]}, {words[3]}, {words[-1][:-1]})")))
            yesNoChatbot(answer)

        elif misspelledWordsForQuery(words[-3]) == 'children': #Questions "Children" -> Can ask 2 or more children
            relationship = misspelledWordsForQuery(words[-3]) 
            found_and = False #boolean for checking the word "and"
            all_children = True #boolean for checking if parent has this all children
            list_of_children = []
            parent = words[-1][:-1]
            word_ctr = 1 #set to 1 since second word is the name
            
            while not found_and:
                child_name = fixName(word[word_ctr])
                if child_name == "and":
                    found_and = True #this means last checking of child
                    child_name = fixName(word[word_ctr+1])
                
                #print(f"QUERYING: child({child_name}, {parent})")
                answer = bool(list(prolog.query(f"child({child_name}, {parent})")))
                if answer:
                    list_of_children.append(child_name.capitalize())
                else:
                    all_children = False #automatic false if one is not
                word_ctr = word_ctr + 1 #next name

            chatbotReply(list_of_children, all_children)
                
        else:
            print("Chatbot: Unknown \"Are\" Question. Kindly refer to the questions prompts for guidance.\n")

    elif words[0] == starting_questions[2]: #Who questions
        relationship = misspelledWordsForQuery(words[3])
        if not relationship:
            print("Chatbot: Unknown \"Who\" Question. Kindly refer to the questions prompts for guidance.\n")
            continue
        #print(f"QUERYING: {relationship}(X, {words[-1][:-1]})")
        answer = list(prolog.query(f"{relationship}(X, {words[-1][:-1]})"))
        if not answer:
            print(f"Chatbot: {words[-1][:-1].capitalize()} has no {words[3]}.\n")
        else:
            verb, response = fixDuplicates(answer)
            print(f"Chatbot: The {words[3]} of {words[-1][:-1].capitalize()} {verb} {response}\n")








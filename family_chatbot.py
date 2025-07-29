#!/usr/bin/env python3
"""
Family Relationship Chatbot
A conversational chatbot that understands family relationships using PROLOG inference engine.
"""

import difflib
import re
import sys
from typing import List, Optional, Tuple

from pyswip import Prolog


class FamilyChatbot:
    def __init__(self):
        """Initialize the chatbot with PROLOG engine and knowledge base."""
        try:
            self.prolog = Prolog()
            self.setup_knowledge_base()
        except Exception as e:
            print(f"Error initializing PROLOG: {e}")
            print("Trying alternative initialization...")
            # Try with explicit path
            import os

            os.environ["SWI_HOME_DIR"] = r"C:\Program Files\swipl"
            self.prolog = Prolog()
            self.setup_knowledge_base()

    def setup_knowledge_base(self):
        """Set up the PROLOG knowledge base with family relationship rules."""
        try:
            # Load rules from the relationships.pl file
            self.load_prolog_file("relationships.pl")
            print("✓ Successfully loaded PROLOG rules from relationships.pl")
        except Exception as e:
            print(f"Warning: Could not load relationships.pl: {e}")
            print("Falling back to hardcoded rules...")
            self.load_hardcoded_rules()

    def load_prolog_file(self, filename):
        """Load PROLOG rules from a file."""
        try:
            with open(filename, "r") as file:
                content = file.read()

            # Split into lines and filter out comments and empty lines
            lines = [line.strip() for line in content.split("\n")]
            rules = []

            for line in lines:
                # Skip empty lines, comments, and lines starting with /*
                if (
                    line
                    and not line.startswith("/*")
                    and not line.startswith("%")
                    and not line.startswith("//")
                ):
                    # Remove trailing comments
                    if "/*" in line:
                        line = line.split("/*")[0].strip()

                    if line:
                        rules.append(line)

            # Handle dynamic predicates first (they need special treatment)
            dynamic_predicates = []
            regular_rules = []

            for rule in rules:
                if rule.startswith(":- dynamic"):
                    dynamic_predicates.append(rule)
                else:
                    regular_rules.append(rule)

            # Assert dynamic predicates using query to avoid syntax issues
            for dynamic_rule in dynamic_predicates:
                try:
                    # Extract the predicate from :- dynamic pred/arity
                    if ":- dynamic" in dynamic_rule:
                        predicate_part = dynamic_rule.replace(":- dynamic", "").strip()
                        # Remove trailing period if present
                        if predicate_part.endswith("."):
                            predicate_part = predicate_part[:-1]
                        # Use query to execute the dynamic directive
                        list(self.prolog.query(f"dynamic({predicate_part})"))
                except Exception as e:
                    print(
                        f"Warning: Could not process dynamic predicate {dynamic_rule}: {e}"
                    )

            # Assert regular rules - clean them up first
            for rule in regular_rules:
                if rule:
                    try:
                        # Clean up the rule: remove extra whitespace and ensure proper formatting
                        cleaned_rule = " ".join(rule.split())  # Normalize whitespace
                        # Remove trailing period if present
                        if cleaned_rule.endswith("."):
                            cleaned_rule = cleaned_rule[:-1]

                        self.prolog.assertz(cleaned_rule)
                    except Exception as e:
                        print(f"Warning: Could not assert rule '{rule}': {e}")

        except FileNotFoundError:
            raise Exception(f"PROLOG file '{filename}' not found")
        except Exception as e:
            raise Exception(f"Error reading PROLOG file: {e}")

    def load_hardcoded_rules(self):
        """Fallback to hardcoded rules if file loading fails."""
        # Define dynamic predicates
        self.prolog.assertz(":- dynamic parent/2")
        self.prolog.assertz(":- dynamic male/1")
        self.prolog.assertz(":- dynamic female/1")

        # Family relationship rules
        rules = [
            # Parents
            "father(F,C) :- parent(F,C), male(F)",
            "mother(M,C) :- parent(M,C), female(M)",
            # Children
            "child(C,P) :- parent(P,C)",
            "son(S,P) :- child(S,P), male(S)",
            "daughter(D,P) :- child(D,P), female(D)",
            # Siblings
            "sibling(X,Y) :- parent(P,X), parent(P,Y), X \\= Y",
            "brother(B,Sib) :- sibling(B,Sib), male(B)",
            "sister(S,Sib) :- sibling(S,Sib), female(S)",
            # Grandparents
            "grandparent(GP,C) :- parent(GP,P), parent(P,C)",
            "grandfather(GF,C) :- grandparent(GF,C), male(GF)",
            "grandmother(GM,C) :- grandparent(GF,C), female(GM)",
            # Ancestors
            "ancestor(A,D) :- parent(A,D)",
            "ancestor(A,D) :- parent(A,X), ancestor(X,D)",
            # Uncles and Aunts
            "uncle(U,N) :- parent(P,N), sibling(U,P), male(U)",
            "aunt(A,N) :- parent(P,N), sibling(A,P), female(A)",
            # Parents of
            "parents_of(P1,P2,C) :- parent(P1,C), parent(P2,C), P1 \\= P2",
        ]

        for rule in rules:
            self.prolog.assertz(rule)

    def extract_names(self, text: str) -> List[str]:
        """Extract capitalized names from text."""
        # Pattern for names: starts with capital letter, followed by lowercase letters
        name_pattern = r"\b[A-Z][a-z]+\b"
        return re.findall(name_pattern, text)

    def parse_statement(self, text: str) -> Optional[Tuple[str, List[str]]]:
        """Parse statements to determine relationship type and extract names."""
        text = text.lower().strip()

        # Statement patterns according to specifications
        patterns = {
            "sister": [r"(\w+) is a sister of (\w+)", r"(\w+) is the sister of (\w+)"],
            "siblings": [r"(\w+) and (\w+) are siblings"],
            "mother": [r"(\w+) is the mother of (\w+)", r"(\w+) is a mother of (\w+)"],
            "grandmother": [
                r"(\w+) is a grandmother of (\w+)",
                r"(\w+) is the grandmother of (\w+)",
            ],
            "child": [r"(\w+) is a child of (\w+)", r"(\w+) is the child of (\w+)"],
            "daughter": [
                r"(\w+) is a daughter of (\w+)",
                r"(\w+) is the daughter of (\w+)",
            ],
            "uncle": [r"(\w+) is an uncle of (\w+)", r"(\w+) is the uncle of (\w+)"],
            "brother": [
                r"(\w+) is a brother of (\w+)",
                r"(\w+) is the brother of (\w+)",
            ],
            "father": [r"(\w+) is the father of (\w+)", r"(\w+) is a father of (\w+)"],
            "parents_of": [r"(\w+) and (\w+) are the parents of (\w+)"],
            "grandfather": [
                r"(\w+) is a grandfather of (\w+)",
                r"(\w+) is the grandfather of (\w+)",
            ],
            "son": [r"(\w+) is a son of (\w+)", r"(\w+) is the son of (\w+)"],
            "aunt": [r"(\w+) is an aunt of (\w+)", r"(\w+) is the aunt of (\w+)"],
            "children_of": [
                r"(\w+) and (\w+) are children of (\w+)",
                r"(\w+) (\w+) and (\w+) are children of (\w+)",
            ],
        }

        for rel_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, text)
                if match:
                    names = [name.lower() for name in match.groups()]
                    return (rel_type, names)

        return None

    def parse_question(self, text: str) -> Optional[Tuple[str, List[str]]]:
        """Parse questions to determine query type and extract names."""
        text = text.lower().strip()

        # Question patterns according to specifications
        patterns = {
            "are_siblings": [r"are (\w+) and (\w+) siblings\?"],
            "who_siblings": [r"who are the siblings of (\w+)\?"],
            "is_sister": [
                r"is (\w+) a sister of (\w+)\?",
                r"is (\w+) the sister of (\w+)\?",
            ],
            "is_brother": [
                r"is (\w+) a brother of (\w+)\?",
                r"is (\w+) the brother of (\w+)\?",
            ],
            "is_mother": [r"is (\w+) the mother of (\w+)\?"],
            "is_father": [r"is (\w+) the father of (\w+)\?"],
            "are_parents": [r"are (\w+) and (\w+) the parents of (\w+)\?"],
            "who_sisters": [r"who are the sisters of (\w+)\?"],
            "who_brothers": [r"who are the brothers of (\w+)\?"],
            "who_mother": [r"who is the mother of (\w+)\?"],
            "who_father": [r"who is the father of (\w+)\?"],
            "who_parents": [r"who are the parents of (\w+)\?"],
            "is_grandmother": [
                r"is (\w+) a grandmother of (\w+)\?",
                r"is (\w+) the grandmother of (\w+)\?",
            ],
            "is_grandfather": [
                r"is (\w+) a grandfather of (\w+)\?",
                r"is (\w+) the grandfather of (\w+)\?",
            ],
            "is_daughter": [
                r"is (\w+) a daughter of (\w+)\?",
                r"is (\w+) the daughter of (\w+)\?",
            ],
            "is_son": [r"is (\w+) a son of (\w+)\?", r"is (\w+) the son of (\w+)\?"],
            "who_daughters": [r"who are the daughters of (\w+)\?"],
            "who_sons": [r"who are the sons of (\w+)\?"],
            "is_child": [
                r"is (\w+) a child of (\w+)\?",
                r"is (\w+) the child of (\w+)\?",
            ],
            "who_children": [r"who are the children of (\w+)\?"],
            "are_children": [
                r"are (\w+) and (\w+) children of (\w+)\?",
                r"are (\w+) (\w+) and (\w+) children of (\w+)\?",
            ],
            "is_aunt": [
                r"is (\w+) an aunt of (\w+)\?",
                r"is (\w+) the aunt of (\w+)\?",
            ],
            "is_uncle": [
                r"is (\w+) an uncle of (\w+)\?",
                r"is (\w+) the uncle of (\w+)\?",
            ],
            "are_relatives": [r"are (\w+) and (\w+) relatives\?"],
        }

        for query_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, text)
                if match:
                    names = [name.lower() for name in match.groups()]
                    return (query_type, names)

        return None

    def submit_query(self, rel, names):
        person1, person2 = names
        if rel == "male" or rel == "female":
            resp = self.prolog.query(f"{rel}({person1})")
        else:
            resp = self.prolog.query(f"{rel}({person1}, {person2})")
        return list(resp)

    def submit_assert(self, rel, names):
        person1, person2 = names
        try:
            if rel == "male" or rel == "female":
                self.prolog.assertz(f"{rel}({person1})")
            else:
                self.prolog.assertz(f"{rel}({person1}, {person2})")
            return True
        except:
            return False

    def check_feasibility(self, rel_type: str, names: List[str]) -> bool:
        """Check if a relationship statement is feasible."""
        if rel_type in ["mother", "father", "child", "daughter", "son"]:
            if len(names) != 2:
                return False
            person1, person2 = names

            # Check for self-relationships
            if person1 == person2:
                return False

            # Check for circular relationships
            try:
                if rel_type in ["mother", "father"]:
                    # Check if child is already a parent of the parent
                    print(list(self.prolog.query(f"ancestor({person2}, {person1})")))
                    result = list(self.prolog.query(f"ancestor({person2}, {person1})"))[
                        :5
                    ]
                    if result:
                        return False
                elif rel_type in ["child", "daughter", "son"]:
                    # Check if parent is already a child of the child
                    result = list(self.prolog.query(f"ancestor({person1}, {person2})"))[
                        :5
                    ]
                    if result:
                        return False
            except:
                pass

            return True

        elif rel_type in ["sister", "brother", "siblings"]:
            if len(names) != 2:
                return False
            person1, person2 = names

            # Check for self-sibling
            if person1 == person2:
                return False

            return True

        elif rel_type in ["grandmother", "grandfather"]:
            if len(names) != 2:
                return False
            grandparent, grandchild = names

            # Check for self-grandparent
            if grandparent == grandchild:
                return False

            return True

        elif rel_type in ["uncle", "aunt"]:
            if len(names) != 2:
                return False
            uncle_aunt, niece_nephew = names

            # Check for self-uncle/aunt
            if uncle_aunt == niece_nephew:
                return False

            return True

        elif rel_type == "parents_of":
            if len(names) != 3:
                return False
            parent1, parent2, child = names

            # Check for self-parenting
            if parent1 == child or parent2 == child:
                return False

            # Check for same parent
            if parent1 == parent2:
                return False

            return True

        elif rel_type == "children_of":
            if len(names) < 3:
                return False
            children = names[:-1]
            parent = names[-1]

            # Check for self-parenting
            if parent in children:
                return False

            # Check for duplicate children
            if len(children) != len(set(children)):
                return False

            return True

        return False

    def check_contradiction(self, relation: str, names) -> list[str]:
        contradictions = []

        x, y = names
        x = x.lower()
        y = y.lower()

        relation = relation.lower()

        # Prevent self-relationships
        if x == y:
            contradictions.append("self-relationship")

        # Check reverse of the same relationship
        if relation == "parent" and list(self.prolog.query(f"parent({y}, {x})")):
            contradictions.append("reverse parent already exists")
        if (
            relation == "parent" or relation == "father" or relation == "mother"
        ) and len(list(self.prolog.query(f"parent(X, {y})"))) > 1:
            contradictions.append("more than two parents")
        if relation == "child" and list(self.prolog.query(f"child({y}, {x})")):
            contradictions.append("reverse child already exists")
        if relation == "father" and len(list(self.prolog.query(f"father(X,{y})"))) > 0:
            contradictions.append("can only have one father")
        if relation == "mother" and len(list(self.prolog.query(f"mother(X,{y})"))) > 0:
            contradictions.append("can only have one mother")

        # Specific contradictory relationship rules
        if relation in ["father", "mother"]:
            # Cant also be child's child, sibling, or cousin
            for rel in ["child", "sibling", "descendant"]:
                if list(self.prolog.query(f"{rel}({x}, {y})")):
                    contradictions.append(
                        f"{x} cannot be both {relation} and {rel} of {y}"
                    )
            # Cant also be uncle/aunt
            for rel in ["uncle", "aunt"]:
                if list(self.prolog.query(f"{rel}({x}, {y})")):
                    contradictions.append(
                        f"{x} cannot be both {relation} and {rel} of {y}"
                    )
            # Cant be grandmother and grandfather at once
            if relation == "father" and list(self.prolog.query(f"female({x})")):
                contradictions.append("father cannot be female")
            if relation == "mother" and list(self.prolog.query(f"male({x})")):
                contradictions.append("mother cannot be male")

        if relation in ["uncle", "aunt"]:
            # Cant be a parent, grandparent, sibling, or cousin
            for rel in ["parent", "grandparent", "sibling"]:
                if list(self.prolog.query(f"{rel}({x}, {y})")):
                    contradictions.append(
                        f"{x} cannot be both {relation} and {rel} of {y}"
                    )

        if relation in ["brother", "sister"]:
            # Cant be parent or child
            for rel in ["parent", "child"]:
                if list(self.prolog.query(f"{rel}({x}, {y})")):
                    contradictions.append(
                        f"{x} cannot be both {relation} and {rel} of {y}"
                    )

        if relation in ["son", "daughter"]:
            # Cant be parent of the same person
            if list(self.prolog.query(f"parent({x}, {y})")):
                contradictions.append(f"{x} cannot be both child and parent of {y}")
            # Gendercheck
            if relation == "son" and list(self.prolog.query(f"female({x})")):
                contradictions.append("son cannot be female")
            if relation == "daughter" and list(self.prolog.query(f"male({x})")):
                contradictions.append("daughter cannot be male")

        return bool(contradictions)

    def add_fact(self, rel_type: str, names: List[str]) -> str:
        """Add a fact to the knowledge base."""
        try:
            if rel_type == "mother":
                mother, child = names
                self.prolog.assertz(f"parent({mother}, {child})")
                self.prolog.assertz(f"female({mother})")
                return "OK! I learned something."

            elif rel_type == "father":
                father, child = names
                self.prolog.assertz(f"parent({father}, {child})")
                self.prolog.assertz(f"male({father})")
                return "OK! I learned something."

            elif rel_type == "child":
                child, parent = names
                self.prolog.assertz(f"parent({parent}, {child})")
                return "OK! I learned something."

            elif rel_type == "daughter":
                daughter, parent = names
                self.prolog.assertz(f"parent({parent}, {daughter})")
                self.prolog.assertz(f"female({daughter})")
                return "OK! I learned something."

            elif rel_type == "son":
                son, parent = names
                self.prolog.assertz(f"parent({parent}, {son})")
                self.prolog.assertz(f"male({son})")
                return "OK! I learned something."

            elif rel_type == "sister":
                sister, sibling = names
                # Add parent relationship to make them siblings
                # This is a simplified approach - in practice, you'd need to know their common parent
                self.prolog.assertz(f"female({sister})")
                return "OK! I learned something."

            elif rel_type == "brother":
                brother, sibling = names
                # Add parent relationship to make them siblings
                # This is a simplified approach - in practice, you'd need to know their common parent
                self.prolog.assertz(f"male({brother})")
                return "OK! I learned something."

            elif rel_type == "siblings":
                sibling1, sibling2 = names
                # This is a simplified approach - in practice, you'd need to know their common parent
                parents_1 = [
                    res["X"]
                    for res in list(self.prolog.query(f"parent(X, {sibling1})"))
                ]
                parents_2 = [
                    res["X"]
                    for res in list(self.prolog.query(f"parent(X, {sibling2})"))
                ]
                common_parent = set(parents_1) & set(parents_2)
                if common_parent:
                    return "OK! I learned something."
                elif len(parents_1) == 1 or len(parents_2) == 1:
                    choice = input(
                        "Can you provide us information about their common parent? [y/n]"
                    )
                    if choice.lower() == "y":
                        common_name = input("Name of common parent: ")
                        self.submit_assert("parent", [common_name.lower(), sibling1])
                        self.submit_assert("parent", [common_name.lower(), sibling2])
                        return "OK! I learned something."

                return "That's impossible!"

            elif rel_type == "grandmother":
                if bool(self.submit_query("grandparent", names)):
                    grandmother, grandchild = names
                    self.prolog.assertz(f"female({grandmother})")
                    return "OK! I learned something."
                else:
                    return "That's impossible!"

            elif rel_type == "grandfather":
                if bool(self.submit_query("grandparent", names)):
                    grandfather, grandchild = names
                    self.prolog.assertz(f"male({grandfather})")
                    return "OK! I learned something."
                else:
                    return "That's impossible!"

            elif rel_type == "uncle":
                uncle, niece_nephew = names
                if bool(self.submit_query("uncle", names)):
                    self.prolog.assertz(f"male({uncle})")
                    return "OK! I learned something."
                else:
                    return "That's impossible!"

            elif rel_type == "aunt":
                aunt, niece_nephew = names
                if bool(self.submit_query("aunt", names)):
                    self.prolog.assertz(f"female({uncle})")
                    return "OK! I learned something."
                else:
                    return "That's impossible!"

            elif rel_type == "parents_of":
                parent1, parent2, child = names
                self.prolog.assertz(f"parent({parent1}, {child})")
                self.prolog.assertz(f"parent({parent2}, {child})")
                return "OK! I learned something."

            elif rel_type == "children_of":
                children = names[:-1]
                parent = names[-1]
                for child in children:
                    self.prolog.assertz(f"parent({parent}, {child})")
                return "OK! I learned something."

        except Exception as e:
            return f"Error adding fact: {str(e)}"

    def query_relationship(self, query_type: str, names: List[str]) -> str:
        """Query the knowledge base for relationships."""
        try:
            if query_type == "are_siblings":
                person1, person2 = names
                # Limit results to prevent infinite loops
                result = list(self.prolog.query(f"sibling({person1}, {person2})"))[:10]
                return "Yes!" if result else "No!"

            elif query_type == "who_siblings":
                person = names[0]
                siblings = list(self.prolog.query(f"sibling({person}, Sibling)"))[:10]
                if siblings:
                    sibling_names = [s["Sibling"] for s in siblings]
                    return f"{', '.join(sibling_names)}"
                else:
                    return "I don't know."

            elif query_type == "is_sister":
                sister, sibling = names
                result = list(self.prolog.query(f"sister({sister}, {sibling})"))
                return "Yes!" if result else "No!"

            elif query_type == "is_brother":
                brother, sibling = names
                result = list(self.prolog.query(f"brother({brother}, {sibling})"))
                return "Yes!" if result else "No!"

            elif query_type == "is_mother":
                mother, child = names
                result = list(self.prolog.query(f"mother({mother}, {child})"))
                return "Yes!" if result else "No!"

            elif query_type == "is_father":
                father, child = names
                result = list(self.prolog.query(f"father({father}, {child})"))
                return "Yes!" if result else "No!"

            elif query_type == "are_parents":
                parent1, parent2, child = names
                result1 = list(self.prolog.query(f"parent({parent1}, {child})"))
                result2 = list(self.prolog.query(f"parent({parent2}, {child})"))
                return "Yes!" if result1 and result2 else "No!"

            elif query_type == "who_sisters":
                person = names[0]
                sisters = list(self.prolog.query(f"sister(Sister, {person})"))[:10]
                if sisters:
                    sister_names = [s["Sister"] for s in sisters]
                    return f"{', '.join(sister_names)}"
                else:
                    return "I don't know."

            elif query_type == "who_brothers":
                person = names[0]
                brothers = list(self.prolog.query(f"brother(Brother, {person})"))[:10]
                if brothers:
                    brother_names = [b["Brother"] for b in brothers]
                    return f"{', '.join(brother_names)}"
                else:
                    return "I don't know."

            elif query_type == "who_mother":
                person = names[0]
                mothers = list(self.prolog.query(f"mother(Mother, {person})"))[:10]
                if mothers:
                    mother_names = [m["Mother"] for m in mothers]
                    return f"{', '.join(mother_names)}"
                else:
                    return "I don't know."

            elif query_type == "who_father":
                person = names[0]
                fathers = list(self.prolog.query(f"father(Father, {person})"))[:10]
                if fathers:
                    father_names = [f["Father"] for f in fathers]
                    return f"{', '.join(father_names)}"
                else:
                    return "I don't know."

            elif query_type == "who_parents":
                person = names[0]
                parents = list(self.prolog.query(f"parent(Parent, {person})"))[:10]
                if parents:
                    parent_names = [p["Parent"] for p in parents]
                    return f"{', '.join(parent_names)}"
                else:
                    return "I don't know."

            elif query_type == "is_grandmother":
                grandmother, grandchild = names
                result = list(
                    self.prolog.query(f"grandmother({grandmother}, {grandchild})")
                )
                return "Yes!" if result else "No!"

            elif query_type == "is_grandfather":
                grandfather, grandchild = names
                result = list(
                    self.prolog.query(f"grandfather({grandfather}, {grandchild})")
                )
                return "Yes!" if result else "No!"

            elif query_type == "is_daughter":
                daughter, parent = names
                result = list(self.prolog.query(f"daughter({daughter}, {parent})"))
                return "Yes!" if result else "No!"

            elif query_type == "is_son":
                son, parent = names
                result = list(self.prolog.query(f"son({son}, {parent})"))
                return "Yes!" if result else "No!"

            elif query_type == "who_daughters":
                person = names[0]
                daughters = list(self.prolog.query(f"daughter(Daughter, {person})"))[
                    :10
                ]
                if daughters:
                    daughter_names = [d["Daughter"] for d in daughters]
                    return f"{', '.join(daughter_names)}"
                else:
                    return "I don't know."

            elif query_type == "who_sons":
                person = names[0]
                sons = list(self.prolog.query(f"son(Son, {person})"))[:10]
                if sons:
                    son_names = [s["Son"] for s in sons]
                    return f"{', '.join(son_names)}"
                else:
                    return "I don't know."

            elif query_type == "is_child":
                child, parent = names
                result = list(self.prolog.query(f"child({child}, {parent})"))
                return "Yes!" if result else "No!"

            elif query_type == "who_children":
                person = names[0]
                children = list(self.prolog.query(f"child(Child, {person})"))[:10]
                if children:
                    child_names = [c["Child"] for c in children]
                    return f"{', '.join(child_names)}"
                else:
                    return "I don't know."

            elif query_type == "are_children":
                if len(names) == 3:
                    child1, child2, parent = names
                    result1 = list(self.prolog.query(f"child({child1}, {parent})"))
                    result2 = list(self.prolog.query(f"child({child2}, {parent})"))
                    return "Yes!" if result1 and result2 else "No!"
                elif len(names) == 4:
                    child1, child2, child3, parent = names
                    result1 = list(self.prolog.query(f"child({child1}, {parent})"))
                    result2 = list(self.prolog.query(f"child({child2}, {parent})"))
                    result3 = list(self.prolog.query(f"child({child3}, {parent})"))
                    return "Yes!" if result1 and result2 and result3 else "No!"

            elif query_type == "is_aunt":
                aunt, niece_nephew = names
                result = list(self.prolog.query(f"aunt({aunt}, {niece_nephew})"))
                return "Yes!" if result else "No!"

            elif query_type == "is_uncle":
                uncle, niece_nephew = names
                result = list(self.prolog.query(f"uncle({uncle}, {niece_nephew})"))
                return "Yes!" if result else "No!"

            elif query_type == "are_relatives":
                person1, person2 = names
                # Check if they share any family relationship
                result = list(self.prolog.query(f"relative({person1}, {person2})"))
                return "Yes!" if result else "No!"

        except Exception as e:
            return f"Error querying relationship: {str(e)}"

    def yesNoChatbot(self, answer: bool):
        if answer:
            return "Yes\n"
        else:
            return "No\n"

    def chatbotReply(self, children: list, answer: bool):
        if answer and children:
            return "Yes\n"
        elif not answer and children:
            if len(children) == 1:
                children_str = children[0]
            elif len(children) == 2:
                children_str = " and ".join(children)
            else:
                children_str = ", ".join(children[:-1]) + ", and " + children[-1]

            return f"Only {children_str}\n"
        else:
            return "No\n"

    # https://stackoverflow.com/questions/41192424/python-how-to-correct-misspelled-names
    # https://docs.python.org/3/library/difflib.html
    def misspelledWordsForQuery(self, word: str) -> str:
        corrected_queries = [
            "father",
            "mother",
            "child",
            "children",
            "son",
            "daughter",
            "sibling",
            "brother",
            "sister",
            "grandmother",
            "grandfather",
            "aunt",
            "uncle",
            "grandparent",
            "relative",
            "parent",
        ]
        check_spelling = difflib.get_close_matches(
            word, corrected_queries, n=1, cutoff=0.7
        )
        if check_spelling:
            if check_spelling[0] == "children":
                return "child"
            return check_spelling[0]
        else:
            return word

    def fixDuplicates(self, word: list) -> str:
        results = set()  # remove duplicates
        for answer in word:
            name = answer["X"].capitalize()
            results.add(name)

        results = list(results)  # back to list so I can access them

        if len(results) == 1:
            return "is", results[0]
        elif len(results) == 2:
            return "are", " and ".join(results)

        return "are", ", ".join(results[:-1]) + ", and " + results[-1]

    def fixName(self, name: str) -> str:
        character = name[-1]
        if not character.isalpha():
            name = name[:-1]  # remove punctuation character like ","
        return name

    def ask_question(self, question):
        starting_questions = ["is", "are", "who"]
        words = question.lower().split(" ")  # should query in all lower case
        if words[0] == starting_questions[0]:  # Is questions -> Yes or No answers
            relationship = self.misspelledWordsForQuery(
                words[3]
            )  # accounts for misspelling queries for smooth conversation
            if not relationship:
                return 'Unknown "Is" Question. Kindly refer to the questions prompts for guidance.\n'
            # print(f"QUERYING: {relationship}({words[1]}, {words[-1][:-1]})")
            answer = bool(
                list(self.prolog.query(f"{relationship}({words[1]}, {words[-1][:-1]})"))
            )
            return self.yesNoChatbot(answer)

        elif words[0] == starting_questions[1]:  # "Are" questions -> Yes or No answers
            if words[4] == words[-1]:  # Questions "siblings" or "relatives"
                relationship = self.misspelledWordsForQuery(words[4][:-1])
                # print(f"QUERYING: {relationship}({words[1]}, {words[3]})")
                answer = bool(
                    list(self.prolog.query(f"{relationship}({words[1]}, {words[3]})"))
                )
                if not answer:  # try switching names
                    # print(f"QUERYING: {relationship}({words[3]}, {words[1]})")
                    answer = bool(
                        list(
                            self.prolog.query(f"{relationship}({words[3]}, {words[1]})")
                        )
                    )
                self.yesNoChatbot(answer)

            elif (
                self.misspelledWordsForQuery(words[5]) == "parent"
            ):  # Questions "parents of"
                # print(f"QUERYING: parents_of({words[1]}, {words[3]}, {words[-1][:-1]})")
                answer = bool(
                    list(
                        self.prolog.query(
                            f"parents_of({words[1]}, {words[3]}, {words[-1][:-1]})"
                        )
                    )
                )
                return self.yesNoChatbot(answer)

            elif (
                self.misspelledWordsForQuery(words[-3]) == "child"
                or words[-3] == "children"
            ):  # Questions "Children" -> Can ask 2 or more children
                relationship = self.misspelledWordsForQuery(words[-3])
                found_and = False  # boolean for checking the word "and"
                all_children = (
                    True  # boolean for checking if parent has this all children
                )
                list_of_children = []
                parent = words[-1][:-1]
                word_ctr = 1  # set to 1 since second word is the name

                while not found_and:
                    child_name = self.fixName(words[word_ctr])
                    if child_name == "and":
                        found_and = True  # this means last checking of child
                        child_name = self.fixName(words[word_ctr + 1])

                    # print(f"QUERYING: child({child_name}, {parent})")
                    answer = bool(
                        list(self.prolog.query(f"child({child_name}, {parent})"))
                    )
                    if answer:
                        list_of_children.append(child_name.capitalize())
                    else:
                        all_children = False  # automatic false if one is not
                    word_ctr = word_ctr + 1  # next name

                return self.chatbotReply(list_of_children, all_children)

            else:
                return 'Unknown "Are" Question. Kindly refer to the questions prompts for guidance.\n'

        elif words[0] == starting_questions[2]:  # Who questions
            relationship = self.misspelledWordsForQuery(words[3])
            if not relationship:
                return 'Unknown "Who" Question. Kindly refer to the questions prompts for guidance.\n'
            # print(f"QUERYING: {relationship}(X, {words[-1][:-1]})")
            answer = list(self.prolog.query(f"{relationship}(X, {words[-1][:-1]})"))
            if not answer:
                return f"{words[-1][:-1].capitalize()} has no {words[3]}.\n"
            else:
                verb, response = self.fixDuplicates(answer)
                return f"The {words[3]} of {words[-1][:-1].capitalize()} {verb} {response}\n"

    def process_input(self, user_input: str) -> str:
        """Process user input and return appropriate response."""
        # Check if it's a question (ends with ?)
        if user_input.strip().endswith("?"):
            parsed = self.parse_question(user_input)
            if parsed:
                query_type, names = parsed
                return self.ask_question(user_input)
            else:
                return "I don't understand that question format. Please try a different way of asking."

        # Check if it's a statement
        else:
            parsed = self.parse_statement(user_input)
            if parsed:
                rel_type, names = parsed
                # print(f"Parsed: {rel_type}, {names}")
                if not self.check_contradiction(rel_type, names):
                    # print("Adding fact...")
                    # print("Fact added!")
                    return self.add_fact(rel_type, names)
                else:
                    return "That's impossible!"
            else:
                return "I don't understand that statement format. Please try a different way of expressing the relationship."

    def run(self):
        """Main chatbot loop."""
        print("=" * 60)
        print("Welcome to the Family Relationship Chatbot!")
        print("I can help you manage and query family relationships.")
        print("\nExamples of statements you can make:")
        print("- John is the parent of Mary")
        print("- Alice is female")
        print("- Bob is male")
        print("\nExamples of questions you can ask:")
        print("- Is John the parent of Mary?")
        print("- Are Alice and Bob siblings?")
        print("- Who are Mary's parents?")
        print("\nType 'quit' to exit.")
        print("=" * 60)

        while True:
            try:
                user_input = input("\nYou: ").strip()

                if user_input.lower() in ["quit", "exit", "bye"]:
                    print("Goodbye! Thanks for using the Family Relationship Chatbot!")
                    break

                if not user_input:
                    continue

                response = self.process_input(user_input)
                print(f"Chatbot: {response}")

            except KeyboardInterrupt:
                print("\n\nGoodbye! Thanks for using the Family Relationship Chatbot!")
                break
            except Exception as e:
                print(f"Chatbot: An error occurred: {str(e)}")


def main():
    """Main function to run the chatbot."""
    try:
        chatbot = FamilyChatbot()
        chatbot.run()
    except Exception as e:
        print(f"Error initializing chatbot: {str(e)}")
        print("Make sure you have PROLOG installed and pyswip is properly configured.")
        sys.exit(1)


if __name__ == "__main__":
    main()

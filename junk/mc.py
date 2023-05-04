import argparse
from typing import Dict, List, Union
import random


def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--question", help="question to ask.")
    return parser.parse_args(args)


def is_choice(word: str):
    if len(word) == 1:
        return False
    return word[0].isalpha() and word[1] == ")"


def extract_choice_string(choice_start: int, choice_str: List[str]):
    buff: str = ""
    for i in range(choice_start, len(choice_str)):
        if is_choice(choice_str[i]):
            break
        buff += f"{choice_str[i]} "
    return buff.rstrip()


def parse_choices(choices_start: str, choices_start_position: int) -> Dict[str, str]:
    choices_dict = {}
    choices = choices_start.split(" ")
    for i in range(choices_start_position, len(choices)):
        if is_choice(choices[i]):
            choice_letter = choices[i][0]
            choice_string = extract_choice_string(i + 1, choices)
            choices_dict[choice_letter] = choice_string

    return choices_dict


def choose_random_answer(question_dict: Dict[str, str]) -> str:
    random_key = random.choice(list(question_dict.keys()))
    random_answer = question_dict[random_key]
    return f"{random_key}) {random_answer}"


def parse_mc_question(question: str) -> Union[bool, str]:
    q1_found = False
    choices_dict = {}
    question_split = question.split(" ")
    for i, word in enumerate(question_split):
        word = question_split[i]
        if word.lower() == "a)":
            choices_dict = parse_choices(question, i)
            q1_found = True
    if q1_found:
        return choose_random_answer(choices_dict)
    return False

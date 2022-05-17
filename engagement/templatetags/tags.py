from django import template
import json
import unidecode
from engagement.models import RangedAnswer, Question, Section

register = template.Library()

@register.simple_tag
def get_key(dictionary, key):
    return dictionary[str(key)]

@register.filter
def proper_order(obj):
    obj2 = obj.order_by('order')
    return obj2

@register.filter
def return_dict_values(source_dict):
    list_to_return = []
    for key, value in source_dict.items():
        list_to_return.append(value)

    return list_to_return

@register.filter
def ordered_by_key(source_dict):
    result_dict = {k: v for k, v in sorted(source_dict.items(), key=lambda item: int(item[0]))}
    return result_dict.items()

@register.filter
def ordered_by_key_return_dict(source_dict):
    result_dict = {k: v for k, v in sorted(source_dict.items(), key=lambda item: int(item[0]))}
    return result_dict

@register.filter
def ordered_by_key_return_value_string(source_dict):
    result_dict = {k: v for k, v in sorted(source_dict.items(), key=lambda item: int(item[0]))}
    result_list = [v for v in result_dict.values()]
    result_string = ' ,'
    return result_string.join(result_list)


@register.filter
def to_decimal_point(number):
    number = str(number).replace(",", ".")
    return str(number)


@register.filter
def ordered_by_order(qs):
    return qs.order_by('order')


@register.filter
def to_dict(string):

    dict_to_return = json.loads(string)
    return dict_to_return

@register.simple_tag
def answer_to_question(answers, question):
    return answers.get(str(question))

@register.simple_tag
def get_answer_description(dictionary, key):

    return dictionary.get(str(key))

@register.filter
def no_spaces(word_string):

    return word_string.replace(' ','').replace('-','').lower()


@register.filter
def up_to_divider(section_name, divider):
    return section_name.split(divider)[0].strip()


@register.simple_tag
def get_answer_multiplied_by_weight(question, answer, sections):
    for section in sections:
        questions = section.question.all()
        for q in questions:
            if q.id == int(question):
                return int(q.weight * answer)

@register.simple_tag
def check_if_ranged(question_number, answer):
    all_ranges = RangedAnswer.objects.all()
    question_ids = []
    for rng in all_ranges:
        questions = rng.question.all()
        for question in questions:
            question_ids.append(question.id)

        if int(question_number) in question_ids:
            try:
                return rng.strings[str(answer)]
            except:
                return ''
            

@register.filter
def total_sum(answers_dict):

    total = 0

    count_of_zeroes = 0

    for question, answer in answers_dict.items():
        if answer == '':
            answer = 0
        total = total + (int(answer) * Question.objects.get(id=int(question)).weight)
        if int(answer) == 0:
            count_of_zeroes += 1


    if count_of_zeroes > 9:
        return "N/A"    
    else:
        try:
            return round(float(total / (len(answers_dict.keys()) - count_of_zeroes)), 2)
        except:
            return 0


@register.filter
def section_sum(answers_dict, section_id):

    total = 0
    questions_ids = []
    count_of_zeroes = 0

    section = Section.objects.get(id=section_id)
    questions_in_section = section.question.all()

    for q in questions_in_section:
        questions_ids.append(q.id)

    for question, answer in answers_dict.items():
        if answer == '':
            answer = 0
        if int(question) in questions_ids:
            total = total + (int(answer) * Question.objects.get(id=int(question)).weight)
            if int(answer) == 0:
                count_of_zeroes += 1

    if count_of_zeroes > 2:
        return "N/A"
    else:
        return round(float((total / (len(questions_ids) - count_of_zeroes))), 2)


@register.filter
def get_list_of_odd_sections(section_set):
    list_of_sections = []
    for section in section_set:
        list_of_sections.append(section.section_name.split(' - ')[0].lower())

    return list_of_sections[1::2]


@register.filter
def get_list_of_even_sections(section_set):
    list_of_sections = []
    for section in section_set:
        list_of_sections.append(section.section_name.split(' - ')[0].lower())

    return list_of_sections[0::2]

@register.simple_tag
def make_empty_tds(count_of_answers, total_needed_answers):

    tds_to_make = total_needed_answers - count_of_answers

    return tds_to_make * str('<td></td>')
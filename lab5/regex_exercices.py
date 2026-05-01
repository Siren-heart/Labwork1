# Practice 5: solutions for regex.md exercises

import re


def match_a_followed_by_zero_or_more_bs(text):
    return bool(re.fullmatch(r"ab*", text))


def match_a_followed_by_two_or_three_bs(text):
    return bool(re.fullmatch(r"ab{2,3}", text))


def find_lowercase_with_underscore(text):
    return re.findall(r"\b[a-z]+_[a-z]+\b", text)


def find_upper_then_lower(text):
    return re.findall(r"\b[A-Z][a-z]+\b", text)


def match_a_anything_ending_b(text):
    return bool(re.fullmatch(r"a.*b", text))


def replace_space_comma_dot(text):
    return re.sub(r"[ ,.]+", ":", text)


def snake_to_camel(text):
    return re.sub(r"_([a-zA-Z])", lambda match: match.group(1).upper(), text)


def split_at_uppercase(text):
    parts = re.split(r"(?=[A-Z])", text)
    return [part for part in parts if part]


def insert_spaces_before_capitals(text):
    return re.sub(r"(?<!^)([A-Z])", r" \1", text)


def camel_to_snake(text):
    return re.sub(r"(?<!^)([A-Z])", r"_\1", text).lower()


def main():
    print("1.", match_a_followed_by_zero_or_more_bs("abbb"))
    print("2.", match_a_followed_by_two_or_three_bs("abb"))
    print("3.", find_lowercase_with_underscore("first_value secondValue third_name"))
    print("4.", find_upper_then_lower("Alice and Bob visited NASA"))
    print("5.", match_a_anything_ending_b("axxxb"))
    print("6.", replace_space_comma_dot("one, two. three four"))
    print("7.", snake_to_camel("my_variable_name"))
    print("8.", split_at_uppercase("SplitThisCamelCase"))
    print("9.", insert_spaces_before_capitals("InsertSpacesBetweenWords"))
    print("10.", camel_to_snake("convertThisString"))


if __name__ == "__main__":
    main()

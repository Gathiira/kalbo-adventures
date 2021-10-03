import os
import random
import string


def split_text(txt):
    splitted = os.path.splitext(txt)
    return splitted


def random_string_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def generate_unique_reference_per_model(model, size=5):
    reference_number = random_string_generator(size=size)

    Klass = model

    qs_exists = Klass.objects.filter(
        reference_number=reference_number).exists()
    if qs_exists:
        return generate_unique_reference_per_model(model, size=size)
    return reference_number


def find_duplicates_in_dict(list_dict, required_key):
    final_list = []
    for dct in list_dict:
        if dct[required_key] not in final_list:
            final_list.append(dct[required_key])
        else:
            return True, 'duplicates'
    return False, final_list
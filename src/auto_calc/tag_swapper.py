import logging
from classes import TagAndSwap, TagValue

logger = logging.getLogger('tag_swapper')


def tag_swapper(job_data: dict, tag_and_swap : dict) -> dict:
    tag_swapped = {}
    job_data_tag = job_data.keys()
    for tag_name, tag_value in tag_and_swap.items():
        if tag_name in job_data_tag:
            if __tag_value_evaluator(job_data.get(tag_name, ''), tag_value):
                value_transformed = __value_transformer(job_data[tag_value.new], tag_value)
                if 'R' in job_data[tag_value.new].keys():
                    match job_data['DO']:
                        case 'R':
                            value = {'R' : value_transformed, 'L' : ''}
                        case 'L':
                            value = {'R' : '', 'L' : value_transformed}
                        case _:
                            value = {'R' : value_transformed, 'L' : value_transformed}
                    tag_swapped[tag_name] = value
                else:
                    tag_swapped[tag_name] = value_transformed
    return tag_swapped


def __tag_value_evaluator(tag_value: any, tag_swap: TagValue) -> bool:
    try:
        match tag_swap.sign:
            case '==':
                if __compare_values(tag_swap.compare_value, tag_value, __equal):
                    return True
            case '>':
                if __compare_values(tag_swap.compare_value, tag_value, __greater):
                    return True
            case '<':
                if __compare_values(tag_swap.compare_value, tag_value, __less):
                    return True
            case '<=':
                if __compare_values(tag_swap.compare_value, tag_value, __greater_equal):
                    return True
            case '>=':
                if __compare_values(tag_swap.compare_value, tag_value, __less_equal):
                    return True
            case 'c':
                if __compare_values(tag_swap.compare_value, tag_value, __contains):
                    return True
        return False
    except Exception as error:
        logger.error(f'Error in {error}')
        raise error    


def __compare_values(compare_value: any, tag_value: any, operator_function: function) -> bool:
    try:
        if tag_value.isinstance(dict):
            for value in tag_value.values():
                if not operator_function(compare_value, value) and len(value) > 0:
                    return False
        else: 
            if operator_function(compare_value, value) and len(value) > 0:
                return True
        return True
    except Exception as error:
        logger.error(f'Error in compare_values {error}')
        raise error


def __equal(compare_value: any, tag_value: any) -> bool:
    if compare_value == tag_value:
        return True
    return False


def __greater(compare_value: any, tag_value: any) -> bool:
    if compare_value < tag_value:
        return True
    return False


def __less(compare_value: any, tag_value: any) -> bool:
    if compare_value > tag_value:
        return True
    return False


def __greater_equal(compare_value: any, tag_value: any) -> bool:
    if compare_value <= tag_value:
        return True
    return False


def __less_equal(compare_value: any, tag_value: any) -> bool:
    if compare_value <= tag_value:
        return True
    return False


def __contains(compare_value: any, tag_value: any) -> bool:
    if tag_value.isinstance(dict):
        for value in tag_value.values():
            if len(compare_value) == len(value):
                if not __compare_by_char(compare_value, tag_value):
                    return False
            if len(compare_value) < len(value):
                if not compare_value in tag_value:
                    return False
        return True             
    if len(compare_value) == len(tag_value):
        if __compare_by_char(compare_value, tag_value):
            return True
        return False
    if len(compare_value) < len(tag_value):
        if compare_value in tag_value:
            return True
        return False    


def __compare_by_char(compare_value: any, value: any) -> bool:
    compared_value = ''
    for compare in compare_value:
        if compare == value[compare_value.index(compare)]:
            compared_value += compare
        if compare == '*':
            compared_value += value[compare_value.index(compare)]
    if len(value) == len(compared_value):
        return True
    return False    


def __value_transformer(original_value: any, tag_swap: TagValue) -> any:
    pass


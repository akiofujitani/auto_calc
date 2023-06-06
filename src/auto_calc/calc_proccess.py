import math, logging
from classes import *


logger = logging.getLogger('calc_proccess')


def set_side_value(side: str, value: any) -> dict:
    '''
    Match job side and return dictionary
    '''
    match side:
        case 'R':
            return {'R' : value, 'L' : ''}
        case 'L':
            return {'R' : '', 'L' : value}
        case _:
            return {'R': value, 'L': value}


def return_side_value(side: str, value: dict) -> dict:
    '''
    Match job side and return unique value
    '''
    match side:
        case 'R':
            return value.get('R', '')
        case 'L':
            return value.get('L', '')
        case _:
            return value.get('R', '')


def corrlen_corrector(job_data: dict, parameters: Parameters, design_list: DesignList) -> dict:
    '''
    CORRLEN corrector, put to work only if CORRLEN is not set on progressive lenses
    '''
    try:
        design = design_list.return_corrlen(return_side_value(job_data.get('DO', ''), job_data.get('LNAM', '')))
        corrlen_value = return_side_value(job_data.get('DO', ''), job_data.get('CORRLEN', {'R': '', 'L': ''}))
        if design and corrlen_value:
            if design.design_type == 'SV':
                return
            elif corrlen_value >= design.corr_len[0] and corrlen_value <= design.corr_len[len(design.corr_len) - 1]:
                return
            else:
                ocht = return_side_value(job_data.get('DO', ''), job_data.get('OCHT', {'R': '', 'L': ''}))
                if ocht:
                    corrlen = parameters.return_corrlen(ocht) - design.corr_len_translator
                    if corrlen in design.corr_len:
                        return set_side_value(job_data.get('DO', ''), corrlen)
                    else:
                        return set_side_value(job_data.get('DO', ''), design.corr_len[0])
    except Exception as error:
        logger.error(f'corrlen_corrector error {error}')
        raise error


def lnam_swapper(lnam_list: list, lnam: any) -> str:
    '''
    Get LNAM, compare and swap if LNAM matches values in LNAM list
    '''
    original_lnam = str(lnam)
    for key, swap_lnam in lnam_list:
        new_lnam = []
        for char in swap_lnam['old']:
            if not char == '?':
                if original_lnam[key] == char:
                    new_lnam = new_lnam + char
            else:
                new_lnam = new_lnam + char
        if len(new_lnam) == len(original_lnam):
            return new_lnam
    return

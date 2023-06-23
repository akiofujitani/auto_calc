import logging
from classes import *

logger = logging.getLogger('calc_proccess')




'''
======================================================================================================

        Support Functions       Support Functions       Support Functions       Support Functions

======================================================================================================
''' 


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


def side_filler(tag_name: str, tag_rl: dict, do: str) -> dict:
    '''
    Fill side values if empty
    '''
    if do == 'B':
        return tag_rl
    else:
        temp_tag = {}
        other_side = 'R' if do == 'L' else 'L'
        temp_tag[do] = tag_rl[do]
        if tag_name == 'AX' and not tag_rl[do] == 0 or tag_rl[do] == 90:
            temp_tag[other_side] = abs(tag_rl[do] - 180)
        else:
            temp_tag[other_side] = tag_rl[do]
        return temp_tag


def fill_default(parameter_value: any, tag_value:any) -> any:
    '''
    Fill empty values with default ones from parameter object if not present in tag
    '''
    if isinstance(tag_value, dict):
        updated_tag_value = {}
        if 'R' in tag_value.keys():
            for side, value in tag_value.items():
                other_side = 'R' if side == 'L' else 'R'
                if not value:
                    if tag_value[other_side]:
                        updated_tag_value[side] = tag_value[other_side]
                    else:
                        updated_tag_value[side] = parameter_value
                else:
                    updated_tag_value[side] = value
            logger.debug(updated_tag_value)
            return updated_tag_value
    else:
        if not tag_value:
            return parameter_value
        else:
            return tag_value


'''
======================================================================================================

        Data Proccessing       Data Proccessing       Data Proccessing       Data Proccessing

======================================================================================================
''' 


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



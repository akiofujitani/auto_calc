import math, logging
from classes import *
from collections import namedtuple

logger = logging.getLogger('calc_proccess')


'''
======================================================================================================

        Support Types       Support Types       Support Types       Support Types       Support Types       

======================================================================================================
''' 

Tag_RL = namedtuple('Tag_RL', 'R L')
Sag_Diop = namedtuple('Sag_Diop', 'sag diop add_minus')

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


def conversion_factor(refraction_index: float) -> float:
    '''
    Conversion factor to calculate diopator of given refraction index
    '''
    try:
        conversion_factor = 0.530 / (refraction_index - 1)
        logger.debug(conversion_factor)
        return conversion_factor
    except Exception as error:
        logger.error(f'conversion_factor error {error}')
        raise error


def diopter_on_ax(sph: float, cyl: float, ax: int, direction: float) -> float:
    '''
    Return the absolute diopter on the set directorion (in angle)
    '''
    if not ax:
        ax = 0
    if direction > 180:
        direction = direction - 180
    diopter_value = (math.sin(math.radians(abs(ax - direction))) + cyl) + sph
    logger.debug(diopter_value)
    return diopter_value


def one_diop_sag(radius: int) -> float:
    '''
    Calculates the one diopter on the 1.530 refraction index on the given radius
    '''
    try:
        one_diop_in_rad = 530 - (math.sqrt(280900 - ((radius / 100) ** 2)))
        logger.debug(one_diop_in_rad)
        return one_diop_in_rad
    except Exception as error:
        logger.error(f'One_diop_sag {error}')
        raise error


def to_string(value: any) -> str:
    return str(value)


def to_float(value: any) -> float:
    return float(value)


def to_int(value: any) -> int:
    return int(float(value))


def fill_zero_mirror(tag_rl: dict, to_type=to_string, angle_type: bool=False) -> dict:
    '''
    Fill with 0 "zero" or mirroring value from other side.    
    '''
    filled_tag = {}
    for side, tag_value in tag_rl.items():
        other_side = 'R' if side == 'L' else 'L'
        if not tag_value and tag_rl[other_side]:
            filled_tag[side] = to_type(tag_rl[other_side] if angle_type == False else angle_mirror(tag_rl[other_side]))
        elif tag_value:
            filled_tag[side] = to_type(tag_rl[side])
        else:
            filled_tag[side] = 0
        logger.debug(filled_tag)
    return filled_tag


def angle_mirror(angle: float) -> float:
    '''
    special function for mirroring angle value
    '''
    angle_value = float(angle)
    if angle_value == 180 or angle_value == 0 or angle_value == 90 or angle_value == 270 or angle_value == 360:
        return angle
    elif angle_value < 180:
        return str(abs(angle_value - 180))
    else:
        return str(360 - (angle_value - 180))


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
    if tag_value.isinstance(dict):
        updated_tag_value = {}
        if 'R' in tag_value.keys():
            for side, value in tag_value.items():
                other_side = 'R' if side == 'L' else 'R'
                if not value:
                    if tag_value[other_side]:
                        updated_tag_value[side] = tag_value[other_side]
                    else:
                        updated_tag_value[side] = parameter_value
            logger.debug(updated_tag_value)
            return updated_tag_value
    else:
        if not tag_value:
            return parameter_value
        else:
            return tag_value


def return_thickness_on_diop(diopter: float, thickness_list: dict) -> dict:
    rounded_diop = f'{round(diopter * 4) / 4}'
    thickness_diopter_list = [float(diopter) for diopter in thickness_list.keys()]
    if rounded_diop < min(*thickness_diopter_list):
        return thickness_list[str(min(*thickness_diopter_list))]
    if rounded_diop > max(*thickness_diopter_list):
        return thickness_list[str(max(*thickness_diopter_list))]
    return thickness_list[str(f'{rounded_diop:0.2f}')]


def return_min_thick(thickness_list: dict, blank: Blank, highest_diop: float) -> float:
    thickness_values = return_thickness_on_diop(highest_diop, thickness_list)
    ct_et_values = thickness_values[blank.index_type]
    return float(ct_et_values['CT']) if ct_et_values['CT'] else float(ct_et_values['ET'])


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


def thickness_per_angle(sph: float, cyl: float, ax: int, add: float, add_perc: float, one_diop_in_index: float, shape: list) -> dict:
    '''
    Calculate the sag (thickness) for the given diopter in each angle of the shape
    '''
    angle = 0
    angle_step = len(shape) / 360
    angle_sag = {}
    angle_diop = {}
    angle_add_minus = {}

    add_converted = add * add_perc
    for radius in shape:
        angle += angle_step
        one_diop_thickness = one_diop_sag(radius)
        diopter_value = diopter_on_ax(sph, cyl, ax, angle) * one_diop_in_index
        angle_sag_value = one_diop_thickness * diopter_value
        add_minus_calc = one_diop_thickness * add_converted * one_diop_in_index
        angle_sag[angle] = angle_sag_value
        angle_diop[angle] = diopter_value
        angle_add_minus[angle] = add_minus_calc
        logger.debug(f'{angle_sag_value} {diopter_value} {add_minus_calc}')
    return Sag_Diop(angle_sag, angle_diop, angle_add_minus)


def thickness_equalizer(job_data: dict, shape_optical_center: dict, blank: Blank, thickness_list: FrameThickness, parameters: Parameters) -> dict:
    '''
    Calculate and equalizer the thickness based on the job data and shape optical centered.
    '''
    diopter_conversion_factor = conversion_factor(blank.index)

    sph = Tag_RL(fill_zero_mirror(job_data.get('SPH', {'R': '', 'L' : ''}), to_float))
    cyl = Tag_RL(fill_zero_mirror(job_data.get('CYL', {'R': '', 'L' : ''}), to_float))
    ax = Tag_RL(fill_zero_mirror(job_data.get('AX', {'R': '', 'L' : ''}), to_int))
    add = Tag_RL(fill_zero_mirror(job_data.get('ADD', {'R': '', 'L' : ''}), to_float))
    add_perc = parameters.add_percentage #<parameter> ADD_PERCENTAGE

    lens_calculation = {}

    # Calculate base thickness for each side
    sides = ('R', 'L')
    for side in sides:
        if cyl.__getattribute__(side) == 0:
            ax_value = 0
        else:
            ax_value = ax.__getattribute__(side)
        sag_diop = thickness_per_angle(sph.__getattribute__(side), 
                                       cyl.__getattribute__(side),
                                       ax_value,
                                       add.__getattribute__(side),
                                       add_perc,
                                       diopter_conversion_factor,
                                       shape_optical_center.get(side))
        
        '''
        Function to process the diopter to be sent for minimum thickness.
            Before send:
                if SPH < 0 and CYL <= 0:
                    Send highest sag diop
                if SPH >= 0:
                    Send highest diop
        >> Minimum thickes get

        
        Function Post processing of minimum thickness based on the following rules
            Positive with ax between 60 and 120 < Can be transformed in parameter
            Change minimum thicknes if it is lower than <parameter> "MIN_THICK_POS_AX90" and SPH value is higher than <parameter> "MIN_SPH" 

        Funciont Calculate all the thickness with the minimum thickess included
            Diopter type selection ??? Don't remember
        '''

        pass



    pass


if __name__ == '__main__':
    tag_value = {'R': 1.00, 'L': ''}
    do = 'B'
    temp = fill_zero_mirror(tag_value, to_float)
    test_tag = Tag_RL(temp['R'], temp['L'])
    print(test_tag.__getattribute__('R'))
    print(test_tag.__getattribute__('L'))
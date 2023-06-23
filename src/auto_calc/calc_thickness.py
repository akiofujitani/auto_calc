import logging, math
from collections import namedtuple
from classes import *

logger = logging.getLogger('calc_thickness')


'''
======================================================================================================

        Support Types       Support Types       Support Types       Support Types       Support Types       

======================================================================================================
''' 

Tag_RL = namedtuple('Tag_RL', 'R L')
Sag_Diop = namedtuple('Sag_Diop', 'sag diop')


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


def thickness_per_angle(sph: float, cyl: float, ax: int, add: float, add_perc: float, one_diop_in_index: float, shape: list) -> dict:
    '''
    Calculate the sag (thickness) for the given diopter in each angle of the shape
    '''
    angle = 0
    angle_step = len(shape) / 360
    sag_diopt = {}

    add_converted = add * add_perc
    for radius in shape:
        angle += angle_step
        one_diop_thickness = one_diop_sag(radius)
        add_plus = 0
        diopter_value = diopter_on_ax(sph, cyl, ax, angle) * one_diop_in_index
        if angle > 180 and angle < 360 and add > 0.00:
            add_plus = (add_converted * math.sin(math.radians(angle))) * one_diop_in_index
        angle_sag_value = one_diop_thickness * (diopter_value - add_plus)
        sag_diopt[angle] = Sag_Diop(diopter_value, angle_sag_value)
        logger.debug(f'{angle_sag_value} {diopter_value}')
    return sag_diopt


def get_highest_diopter(sph: float, cyl: float, sag_diop: dict[Sag_Diop]) -> float:
    '''
    Evaluate diopter and return the highest one
    '''
    if sph < 0 and cyl <= 0:
        return min(*[sag.diop for sag in sag_diop.values()])
    elif sph >= 0:
        return max(*[sag.diop for sag in sag_diop.values()])


def return_thickness_on_diop(diopter: float, thickness_list: dict) -> dict:
    '''
    Get diopter round in 0.25 and return its equivalent thickness
    '''
    rounded_diop = f'{round(diopter * 4) / 4}'
    logger.debug(f'Rounded diopter {rounded_diop}')
    thickness_diopter_list = [float(diopter) for diopter in thickness_list.keys()]
    if rounded_diop < min(*thickness_diopter_list):
        return thickness_list[str(min(*thickness_diopter_list))]
    if rounded_diop > max(*thickness_diopter_list):
        return thickness_list[str(max(*thickness_diopter_list))]
    return thickness_list[str(f'{rounded_diop:0.2f}')]


def return_min_thick(thickness_list: dict, blank: Blank, highest_diop: float) -> float:
    ''' 
     From thickness list and diopter return the base diopter
     Then select the thickness based on the blank index
    '''
    thickness_values = return_thickness_on_diop(highest_diop, thickness_list)
    return thickness_values[blank.index_type]


def calc_edge_thickness(minimum_thickness: dict, ax: int, min_sph_value: float, thick_on_vertical_ax: float, sag_per_angle: dict[Sag_Diop]) -> float and list:
    '''
    Calculate the minimun thickness for center and edge
    '''
    max_diop = max(*[sag.diop for sag in sag_per_angle.values()])
    logger.debug(f'Max diopter {max_diop}')
    edge_thick = []
    if minimum_thickness.get('CT'):
        min_thick = minimum_thickness.get('CT')
        center_thick = minimum_thickness.get('CT')
    else:
        if ax >= 60 and ax <= 120 and max_diop > min_sph_value and minimum_thickness.get('ET') < thick_on_vertical_ax:
            min_thick = thick_on_vertical_ax
        else:
            min_thick = minimum_thickness.get('ET')
        center_thick = min_thick + max(*[sag.sag for sag in sag_per_angle.values()]) 
    for sag in sag_per_angle.values():
        edge_thick.append(sag.sag + min_thick)
        logger.debug(f'{center_thick} {edge_thick}')
        logger.info(f'Center and edge thickness done')
    return center_thick, edge_thick

'''
============================================================================================================

        Thickness Equalizer       Thickness Equalizer       Thickness Equalizer       Thickness Equalizer              

============================================================================================================
''' 


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
        high_diopter = get_highest_diopter(sph.__getattribute__(side), cyl.__getattribute__(side), sag_diop)
        min_thick = return_min_thick(thickness_list, blank, high_diopter)
        center_thick, edge_thick = calc_edge_thickness(min_thick, ax_value, parameters.thick_on_vertical_ax, sag_diop)


        '''
        Get average thicknes on each quadrant (top, down, in, out)
        Must recognize side for "in" and "out" values
        Create namedtuple for Quadrant values 
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
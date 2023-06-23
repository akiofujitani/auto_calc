'''
Build file handler and frame resizer/rebuilder.
'''
import math, logging
from collections import namedtuple
from PIL import Image, ImageDraw

logger = logging.getLogger('vca_handler_frame')

Point = namedtuple('Point', 'x y')
Frame_Box = namedtuple('Frame_Box', 'hbox vbox')


def __volpe_points_corrector(shape_data_points):
    logger.debug('correcting number of points')
    temp_shape_data = [int(value) for value in shape_data_points]
    if len(shape_data_points) == 359:
        last_point = round((temp_shape_data[0] + temp_shape_data[358]) / 2)
        temp_shape_data.append(last_point)
        return temp_shape_data
    return temp_shape_data


def __shape_to_xy(shape_points):
    try:
        x_y_dict_list = []
        angle_unit = 360 / len(shape_points)
        angle_value = angle_unit
        for radius in shape_points:
            x_value = math.cos(math.radians(angle_value)) * int(radius)
            y_value = math.sin(math.radians(angle_value)) * int(radius)
            x_y_dict_list.append(Point(x_value, y_value))
            angle_value += angle_unit
    except Exception as error:
        logger.error(f'Could not convert frame values duue {error}')
        raise error
    logger.info('Shape to X Y coordinates')
    return x_y_dict_list


def new_resize(hbox: int, vbox: int, shape_in_x_y: list):
    actual_frame_size = __xy_shape_size(shape_in_x_y)
    size_diff = Frame_Box(hbox - actual_frame_size.x, vbox - actual_frame_size.y)
    resized_vector = []
    for i in range(shape_in_x_y):
        x_vector = shape_in_x_y[i].x * size_diff.x * math.cos(i)
        y_vector = shape_in_x_y[i].y * size_diff.y * math.sin(i)
        resized_vector[i] = math.atan(x_vector, y_vector)
    draw_points(resized_vector)
    return resized_vector    


def __xy_shape_size(x_y_dict_list):
    angle_x_list = [angle.x for angle in x_y_dict_list]
    angle_y_list = [angle.y for angle in x_y_dict_list]
    frame_size = Frame_Box(abs(min(angle_x_list)) + abs(max(angle_x_list)), abs(min(angle_y_list)) + abs(max(angle_y_list)))
    logger.debug(f'{frame_size.hbox} {frame_size.vbox}')
    return frame_size


def shape_xy_resize(x_y_dict_list: list, hbox: str, vbox: str):
    frame_size = __xy_shape_size(x_y_dict_list)
    try:
        hbox = int(hbox)
        vbox = int(vbox)
    except TypeError:
        raise Exception('Type error')
    hbox = frame_size.hbox if hbox == 0 else int(hbox) * 100
    vbox = frame_size.vbox if vbox == 0 else int(vbox) * 100
    logger.debug(f'{hbox} {vbox}')

    x_frame_diff = (frame_size.hbox - hbox) * -1
    y_frame_diff = (frame_size.vbox - vbox) * -1
    x_scale_factor = (frame_size.hbox + x_frame_diff) / frame_size.hbox
    y_scale_factor = (frame_size.vbox + y_frame_diff) / frame_size.vbox
    shape_xy_resized = []
    for x_y_value in x_y_dict_list:
        shape_xy_resized.append(Point(x_y_value.x * x_scale_factor, x_y_value.y * y_scale_factor))
    logger.info('Shape resized')
    return shape_xy_resized


def __atan_to_360(y_x_values: Point) -> math.radians:
    angle_radians = math.atan(y_x_values.y / y_x_values.x)
    
    x = y_x_values.x
    y = y_x_values.y
    if x > 0 and y > 0:
        angle_converter = 0
    if x < 0 and y > 0 or x < 0 and y < 0:
        angle_converter = math.pi
    if x > 0 and y < 0:
        angle_converter = math.pi * 2
    return angle_radians + angle_converter


def __cycle_values(value, reference_cycle):
    if value > reference_cycle:
        for _ in range(round(value / reference_cycle)):
            value = value - reference_cycle
        return value
    elif value < 0:
        if round(abs(value) / reference_cycle) > 0:
            for _ in range(round(abs(value) / reference_cycle)):
                value = value - reference_cycle
            return value
        else:
            return reference_cycle - abs(value)
    elif value == reference_cycle:
        return 0
    else:
        return value


def __get_current_angles(shape_xy_resized: list) -> list:
    angle_values = []
    for xy_values in shape_xy_resized:
        angle_values.append(__atan_to_360(xy_values))
    return angle_values


def __get_closest_angles(angle: float, angle_values: list) -> int:
    '''
    Get the closest point values to calculate the current angle
    '''
    radian_angle = math.radians(angle)
    logger.debug(f'Angle in radian {radian_angle}')
    counter_minus = ''
    counter_plus = ''
    for counter, value in enumerate(angle_values):
        logger.debug(value * 180 / math.pi)
        if value < radian_angle:
            counter_minus = counter
        else:
            counter_plus = counter
            if not counter_minus == '':
                return counter_minus, counter_plus


def __get_closest_angles_plus(angle: float, angle_values: list, number_of_values: int=5) -> list:
    '''
    Get the closest point values to calculate the current angle
    '''
    radian_angle = math.radians(angle)
    logger.debug(f'Angle in radian {radian_angle}')
    counter_minus = ''
    counter_plus = ''
    for counter, value in enumerate(angle_values):
        logger.debug(value * 180 / math.pi)
        if value < radian_angle:
            counter_minus = counter
        else:
            counter_plus = counter
            if not counter_minus == None:
                break
    return_list = [counter_minus, counter_plus]
    for i in range(number_of_values - 2):
        return_list.append((counter_plus + i + 1) % len(angle_values))
    return return_list



def radius_recalc(shape_xy_resized: list, angle_count_convert: int=360) -> dict:
    shape_in_angle = {}
    angle = 1
    shape_xy_angle = __get_current_angles(shape_xy_resized)
    while len(shape_in_angle.keys()) < angle_count_convert:
        low, high = __get_closest_angles(angle, shape_xy_angle)
        if angle == 360:
            print(angle)
        x_y_values_a = shape_xy_resized[low]
        x_y_values_b = shape_xy_resized[high]
        angle_a = __atan_to_360(x_y_values_a)
        angle_b = __atan_to_360(x_y_values_b)

        length_a = math.sqrt(x_y_values_a.x ** 2 + x_y_values_a.y ** 2)
        length_b = math.sqrt(x_y_values_b.x** 2 + x_y_values_b.y ** 2)
        length_a_to_b = math.sqrt((x_y_values_a.x - x_y_values_b.x) ** 2 + (x_y_values_a.y - x_y_values_b.y) ** 2)
        angle_diff = abs(abs(angle_a) - abs(angle_b))
        length_a_to_b = math.sqrt((length_a ** 2 + length_b ** 2) - (2 * length_a * length_b) * math.cos(angle_diff))
        # acos_value_1 = length_a ** 2 + length_a_to_b ** 2 - length_b ** 2
        # acos_value_2 = length_a * length_a_to_b * 2
        # angle_a_to_b = math.radians(math.acos(acos_value_1 / acos_value_2))
        angle_resize_diff_a = abs(abs(math.degrees(angle_a)) - abs(angle))
        angle_resize_diff_b = abs(abs(math.degrees(angle_b)) - abs(angle))
        lengh_angle_diff = ''
        length = ''
        if angle_resize_diff_a == 0:
            length = length_b
        elif angle_resize_diff_b == 0:
            length = length_a
        else: 
            lengh_angle_diff = math.sqrt((length_a ** 2 + length_b ** 2) - 2 * length_a * length_b * math.cos(math.radians(angle_resize_diff_a)))
            length_factor = lengh_angle_diff / length_a_to_b
            if length_a > length_b:
                lenght_diff = length_a - length_b
                length = length_a + (lenght_diff * length_factor)
            else:
                lenght_diff = length_b - length_a
                length = length_b + (lenght_diff * length_factor)
        shape_in_angle[angle] = int(round(length))
        angle = angle + 1 if angle < 360 else 0
    return shape_in_angle


def shape_mirror(shape_in_radius=dict) -> dict:
    mirrored_shape = {}
    first_angle = shape_in_radius.keys()[0]
    full_turn = len(shape_in_radius)
    half_turn = full_turn / 2

    for angle, radius in shape_in_radius.items():
        mirrored_radius = 0
        if angle >= first_angle and angle <= half_turn:
            mirrored_radius = shape_in_radius[half_turn - angle]
        else:
            mirrored_radius = shape_in_radius[full_turn - (half_turn - angle)]
        mirrored_shape[angle] = mirrored_radius
        logger.debug('Shape mirrored')
    return mirrored_shape


def frame_resize(shape_data=list, vbox=int, hbox=int) -> dict:
    shape_data_corrected = __volpe_points_corrector(shape_data)
    shape_to_xy = __shape_to_xy(shape_data_corrected)
    frame_size = __xy_shape_size(shape_to_xy)
    if abs(frame_size.hbox - int(hbox)) < 1.0 and abs(frame_size.vbox - int(vbox)) < 1.0 and len(shape_data_corrected) == 360:
        shape_in_radius = {}
        for angle, radius in enumerate(shape_data_corrected, 1):
            shape_in_radius[angle] = radius
        return shape_in_radius
    shape_resized_xy = shape_xy_resize(shape_to_xy, vbox, hbox)    
    shape_in_radius = radius_recalc(shape_resized_xy)
    return shape_in_radius


def frame_recenter(shape_data: list, side: str, ipd: float, ocht: float, dbl: float) -> dict:
    shape_to_xy = __shape_to_xy(shape_data)
    frame_size = __xy_shape_size(shape_to_xy)
    logger.debug(f'Calculating diff {frame_size.hbox} x {frame_size.vbox}')
    horizontal_center_diff = (frame_size.hbox / 2) - (float(ipd) * 100) - ((float(dbl) * 100) / 2)
    vertical_center_diff = (float(ocht) * 100) - (frame_size.vbox / 2)
    if side == 'L':
        horizontal_center_diff = horizontal_center_diff * -1
    shape_center_repositioned = xy_center_pos(shape_to_xy, horizontal_center_diff, vertical_center_diff)
    shape_in_radius = radius_recalc(shape_center_repositioned)
    return shape_in_radius


def xy_center_pos(shape_in_xy: list, horizontal_center_diff: float, vertical_center_diff: float) -> list:
    center_reposition = []
    for point in shape_in_xy:
        center_reposition.append(Point(point.x - horizontal_center_diff, point.y - vertical_center_diff))
    return center_reposition


def resize_points(radius_list: list, hbox: float, vbox: float) -> dict:
    xy_shape = __shape_to_xy(radius_list)
    actual_shape_size = __xy_shape_size(xy_shape)
    x_factor = float(hbox) / actual_shape_size.hbox
    y_factor = float(vbox) / actual_shape_size.vbox

    angle_step = 360 / len(radius_list)
    resized_shape = {}
    angle = 0
    # cos_zero = math.cos(0)
    # sin_zero = math.sin(0)
    for radius in radius_list:
        x_pre_resized = float(radius) * x_factor
        y_pre_resized = float(radius) * y_factor
        cos_angle = math.cos(math.radians(angle))
        sin_angle = math.sin(math.radians(angle))
        # x_diff = x_pre_resized * cos_angle * 100
        # y_diff = y_pre_resized * sin_angle * 100
        # x_resized = x_diff * cos_zero - y_diff * sin_zero
        # y_resized = x_diff * sin_zero + y_diff * cos_zero
        x_resized = x_pre_resized * cos_angle * 100
        y_resized = y_pre_resized * sin_angle * 100
        new_angle = math.atan2(y_resized, x_resized)
        new_radius = round(math.sqrt((x_resized ** 2) + (y_resized ** 2)))
        logger.debug(f'{math.degrees(new_angle)} {new_radius}')
        resized_shape[new_angle] = new_radius
        angle += angle_step
    
    return resized_shape


def draw_points(points_dict: list, width: int=600, height: int=400, scale: int=15) -> None:
    logger.debug('Draw shape points')
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    center_x = width/ 2
    center_y = height / 2
    point_xy = __shape_to_xy(points_dict)
    coordinates = [(center_x + (points.x / scale), center_y - (points.y / scale)) for points in point_xy]
    draw.point(coordinates, fill='black')
    image.show()
    logger.debug('Done')
    return



'''
==============================================================================================================================================

            NOTES AND TESTS             NOTES AND TESTS             NOTES AND TESTS             NOTES AND TESTS             NOTES AND TESTS

==============================================================================================================================================

Arc between 3 points

Center of arc is equall between the points

(X-Xa)^2+(Y-Ya)^2 = (X-Xb)^2+(Y-Yb)^2 = (X-Xc)^2+(Y-Yc)^2

Subtracting the first member from the second and the third, we get after regrouping:

2(Xa-Xb) X + 2(Ya-Yb) Y + Xb^2+Yb^2-Xa^2-Ya^2 = 0
2(Xa-Xc) X + 2(Ya-Yc) Y + Xc^2+Yc^2-Xa^2-Ya^2 = 0

This linear system of two equations in two unknowns is easy to solve with Cramer's rule.
The radius and angles can be found using the Cartesian-to-polar transform around the center:

R= Sqrt((Xa-X)^2+(Ya-Y)^2)

Ta= atan2(Ya-Y, Xa-X)
Tc= atan2(Yc-Y, Xc-X)

But you still miss one thing: what is the relevant part of the arc ? Smaller or larger than a half turn ?

From Ta to Tb or from Tb to 2 Pi to Ta + 2 Pi, or what ? The answer is much less obvious
than it seems, try it (because the three angles Ta, Tb and Tc are undeterminate to a multiple of
2 Pi and you cannot sort them) !

Hint: consider the sign of the area of the triangle ABC, precisely the half of the determinant of the
system. It will tell you if B lies on the left or the right of AC.


'''

def determinant_fast(square_matrix: list) -> float:
    '''
    Thanks to Thom Ives
    https://integratedmlai.com/find-the-determinant-of-a-matrix-with-pure-python-without-numpy-or-scipy/
    '''

    # Section 1: Establish n parameter and copy A
    n = len(square_matrix)
    AM = square_matrix.copy()
 
    # Section 2: Row ops on A to get in upper triangle form
    for fd in range(n): # A) fd stands for focus diagonal
        for i in range(fd+1,n): # B) only use rows below fd row
            if AM[fd][fd] == 0: # C) if diagonal is zero ...
                AM[fd][fd] == 1.0e-18 # change to ~zero
            # D) cr stands for "current row"
            crScaler = AM[i][fd] / AM[fd][fd] 
            # E) cr - crScaler * fdRow, one element at a time
            for j in range(n): 
                AM[i][j] = AM[i][j] - crScaler * AM[fd][j]
     
    # Section 3: Once AM is in upper triangle form ...
    product = 1.0
    for i in range(n):
        # ... product of diagonals is determinant
        product *= AM[i][i] 
 
    return product


def determinant_recursive(A: list, total=0):
    # Section 1: store indices in list for row referencing
    indices = list(range(len(A)))
     
    # Section 2: when at 2x2 submatrices recursive calls end
    if len(A) == 2 and len(A[0]) == 2:
        val = A[0][0] * A[1][1] - A[1][0] * A[0][1]
        return val
 
    # Section 3: define submatrix for focus column and 
    #      call this function
    for fc in indices: # A) for each focus column, ...
        # find the submatrix ...
        As = A.copy() # B) make a copy, and ...
        As = As[1:] # ... C) remove the first row
        height = len(As) # D) 
 
        for i in range(height): 
            # E) for each remaining row of submatrix ...
            #     remove the focus column elements
            As[i] = As[i][0:fc] + As[i][fc+1:] 
 
        sign = (-1) ** (fc % 2) # F) 
        # G) pass submatrix recursively
        sub_det = determinant_recursive(As)
        # H) total all returns from recursion
        total += sign * A[0][fc] * sub_det 
 
    return total





'''
Finding the Center of a Circle Given 3 Points


Date: 05/25/2000 at 00:14:35
From: Alison Jaworski
Subject: finding the coordinates of the center of a circle

Hi,

Can you help me? If I have the x and y coordinates of 3 points - i.e. 
(x1,y1), (x2,y2) and (x3,y3) - how do I find the coordinates of the 
center of a circle on whose circumference the points lie?

Thank you.


Date: 05/25/2000 at 10:45:58
From: Doctor Rob
Subject: Re: finding the coordinates of the center of a circle

Thanks for writing to Ask Dr. Math, Alison.

Let (h,k) be the coordinates of the center of the circle, and r its 
radius. Then the equation of the circle is:

     (x-h)^2 + (y-k)^2 = r^2

Since the three points all lie on the circle, their coordinates will 
satisfy this equation. That gives you three equations:

     (x1-h)^2 + (y1-k)^2 = r^2
     (x2-h)^2 + (y2-k)^2 = r^2
     (x3-h)^2 + (y3-k)^2 = r^2

in the three unknowns h, k, and r. To solve these, subtract the first 
from the other two. That will eliminate r, h^2, and k^2 from the last 
two equations, leaving you with two simultaneous linear equations in 
the two unknowns h and k. Solve these, and you'll have the coordinates 
(h,k) of the center of the circle. Finally, set:

     r = sqrt[(x1-h)^2+(y1-k)^2]

and you'll have everything you need to know about the circle.

This can all be done symbolically, of course, but you'll get some 
pretty complicated expressions for h and k. The simplest forms of 
these involve determinants, if you know what they are:

         |x1^2+y1^2  y1  1|        |x1  x1^2+y1^2  1|
         |x2^2+y2^2  y2  1|        |x2  x2^2+y2^2  1|
         |x3^2+y3^2  y3  1|        |x3  x3^2+y3^2  1|
     h = ------------------,   k = ------------------
             |x1  y1  1|               |x1  y1  1|
           2*|x2  y2  1|             2*|x2  y2  1|
             |x3  y3  1|               |x3  y3  1|

Example: Suppose a circle passes through the points (4,1), (-3,7), and 
(5,-2). Then we know that:

     (h-4)^2 + (k-1)^2 = r^2
     (h+3)^2 + (k-7)^2 = r^2
     (h-5)^2 + (k+2)^2 = r^2

Subtracting the first from the other two, you get:

     (h+3)^2 - (h-4)^2 + (k-7)^2 - (k-1)^2 = 0
     (h-5)^2 - (h-4)^2 + (k+2)^2 - (k-1)^2 = 0

     h^2+6*h+9 - h^2+8*h-16 + k^2-14*k+49 - k^2+2*k-1 = 0
     h^2-10*h+25 - h^2+8*h-16 + k^2+4*k+4 - k^2+2*k-1 = 0

     14*h - 12*k + 41 = 0
     -2*h + 6*k + 12 = 0

     10*h + 65 = 0
     30*k + 125 = 0

     h = -13/2
     k = -25/6

Then

     r = sqrt[(4+13/2)^2 + (1+25/6)^2]
       = sqrt[4930]/6

Thus the equation of the circle is:

     (x+13/2)^2 + (y+25/6)^2 = 4930/36

- Doctor Rob, The Math Forum
  http://mathforum.org/dr.math/   


'''

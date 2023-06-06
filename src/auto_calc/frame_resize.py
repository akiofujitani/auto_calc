import vca_handler, vca_handler_frame_size, json_config, os, logging, log_builder, file_handler
from time import sleep


logger = logging.getLogger('frame_resize')


def __resize_both_sides(trcfmt=dict, hbox=int, vbox=int) -> dict:
    resized_trcfmt = {}
    temp_trcfmt = {}
    for side, value in trcfmt.items():
        shape_resized = vca_handler_frame_size.frame_resize(value['R'], hbox[side], vbox[side])
        temp_trcfmt['R'] = list(shape_resized.values())
        temp_trcfmt['TRCFMT'] = ['1', str(len(shape_resized)), 'E', side, 'F']
        resized_trcfmt[side] = temp_trcfmt
        temp_trcfmt = {}
        if len(trcfmt) == 1:
            other_side = 'R' if side == 'R' else 'L'
            temp_trcfmt['R'] = list(vca_handler_frame_size.shape_mirror(shape_resized).values())
            temp_trcfmt['TRCFMT'] = ['1', len(shape_resized), 'E', other_side, 'F']
            resized_trcfmt[other_side] = temp_trcfmt
        logger.debug(f'Side {side} done')
    logger.debug('Both sizes resized')     
    return resized_trcfmt


def resize(trcfmt: dict, hbox: int, vbox: int) -> dict:
    '''
    Resize trcfmt values
    trcfmt = {'R' : radius list and TRCFMT values, 'L' : radius list and TRCFMT values}
    hbox = horizontal frame length
    vbox = vertical frame length
    '''
    try:
        resized_trcfmt = {}
        temp_trcfmt = {}
        for side, radius_list in trcfmt.items():
            if radius_list:
                shape_resized = vca_handler_frame_size.resize_points(radius_list, hbox, vbox)
                temp_trcfmt[side] = list(shape_resized.values())
                temp_trcfmt['TRCFMT'] = ['1', str(len(shape_resized)), 'E', side, 'F']
                resized_trcfmt[side] = temp_trcfmt
                temp_trcfmt = {}
                logger.debug(f'Resize {side} done')
        if len(resized_trcfmt) == 1:
            other_side = 'R' if list(resized_trcfmt.keys())[0] == 'L' else 'R'
            temp_trcfmt['R'] = list(vca_handler_frame_size.shape_mirror(shape_resized).values())
            temp_trcfmt['TRCFMT'] = ['1', len(shape_resized), 'E', other_side, 'F']
            resized_trcfmt[other_side] = temp_trcfmt
            logger.debug(f'Mirror {other_side} done')
        logger.debug(f'Resize done')
        return resized_trcfmt
    except Exception as error:
        logger.error(f'Frame resize error {error}')
        raise error


def shape_center(trcfmt: dict, ipd: dict, ocht: dict, dbl: float) -> dict:
    '''
    Used to thickness calculation, must have both sides to work
    If one side is missing, other side will be copied to fill the value gap
    trcfmt -> R: radius list, L: radius list
    ipd -> R: float, L: float
    ocht -> R: float, L: float
    dbl -> float
    '''
    try:
        ipd_values = r_l_gap_filler(ipd)
        ocht_values = r_l_gap_filler(ocht)

        shape_optical_center = {}
        for side, trcfmt_value in trcfmt:
            shape_optical_center[side] = vca_handler_frame_size.frame_recenter(trcfmt_value['R'], 
                                side, 
                                ipd_values[side], 
                                ocht_values[side], 
                                dbl)
        return shape_optical_center
    except Exception as error:
        logger.error(f'shape_center error {error}')
        raise error


def r_l_gap_filler(tag_value: dict) -> dict:
    filled_tag_value = {}
    for side, value in tag_value:
        if not value:
            other_side = 'R' if side == 'L' else 'L'
            filled_tag_value[side] = tag_value[other_side]
        else:
            filled_tag_value[side] = value
    return filled_tag_value


if __name__ == '__main__':
    logger = logging.getLogger()
    log_builder.logger_setup(logger)


    # path = os.path.normpath(config['path'])
    # path_done = os.path.normpath(config['path_done'])
    # path_new = os.path.normpath(config['path_new_file'])
    # sleep_time = int(config['sleep_time'])

    path = os.path.normpath(r'C:\Users\faust\OneDrive\Documentos\VCA\VCA Import')
    path_done = os.path.normpath(r'C:\Users\faust\OneDrive\Documentos\VCA\VCA Import\Done')
    sleep_time = int(3)


    while True:
        vca_list = file_handler.file_list(path, 'vca')
        if len(vca_list) > 0:
            for vca_file in vca_list:
                try:
                    vca_data = file_handler.file_reader(os.path.join(path, vca_file))
                    job_vca = vca_handler.VCA_to_dict(vca_data)
                    logger.debug(f'{job_vca["JOB"]}\n')
                    trace_format_resized = __resize_both_sides(job_vca['TRCFMT'], job_vca['HBOX'], job_vca['VBOX'])
                    job_vca['TRCFMT'] = trace_format_resized
                    vca_contents_string = vca_handler.dict_do_VCA(job_vca)
                    file_handler.file_move_copy(path, path_done, vca_file, False)
                    logger.debug(vca_contents_string)
                    logger.debug('\n')
                except Exception as error:
                    logger.error(f'Error {error} in file {vca_file}')
        sleep(sleep_time)
        logger.info(f'Waiting... {sleep_time}')

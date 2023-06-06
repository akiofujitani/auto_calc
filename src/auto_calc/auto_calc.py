import file_handler, json_config, log_builder, logging, keyboard, threading, vca_handler, frame_resize, calc_proccess
from classes import *
from time import sleep
from ntpath import join

logger = logging.getLogger('auto_calc')


'''
=============================================================================================

        Template        Template        Template        Template        Template        

=============================================================================================
''' 

config = '''
{
    "sleep_time" : 3,
    "input" : "./",
    "output" : "./",
    "error" : "./",
    "extension" : "vca",
}
'''

parameters = '''
    "frame_type" : {
        "plastic" : "1",
        "rimless" : "1",
        "metal" : "2",
        "rimless_grooved" : "3",
        "security" : "4"
    },
    "default_ipd" : "32",
    "default_ocht" : "21",
    "default_dbl" : "18",
    "corrlen_ocht" : {
        "14" : {
            "min" : "14",
            "max" : "18"
        },
        "16" : {
            "min" : "19",
            "max" : "23"  
        },
        "18" : {
            "min" : "24",
            "max" : "29"  
        },
        "20" : {
            "min" : "30",
            "max" : "40"  
        }
    }
'''


tag_swap = '''
{
    "tag_swap" : {
        {
            "tag" : {
                "sign" : "",
                "old_value" : "",
                "new" : ""
                "new_value" : ""            
            }
        }
    }
}

'''


blanks = '''
{
    "blank_list" : {
        "0000" : {
            "blank_code" : "0000",
            "code" : "000",
            "index" : "1.53",
            "index_group : "153",
            "base_list": {
                "0" : "0.00",
                "1" : "1.00",
                "2" : "2.00",
                "3" : "3.00",
                "4" : "4.00",
                "5" : "5.00",
                "6" : "6.00",
                "7" : "7.00",
                "8" : "8.00",
                "9" : "9.00",
                "10" : "10.00"
            }
        },
        "4155" : {
            "blank_code" : "4155",
            "code" : "083",
            "index" : "149",
            "index_group : "1.49",
            "base_list": {
                "0" : "0.50",
                "2" : "2.00",
                "4" : "4.00",
                "5" : "5.00",
                "6" : "6.00",
                "8" : "8.00",
                "10" : "10.00"
            }
        }
    }
}

'''

desings_list = '''
{
    "design_list" : {
        "desing" : {
            "lds" : "SCH",
            "lds_code" : "1",
            "design" : "Natural Accuracy",
            "design_code" : "01",
            "design_type" : "PR",
            "corr_len" : [
                "14", "16", "18"
            ]  
        }
    }
}
'''


'''
=============================================================================================

        Functions       Functions       Functions       Functions       Functions            

=============================================================================================
''' 

def quit_func():
    '''
    check event and terminated thread on set
    '''
    logger.info('Quit pressed')
    event.set()
    return


def shape_resize(job_data: dict) -> dict:
    '''
    Return the shape resized to main function
    '''
    try:
        side = job_data['DO']
        hbox = calc_proccess.return_side_value(side, job_data['HBOX'])
        vbox = calc_proccess.return_side_value(side, job_data['VBOX'])
        shape_resized = frame_resize.resize(job_data['TRCFMT'], hbox, vbox)
        return shape_resized
    except Exception as error: 
        logger.error(f'shape_resize error {error}')
        raise error


def fill_default(parameter_value: any, tag_value:any) -> any:
    '''
    Fill empty values with default ones from parameter object if not present in tag
    '''
    if tag_value.isinstance(dict):
        updated_tag_value = {}
        if 'R' in tag_value.keys():
            for side, value in tag_value.items():
                if not value and not tag_value['R' if side == 'L' else 'R']:
                    updated_tag_value[side] = parameter_value
            return updated_tag_value
    else:
        if not tag_value:
            return parameter_value
        else:
            return tag_value


def shape_to_optical_center(parameters: Parameters, shape_resized: dict, job_data: dict) -> dict:
    '''
    Return the shape recentered to the optical center for thickness calculation
    '''
    try:
        ipd = fill_default(parameters.ipd_default, job_data.get('IPD', {'R': '', 'L': ''}))
        ocht = fill_default(parameters.ocht_default, job_data.get('OCHT', {'R': '', 'L': ''}))
        dbl = fill_default(parameters.dbl_default, job_data.get('DBL', ''))
        shape_recentered = frame_resize.shape_center(shape_resized, ipd, ocht, dbl)
        return shape_recentered
    except Exception as error:
        logger.error(f'shpe_optical_center error {error}')
        raise error


def main(event: threading.Event, config: Configuration, lnam_swap_list: list) -> None:
    if event.isSet():
        return
    
    done_list = []
    while True:
        sleep(config.sleep_time)
        file_list = file_handler.file_list(config.input, config.extension)
        if len(file_list) > 0:
            for file in file_list:
                if file not in done_list:
                    updated_tags = {}
                    try:
                        file_contents = file_handler.file_reader(join(config.input, file))
                        vca_converted = vca_handler.VCA_to_dict(file_contents)

                        if len(lnam_swap_list) > 0: # LNAM Swapper
                            new_lnam = calc_proccess.lnam_swapper(lnam_swap_list, vca_converted['LNAM']['L'] if vca_converted['DO'] == 'L' else vca_converted['LNAM']['R'])
                            if new_lnam:
                                updated_tags['LNAM'] = calc_proccess.set_side_value(vca_converted['DO'], new_lnam)
                                logger.debug(f'LNAM: {new_lnam}')
                        shape_resized = shape_resize(vca_converted)
                        shape_optical_center = shape_to_optical_center(parameters, shape_resized, vca_converted)
                        

                    except Exception as error:
                        logger.error(f'VCA conversion error {error}')
                        file_handler.file_move_copy(config.input, config.error, file, False, True)
        pass






'''
=============================================================================================

        Main        Main        Main        Main        Main        Main        Main        

=============================================================================================
''' 


if __name__ == '__main__':
    logger = logging.getLogger()
    log_builder.logger_setup(logger)


    try:
        config_dict = json_config.load_json_config('config.json', config)
        config = Configuration.init_dict(config_dict)
    except:
        logger.critical('Could not load config file')
        exit()


    keyboard.add_hotkey('space', quit_func)
    event = threading.Event()

    for _ in range(3):
        if event.is_set():
            break
        thread = threading.Thread(target=main, args=(event, config, ), name='white_label')
        thread.start()
        thread.join()

    logger.debug('Done')
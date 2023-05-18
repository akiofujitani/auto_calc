import file_handler, json_config, log_builder, logging, keyboard, threading, vca_handler
from dataclasses import dataclass
from time import sleep
from os.path import normpath, abspath
from ntpath import join

logger = logging.getLogger('auto_calc')


'''
=============================================================================================

        Classes     Classes     Classes     Classes     Classes     Classes     Classes     

=============================================================================================
'''

@dataclass
class Configuration:
    input : str
    output : str
    error : str
    extension : str
    sleep_time : int



    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, self.__class__):
            return NotImplemented
        else:
            self_values = self.__dict__
            for key in self_values.keys():
                if not getattr(self, key) == getattr(__o, key):
                    return False
            return True
    

    @classmethod
    def init_dict(cls, dict_values=dict):
        try:
            input = normpath(dict_values['input'])
            output = normpath(dict_values['output'])
            error = normpath(dict_values['error'])
            extension = dict_values ['extension']
            sleep_time = int(dict_values['sleep_time'])
            return cls(input, output, sleep_time)
        except Exception as error:
            logger.error(f'Error in {error}')


@classmethod
class Blank:
    blank_code: int
    code : int
    index: float
    index_group: str
    base_list: dict


    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, self.__class__):
            return NotImplemented
        else:
            self_values = self.__dict__
            for key in self_values.keys():
                if not getattr(self, key) == getattr(__o, key):
                    return False
            return True





'''
=============================================================================================

        Template        Template        Template        Template        Template        

=============================================================================================
''' 

template = '''
{
    "sleep_time" : 1,
    "input" : "./",
    "output" : "./",
    "error" : "./",
    "extension" : "vca"
}
'''

lnam_swap = '''
{
    "lnam_swap" : [
        {
            "old" : "",
            "new" : ""
    ]
}

'''


blanks = '''
{
    "blank_list" : [
        {
            "blank_code" : "",
            "code" : "",
            "index" : "",
            "index_group : "",
            "base_list": {
                "0" : "0.50",
                "2" : "2.00",
                "4" : "4.00",
                "6" : "6.00",
                "8" : "8.00"
            } 
        }
    ]
}

'''

desings_list = '''
{
    "design_list" : {
        "lms_design" : "",
        "corr_len" : "",
        "design_type" 
    }
}
'''



'''
=============================================================================================

        Functions       Functions       Functions       Functions       Functions            

=============================================================================================
''' 

def quit_func():
    logger.info('Quit pressed')
    event.set()
    return


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


def refraction_index(lnam: str, blank_list: list) -> int:
    '''
    Get LNAM code and extract blank value, compare with given list and return the refraction index
    '''
    index_code = lnam[1:4]
    for blank in blank_list:
        if blank.code in index_code:
            return float(blank.code)
    return float(1.53)


def frame_type_thicknes_definer(frame_type: str):
    match int(frame_type):
        case 4:
            return 'safety'
        case 3:
            return 'grooved'
        case 2:
            return 'default'
        case _:
            return 'default' 


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

                        '''
                        LNAM Swapper

                        '''
                        if lnam_swap_list:
                            new_lnam = lnam_swapper(lnam_swap_list, vca_converted['LNAM']['L'] if vca_converted['DO'] == 'L' else vca_converted['LNAM']['R'])
                            if new_lnam:
                                updated_tags['LNAM'] = set_side_value(vca_converted['DO'], new_lnam)
                                logger.debug(f'LNAM: {new_lnam}')
                        '''
                        Thickness Type
                        '''              
                        



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
        config_dict = json_config.load_json_config('config.json', template)
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
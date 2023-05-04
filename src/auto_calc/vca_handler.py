import os, logging, file_handler
from datetime import datetime

logger = logging.getLogger('vca_handler')


def convert_add_to_list(values_old: any, new_values: any) -> list:
    if not type(values_old) == list:
        return [values_old] + [new_values]
    else:
        return values_old + [new_values]


def VCA_to_dict(VCA_file_contents):
    data_value = {}
    try:
        for line in VCA_file_contents:
            line = line.replace('\n', '').replace('\t', '')
            if len(line) > 0:
                tag_and_value = line.split('=')
                logger.debug(tag_and_value[0])
                if ';' not in tag_and_value[1]:
                    if tag_and_value[0] in data_value.keys():
                        data_value[tag_and_value[0]] = convert_add_to_list(data_value[tag_and_value[0]], tag_and_value[1])
                    else:
                        data_value[tag_and_value[0]] = tag_and_value[1]
                else:
                    values_splited = tag_and_value[1].split(';')
                    if len(values_splited) == 2:
                        if tag_and_value[0] in data_value.keys():
                            data_value[tag_and_value[0]] = convert_add_to_list(data_value[tag_and_value[0]], {'R' : values_splited[0], 'L' : values_splited[1]})
                        else:
                            data_value[tag_and_value[0]] = {'R' : values_splited[0], 'L' : values_splited[1]}
                    if tag_and_value[0] == 'TRCFMT' or tag_and_value[0] == 'CRIBFMT':
                        counter = round(int(values_splited[1]) / 15 if int(values_splited[1]) == 1000 else 10)
                        temp_values = {}
                        tag_name = tag_and_value[0]
                        temp_values[tag_name] = values_splited
                        radius_list = []
                    if tag_and_value[0] == 'R':
                        radius_list = radius_list + values_splited
                        counter -= 1
                        if counter == 0:
                            temp_values['R'] = radius_list
                            if tag_name in data_value.keys():
                                data_value[tag_name].update({temp_values[tag_name][3] : temp_values})
                            else:
                                data_value[tag_name] = {temp_values[tag_name][3] : temp_values}
        logger.info('VCA contents converted')
        return data_value
    except Exception as error:
        logger.error(f'Error ocurred in {error}')
        raise Exception(f'Error in {error}')
                

def dict_do_VCA(job_data=dict):
    vca_contents = ''
    for key, value in job_data.items():
        vca_contents = vca_contents + __to_string(key, value)
    return vca_contents


def __divide_list_chunks(values_list=list, chunk_size=10):
    values_list = list(values_list)
    new_list = [values_list[i:i + chunk_size] for i in range(0, len(values_list), chunk_size)]
    return new_list


def __to_string(key=str, values=any, left='L', right='R') -> str:
    string_line = ''
    if type(values) == str:
        string_line = f'{key}={values}\n'
        return string_line
    elif key == 'TRCFMT':
        for value in values.values():
            string_line = string_line + f'{key}={";".join(value["TRCFMT"])}\n'
            radius_in_chunks = __divide_list_chunks(value['R'])
            for chunk in radius_in_chunks:
                string_line = string_line + f'R={";".join([str(value) for value in chunk])}\n'
        return string_line
    elif type(values) == list:
        for value in values:
            string_line = string_line + f'{key}={value}\n'
        return string_line
    elif 'R' in values.keys() or 'L' in values.keys():
        string_line = f'{key}={string_line}{values[right]};{values[left]}\n'
        return string_line
    else:
        logger.info(f'{key}={value}')     
    return


# check and deativate > file_handler.file_finder is simpler and works almost the same way getting the same input
def find_files(path_root_list, name, extention, start_pos, end_pos=None):
    for path_root in path_root_list:
        for root, dir, files in os.walk(path_root):
            file_dict = {}
            for file in files:
                if file.lower().endswith(f'{extention}') and name in file[start_pos:end_pos]:
                    file_dict['root'] = root
                    file_dict['file_name'] = file
                    return file_dict
    return False


def filter_tag(job_data: dict, **kwargs) -> dict:
    '''
    filter dict data based on tag's list
    '''
    filtered_data = {}
    for key, arg in kwargs.items():
        retrieved_data = job_data.get(key, arg)
        logger.debug(f'{key} : {retrieved_data}')
        if not type(retrieved_data) == type(arg):
            if 'R' in arg.keys() and 'L' in arg.keys():
                side = job_data.get('DO', 'R')
                temp_dict = {}
                temp_dict[side] = retrieved_data
                temp_dict['L' if side == 'R' else 'R'] = ''
                retrieved_data = temp_dict
            logger.warning('Value type diff')        
        filtered_data[key] = retrieved_data
    return filtered_data


def read_vca(file_list: list, start_date: datetime.date, end_date: datetime.date, **kwargs) -> dict:
    '''
    Read all vca files within the given start and end date and return a dict using the job number as key
    '''
    date_filtered_list = file_handler.listByDate(file_list, start_date, end_date)
    values_dict = {}
    for file in date_filtered_list:
        try:
            logger.debug(f'Tring to open file {file}')
            with open(file, 'r', errors='replace') as contents:
                fileContents = contents.readlines()
                temp_vca_contents = VCA_to_dict(fileContents)

                logger.debug('Filtering tags')
                if len(kwargs) > 0:
                    filtered_vca = filter_tag(temp_vca_contents, **kwargs)
                    values_dict[temp_vca_contents['JOB']] = filtered_vca
                else:
                    values_dict[temp_vca_contents['JOB']] = temp_vca_contents
        except Exception as error:
            logger.error(error)
    return values_dict


def read_vca_by_job(file_list: list, job_number_list: list, name_start_pos: int=0, name_end_pos: int | None=None, **kwargs) -> dict:
    '''
    Find vca by job number list returning a dict values filtered by tags
    '''
    try:
        found_dict = {}
        for job_number in job_number_list:
            file_found = file_handler.file_finder(file_list, job_number, start_pos=name_start_pos, end_pos=name_end_pos)
            if file_found:
                logger.info(f'{job_number} found')
                vca_converted = VCA_to_dict(file_handler.file_reader(file_found))

                logger.debug('Filtering tags')
                if len(kwargs) > 0:
                    filtered_vca = filter_tag(vca_converted, **kwargs)
                    found_dict[job_number] = filtered_vca
                else:
                    found_dict[job_number] = vca_converted
        logger.info('Returning values')
        return found_dict
    except Exception as error:
        logger.error(f'read_vca_by_job {error}')
        raise error


def key_renamer(name_insertion: str, dict_values: dict) -> dict:
    new_dict = {}
    for key, value in dict_values.items():
        new_dict[f'{name_insertion}_{key}'] = value
    return new_dict


def merge_read_vca(read_vca_1: dict, 
                   read_vca_2: dict, 
                   read_vca_1_name: str, 
                   read_vca_2_name: str, 
                   vca_2_kwargs: dict) -> dict:
    '''
    Merge two vca job dict using their key as match
    '''
    merged_dict = {}
    for key, vca in read_vca_1.items():
        temp_dict = {}
        temp_dict.update(key_renamer(read_vca_1_name, vca))
        temp_dict.update(key_renamer(read_vca_2_name, read_vca_2.get(key, vca_2_kwargs)))
        merged_dict[key] = temp_dict
    return merged_dict


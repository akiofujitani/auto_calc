import csv, os, shutil, datetime, time, chardet, logging
from ntpath import join

logger = logging.getLogger('file_handler')


def file_list(path=str, file_extention=str) -> list:
    '''
    List files ended with choosen extension inside one directory
    '''
    if not os.path.exists(path):
        os.makedirs(path)
        logger.info(f'Directory {path} created')
    return [file for file in os.listdir(path) if file.lower().endswith(f'.{file_extention.lower()}')]


def listFilesInDirSubDir(pathRoot: str, extention: str='') -> list:
    '''
    List files ended with choosen extension inside all directories inside the path
    '''
    fileList = []
    for root, _, files in os.walk(pathRoot):
        for file in files:
            if file.lower().endswith(extention):
                logger.debug(f'file {file}')
                fileList.append(os.path.join(root, file))
    logger.info(f'Listing for {pathRoot} done')
    return fileList


def fileListFullPath(path, file_extention) -> list:
    '''
    List files returning the full path list ended with choosen extension inside one directory
    '''    
    if not os.path.exists(path):
        os.mkdir(path)
        logger.info(f'Directory {path} created')    
    return [os.path.join(path, file) for file in os.listdir(path) if file.lower().endswith(f'.{file_extention.lower()}')]


def __csv_reader(file_path, case_upper, delimeter_char, encoding='utf-8'):
    '''
    Auxiliary method for CSVtoList
    '''
    with open(file_path, encoding=encoding) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=delimeter_char, quoting=csv.QUOTE_NONE)
        header = []
        header = next(csv_reader)

        csv_contents = []
        for row in csv_reader:
            row_Contents = {}
            for key in range(len(header)):
                if case_upper:
                    header_value = header[key].upper()
                else:
                    header_value = header[key]
                row_Contents[header_value] = row[key]        
            csv_contents.append(row_Contents)
    logger.info('CSV contents extracted')
    return csv_contents


def CSVtoList(filePath, case_upper=True, delimeter_char='\t') -> list:
    '''
    Get csv file, ready and convert it to list
    '''
    file_path = os.path.normpath(filePath)
    try:
        logger.debug('Trying to read csv file on default enconde')
        csv_contents = __csv_reader(file_path, case_upper, delimeter_char)
    except Exception as error:
        logger.error(error)
        try:
            try:
                logger.debug('Trying to read csv file on default enconde cp1252')
                csv_contents = __csv_reader(filePath, case_upper, delimeter_char, encoding='cp1252')
            except:
                logger.debug('Find best suited enconde and try to read')
                encoding = __detect_encode(filePath)
                csv_contents = __csv_reader(filePath, case_upper, delimeter_char, encoding=encoding)
        except:
            raise Exception('Could not read file contents')        
    return csv_contents


def __detect_encode(file_path):
    '''
    Auxiliary method for CSVoList
    Try to detect the encoding type
    '''
    logger.debug('Try to find best tuited encode for data')
    with open(file_path, 'rb') as rawdata:
        result = chardet.detect(rawdata.read(100000))
    return result['encoding']


def listToCSV(valuesList, filePath) -> None:
    '''
    Convert list to CSV using first line as header
    '''
    with open(filePath, 'w', newline='') as csvFile:
        writer = csv.DictWriter(csvFile, fieldnames=list(valuesList[0].keys()), quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(valuesList)
        logger.debug('List to CSV complete')
    return


def file_finder(file_list: list, file_name: str, start_pos: int=0, end_pos: None=None) -> str:
    '''
    Search file in list by partial name with start en end position 
    '''
    logger.info(f'Searching for file {file_name}')
    for file in file_list:
        try:
            base_name = os.path.basename(file)
            cropped_name = base_name[start_pos:end_pos]
            if file_name in cropped_name:
                logger.info(f'{file_name} found')
                return file
        except Exception as error:
            logger.error(f'Error searching {file} due {error}')
    return False


def file_reader(file_path):
    try:
        with open(file_path, encoding='utf-8') as file:
            return file.readlines()
    except Exception as error:
        logger.warning(f'Error {error}')
        with open(file_path, encoding='cp1252') as file:
            return file.readlines()


def file_writer(file_path=str, file_name=str, string_values=str) -> None:
    if not os.path.exists(file_path):
        os.mkdir(file_path)
        logger.info(f'Directory {file_path} created')
    with open(join(file_path, file_name), 'w') as writer:
        writer.write(string_values)
        return


def file_move_copy(path_from, path_to, file_name, copy=bool, overwrite=False):
    try:
        path_from = os.path.normpath(path_from)
        path_to = os.path.normpath(path_to)
        move_copy = 'copied' if copy == True else 'moved'
        logger.debug(f'From {path_from} to {path_to}')
        logger.debug(f'File {file_name} {move_copy}')
        check_create_dir(path_to)
        new_file_name = __file_name_check(path_to, file_name) if overwrite is False else file_name
        if copy == True:
            return shutil.copy(join(path_from, file_name), join(path_to, new_file_name))
        else:
            return shutil.move(join(path_from, file_name), join(path_to, new_file_name))
    except Exception as error:
        logger.error(f'Could not execute {error}')
        raise error


def __copy_number_definer(file_name=str):
    count = 0
    pure_file_name = file_name.replace(')', '').split('_(Copy_')
    count = int(pure_file_name[1]) + 1
    return f'{pure_file_name[0]}_(Copy_{count})'


def __file_name_check(path, file_name):
    while os.path.exists(join(path, file_name)):
        name_splitted = file_name.split('.')
        if len(name_splitted) >= 2:
            temp_name = ''
            for i in range(len(name_splitted) - 1):
                temp_name = temp_name + f'{name_splitted[i]}.'
            file_name_no_ext = temp_name[:-1]
            extension = name_splitted.pop()
        else:
            file_name_no_ext = name_splitted[0]
        if '_(Copy_' in file_name_no_ext:
            file_name = __copy_number_definer(file_name_no_ext)
        else:
            file_name = f'{file_name_no_ext}_(Copy_1).{extension}' if extension else f'{name_splitted[0]}_(Copy_1)'
    logger.debug(file_name)
    return file_name


def fileNameDefiner(path, file_name, extention):
    while os.path.exists(join(path, f'{file_name}.{extention}')):
        name_splitted = file_name.split('_')
        if len(name_splitted) == 1:
            file_name += '_1'
        else:
            number = int(name_splitted[-1]) + 1
            rebuilt_name = ''
            for part in range(len(name_splitted) - 1):
                rebuilt_name = rebuilt_name + '_' + name_splitted[part]
            rebuilt_name = rebuilt_name.replace('_' , '', 1)
            file_name = f'{rebuilt_name}_{number}'
    logger.debug(f'File name {file_name}')
    return file_name


def fileMoveRename(source, destin, source_name, destin_name):
    destin_name_no_extention = destin_name.split('.')[0]
    extention = destin_name.split('.')[1]
    try:
        file_name_checked = fileNameDefiner(destin, destin_name_no_extention, extention)
        shutil.move(join(source, f'{source_name}'), join(destin, f'{file_name_checked}.{extention}'))
        logger.info(f'{source_name} renamed to {destin_name}')
        logger.info(f'Moved from "{source}" to "{destin}"')
        return
    except FileNotFoundError as file_error:
        logger.warning(file_error)
    return


def creatDir(path, dir_name=None):
    full_path = path
    if not dir_name == None:
        full_path = join(path, dir_name)
    if not os.path.exists(full_path):
        os.mkdir(full_path)
        logger.info(f'Directory "{dir_name}" created.')
    return


def check_create_dir(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
            logger.info(f'Directory "{path}" created.')
        return path
    except Exception as error:
        logger.error(f'Could not check/create {path}')
        raise Exception(error)


def file_list_last_date(path: str, extension: str, pattern_removal: str, date_pattern: str) -> datetime.datetime.date:
    '''
    Retrieves the last defined data in file list.
    This don't retrieves the creattion date, its the date defined in the file name
    '''
    try:
        files_list = file_list(path, extension)
        date_list = []
        for file in files_list:
            file_extension = file.split('.')
            date_list.append(datetime.datetime.strptime(file_extension[0].replace(pattern_removal, ''), date_pattern))
            date_list.sort(reverse=True)
        logger.debug(date_list[0])
        return date_list[0].date()
    except Exception as error:
        logger.error(error)
        return None


def file_contents_last_date(file_contents=dict, field_name=str, time_format='%d/%m/%Y'):
    try:
        last_date = sorted(file_contents, key=lambda value : datetime.datetime.strptime(value[field_name], time_format), reverse=True)[0][field_name]
        strip_date = datetime.datetime.strptime(last_date, time_format).date()
        return strip_date
    except Exception as error:
        logger.error('Could not get date from file')
        raise error


def file_contents_last_date1(path: str, extension: str, field_name: str) -> datetime.datetime.date:
    try:
        files_list = file_list(path, extension)
        last_date = ''
        for file in files_list:
            file_contents = CSVtoList(join(path, file))
            temp_date =  datetime.datetime.strptime(sorted(file_contents, key=lambda value : value[field_name], reverse=True)[0][field_name], '%d/%m/%Y').date()
            if last_date == '':
                last_date = temp_date
            if temp_date > last_date:
                last_date = temp_date
        logger.debug(datetime.datetime.strptime(last_date, '%Y/%m/%d'))
        return last_date
    except Exception as error:
        logger.error('Could not get date from files')
        raise error


def listByDate(filesList: list, dateStart: datetime.date, dateEnd: datetime.date) -> list:
    listByDate = []
    for file in filesList:
        fileDate = fileCreationDate(file)
        if fileDate >= dateStart and fileDate <= dateEnd if dateEnd else dateStart:
            listByDate.append(file)
    logger.info(f'Listing by date {dateStart} / {dateEnd} done')
    return listByDate


def fileCreationDate(file):
    return datetime.datetime.fromtimestamp(os.path.getctime(file)).date()


# def fileCreationDate(file):
#     strSplit = time.ctime(os.path.getmtime(file)).split(' ')
#     for item in strSplit:
#         if len(item) == 0:
#             strSplit.remove(item)
#     return datetime.datetime.strptime(f'{strSplit[4]}/{strSplit[1]}/{strSplit[2]}', '%Y/%b/%d').date()


def listFilesInDirSubDirWithDate(pathRoot: str, extention: str='') -> list:
    '''
    List files ended with choosen extension inside all directories inside the path
    '''
    fileList = []
    for root, _, files in os.walk(pathRoot):
        for file in files:
            if file.lower().endswith(extention):
                file_path = os.path.join(root, file)
                file_date = fileCreationDate(file_path)
                logger.debug(f'file {file_path} {file_date}')
                fileList.append({'FILE' : file_path, 'DATE' : file_date})
    logger.info(f'Listing for {pathRoot} done')
    return fileList



def listFilesInDirSubDirByDate(pathRoot: str, extention: str='') -> dict:
    '''
    List files ended with choosen extension inside all directories inside the path
    '''
    file_dict_date = {}
    for root, _, files in os.walk(pathRoot):
        for file in files:
            if file.lower().endswith(extention):
                file_path = os.path.join(root, file)
                file_date = datetime.datetime.strftime(fileCreationDate(file_path), '%Y/%m/%d')
                logger.debug(f'file {file_path} {file_date}')
                dict_value = file_dict_date.get(file_date, None)
                if dict_value == None:
                    file_dict_date[file_date] = [file_path]
                else:
                    file_dict_date[file_date].append(file_path)          
    logger.info(f'Listing for {pathRoot} done')
    return file_dict_date
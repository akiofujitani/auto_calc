import json, os


def load_json_config(config_file=str, template_data=None) -> dict:
    '''
    load json file and transforms it in dictionary
    the template_data  
    '''
    if os.path.exists(config_file):
        with open(config_file, encoding='utf-8') as file_data:
            return json.load(file_data)
    elif template_data:
        template_data = json.loads(template_data)
        with open(config_file, 'w') as json_file:
            json.dump(template_data, json_file, indent=4)
            return template_data
    else:
        raise Exception('File not found and no template data inserted')


def save_json_config(config_file=str, json_config=dict) -> None:
    with open(config_file, 'w') as json_file:
        json.dump(json_config, json_file, indent=4)
    return



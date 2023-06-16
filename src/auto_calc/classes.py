import logging, log_builder
from dataclasses import dataclass
from os.path import normpath


logger = logging.getLogger('classes')


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
            return cls(input, output, error, extension, sleep_time)
        except Exception as error:
            logger.error(f'Error in {error}')


@dataclass
class Parameters:
    frame_type: dict
    default_ipd: float
    default_ocht: float
    default_dbl: float
    corrlen_ocht: dict


    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, self.__class__):
            return NotImplemented
        else:
            self_values = self.__dict__
            for key in self_values.keys():
                if not getattr(self, key) == getattr(__o, key):
                    return False
            return True
    

    def return_frame_type(self, frame_type_num: int) -> str:
        for type_key, type_num in self.frame_type:
            if int(type_num) == frame_type_num:
                return type_key
        return 'Default'


    def return_corrlen(self, ocht: float) -> int:
        for corrlen, ocht_dict in self.corrlen_ocht.items():
            if ocht >= ocht_dict.get('min', '') and ocht <= ocht_dict.get('max', ''):
                return corrlen
        return 16.00


    @classmethod
    def init_dict(cls, dict_values=dict):
        try:
            frame_type = dict_values['frame_type']
            default_ipd = float(dict_values['default_ipd'])
            default_ocht = float(dict_values['default_ocht'])
            default_dbl = float(dict_values['default_dbl'])
            corrlen_ocht = dict_values['corrlen_ocht']
            return cls(frame_type, default_ipd, default_ocht, default_dbl, corrlen_ocht)
        except Exception as error:
            logger.error(f'Error in {error}')


@dataclass
class TagAndSwap:
    '''
    Tags list with TagValue object
    '''
    tag_list: list


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
            tag_list = {tag_name : TagValue.init_dict(tag_value) for tag_name, tag_value in dict_values['tag_list'].items()}
            return cls(tag_list)
        except Exception as error:
            logger.error(f'Error in {error}')


@dataclass
class TagValue:
    '''
    sign > must be: 
    >: greater
    <: less
    >=: greater equal
    <=: less equal
    ==: equal
    c: contains
    compare to old value and if matches, asign the new value to the new Tag
    '''
    sign : str
    compare_value : str
    destin_tag : str
    new_sign : str
    new_value : str


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
            sign = dict_values['sign']
            compare_value = dict_values['compare_value']
            destin_tag = dict_values['destin_tag']
            new_sign = dict_values['new_sign']
            new_value = dict_values['new_value']
            return cls(sign, compare_value, destin_tag, new_sign, new_value)
        except Exception as error:
            logger.error(f'Error in {error}')


@dataclass
class Blank:
    blank_code : int
    code : int
    index : float
    index_group : str
    index_type: str
    base_list : dict


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
            blank_code = int(dict_values['blank_code'])
            code = int(dict_values['code'])
            index = float(dict_values ['index'])
            index_group = str(dict_values['index_group'])
            index_type = str(dict_values['index_type'])
            base_list = dict_values['base_list']
            return cls(blank_code, code, index, index_group, index_type, base_list)
        except Exception as error:
            logger.error(f'Error in {error}')


@dataclass
class BlankList:
    blank_list : dict


    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, self.__class__):
            return NotImplemented
        else:
            self_values = self.__dict__
            for key in self_values.keys():
                if not getattr(self, key) == getattr(__o, key):
                    return False
            return True


    def return_blank_by_lnam(self, lnam: int) -> Blank:
        code = int(lnam[1:5])
        for blank in self.blank_list:
            if blank.code == code:
                return blank
        return self.blank_list['0000']
    

    @classmethod
    def init_dict(cls, dict_values=dict):
        try:
            blank_list = {blank_code : Blank.init_dict(blank_value) for blank_code, blank_value in dict_values['blank_list'].items()}
            return cls(blank_list)
        except Exception as error:
            logger.error(f'Error in {error}') 


@dataclass
class Design:
    '''
    lds: IOT, SCH, HOR -> calculationr design provider
    lsd_code: 1, 2, 4, 5 -> As set, first digit of the code is the LDS number
    design: BasicH40, Natural Accuracy -> Name of the designt
    design_code: 01, 02, 03 -> As set, last two digits of the code is the design number
    design_type: PR, VS -> type of the design, progressive, single vision
    corr_len: [14, 16, 18] -> list of the avaiable corre_len
    corr_len_translator: 0, 2 -> int value to translate corre_len to the real value presented in the LDS chart

    '''
    lds : str
    lds_code : int
    design : str
    design_code : int
    design_type : str
    corr_len : list
    corr_len_translator: int


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
            lds = dict_values['lds']
            lds_code = int(dict_values['lds_code'])
            design = dict_values ['design']
            design_code = int(dict_values['design_code'])
            design_type = str(dict_values['design_type'])
            corr_len_translator = dict_values['corr_len_translator']
            corr_len = dict_values['corr_len']
            return cls(lds, lds_code, design, design_code, design_type, corr_len_translator, corr_len)
        except Exception as error:
            logger.error(f'Error in {error}') 


@dataclass
class DesignList:
    '''
    Design list is the dict of class Design
    using design name as key
    '''
    design_list : dict


    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, self.__class__):
            return NotImplemented
        else:
            self_values = self.__dict__
            for key in self_values.keys():
                if not getattr(self, key) == getattr(__o, key):
                    return False
            return True


    def return_corrlen(self, lnam: int) -> Design:
        try:
            lds_code = lnam[1:1]
            design_code = lnam[4:6]
            for design in self.design_list:
                if design.lds_code == lds_code and design.design_code == design_code:
                    return design
            return None
        except Exception as error:
            logger.error(f'Return_corrlen error {error}')
            return None


    @classmethod
    def init_dict(cls, dict_values=dict):
        try:
            design_list = {desing_name : Design.init_dict(design_value) for desing_name, design_value in dict_values['design_list'].items()}
            return cls(design_list)
        except Exception as error:
            logger.error(f'Error in {error}')


@dataclass
class FrameThickness:
    thickness_list : dict


    def return_thickness(self, sph_diopter: float):
        sph_in_quarter = float(round(sph_diopter * 4) / 4)
        max_diopter = max(float(diopter) for diopter in list(self.thickness_list.keys()))
        min_diopter = min(float(diopter) for diopter in list(self.thickness_list.keys()))
        if sph_in_quarter >= max_diopter:
            thicknes_group = self.thickness_list[str(f'{max_diopter:0.2f}')]
            return thicknes_group['ET']
        if sph_in_quarter <= min_diopter:
            thicknes_group = self.thickness_list[str(f'{max_diopter:0.2f}')]
            return thicknes_group['CT']       
        for sph, thicknes in self.thickness_list:
            if float(sph) == sph_in_quarter:
                if thicknes['CT']:
                    return thicknes['CT']
                else:
                    return thicknes['ET']


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
            thickness_list = dict_values
            return cls(thickness_list)
        except Exception as error:
            logger.error(f'Error in {error}')


@dataclass
class FrameThicknessList:
    frame_thickenss_list : dict


    def return_frame_thickness_list(self, frame_type: str) -> FrameThickness:
        if frame_type in self.frame_thickenss_list.keys():
            return self.frame_thickenss_list[frame_type]
        else:
            return self.frame_thickenss_list['plastic']


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
            frame_thickenss_list = {frame_type: FrameThickness(frame_thickness) for frame_type, frame_thickness in dict_values.items()}
            return cls(frame_thickenss_list)
        except Exception as error:
            logger.error(f'Error in {error}')
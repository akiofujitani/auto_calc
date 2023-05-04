import tkinter, logging
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog
from dataclasses import dataclass
from PIL import Image, ImageTk
from os.path import normpath, exists
logger = logging.getLogger('gui_classes')


@dataclass
class Configuration_Values:
    '''
    Configuration values dataclass, customize it for your needings
    '''
    def __init__(self) -> None:
        pass


    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        else:
            self_values = self.__dict__
            for key in self_values.keys():
                if not getattr(self, key) == getattr(other, key):
                    return False
            return True


    def check_create_insertion(cls, dict_values=dict):
        '''
        Receive values and transforms it in class
        '''
        pass


    def __dict__(self) -> dict:
        '''
        Custom dict converter
        '''
        pass


@dataclass
class Configuration_Frame:


    def __init__(self) -> None:
        pass


    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        else:
            self_values = self.__dict__
            for key in self_values.keys():
                if not getattr(self, key) == getattr(other, key):
                    return False
            return True
    

    def check_create_insertion(cls, dict_values=dict):
        '''
        Receive values and transforms it in class
        '''
        pass


    def __dict__(self) -> dict:
        '''
        Custom dict converter
        '''
        pass

@dataclass
class Tree_Settings:
    '''
    Tree settings dataclass, customize it for your needings
    '''
    pass


    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        else:
            self_values = self.__dict__
            for key in self_values.keys():
                if not getattr(self, key) == getattr(other, key):
                    return False
            return True


@dataclass
class Config_Frame_Values:
    '''
    - labels_entry_type must use the Keys as Labels to be inserted in Config_Frame GUI and the values must be the type of the entry (str, int, boolean, treeview, path)
    - treeview_columns must be present only in case of treeview entry type, use the referent label name as key to be used to create the treeview columns.
    '''
    labels_entry_type : dict
    treeview_columns : None | dict


    def add_label(self, key=str, value=any):
        if key in self.labels_entry_type.keys():
            raise Exception('Key already exists error')
        self.labels_entry_type[key] = value
    

    def add_treview_columns(self, key, value_list=tuple):
        if key not in self.labels_entry_type.keys():
            raise Exception('Key dont exist in labels')
        self.treeview_columns[key] = value_list


class Edit_Values(tkinter.Toplevel):
    def __init__(self, 
                    parent=ttk.Treeview, 
                    key_list=tuple, 
                    type_list=tuple,
                    edit_title=str, 
                    values_disabled=None, 
                    focus_force=None, 
                    drop_down_list=None,
                    *args, **kwargs) -> None:
        tkinter.Toplevel.__init__(self, *args, **kwargs)
        self.last_grab = self.grab_current()
        self.grab_set()
        self.parent = parent
        self.title(edit_title)
        self.transient()
        self.selected_item = self.parent.selection()[0]
        self.record_value = [str(value) for value in self.parent.item(self.selected_item)['values']]
        self.type_list = type_list
        self.entry_dict = {}
        self.button_dict = {}
        for key_index in range(len(key_list)):
            ttk.Label(self, text=key_list[key_index], justify='left').grid(column=0, row=key_index, padx=(5), pady=(5, 0))
            match type_list[key_index]:
                case 'str' | 'int' :
                    entry = ttk.Entry(self, width=50, justify='center')
                    entry.grid(column=1, row=key_index, sticky='nesw', columnspan=3, padx=(5), pady=(5, 0))
                    entry.insert(tkinter.END, str(self.record_value[key_index]))
                case 'path':
                    entry = ttk.Entry(self, width=50, justify='center')
                    entry.grid(column=1, row=key_index, sticky='nesw', columnspan=2, padx=(5, 0), pady=(5, 0))
                    browse_button = tkinter.Button(self, text='...', width=3)
                    browse_button.grid(column=3, row=key_index, padx=(0, 5), pady=(5, 0))
                    self.button_dict[f'{key_list[key_index]}'] = browse_button
                    self.button_dict[f'{key_list[key_index]}'].configure(command= lambda info=key_list[key_index]: self.__browse_files(info))
                    entry.insert(tkinter.END, str(self.record_value[key_index]))
                case 'boolean':
                    entry = tkinter.BooleanVar()
                    entry.set(self.record_value[key_index] if not self.record_value[key_index] == '' else False)
                    boolean_name = ('True', 'False')
                    radio_bool_button = {}
                    for i in range(len(boolean_name)):
                        radio_bool_button[i] = tkinter.ttk.Radiobutton(self, text=boolean_name[i], value=eval(boolean_name[i]), variable=entry, command=lambda variable=entry: self.__click_radio_bool(variable))
                        radio_bool_button[i].grid(column=1 + i, row=key_index)
                case 'combo_box':
                    entry = ttk.Combobox(self, width=50, justify='center')
                    entry['values'] = drop_down_list[key_list[key_index]]
                    entry.set(str(self.record_value[key_index]) if not str(self.record_value[key_index]) == '' else 'Daily')
                    entry.grid(column=1, row=key_index, sticky='nesw', columnspan=3, padx=(5), pady=(5, 0))
                case _:
                    entry = ttk.Entry(self, width=50, justify='center')
                    entry.grid(column=1, row=key_index, sticky='nesw', columnspan=2, padx=(5), pady=(5, 0))
                    entry.insert(tkinter.END, str(self.record_value[key_index]))
            if not values_disabled == None:
                if key_list[key_index] in values_disabled:
                    entry.configure(state='disabled')
            self.entry_dict[key_list[key_index]] = entry
        if focus_force:
            self.entry_dict[focus_force].focus_force()
            self.entry_dict[focus_force].select_clear()
            self.entry_dict[focus_force].select_range(0, tkinter.END)
        self.bind("<Return>", self.__click_button_save)
        self.bind("<Escape>", lambda *ignore: self.destroy())

        cancel_button = tkinter.Button(self, text='Cancel', command=self.__click_button_cancel, width=15)
        cancel_button.grid(column=1, row=key_index + 1, padx=(5), pady=(5))    
        save_button = tkinter.Button(self, text='Save', command=self.__click_button_save, width=15)
        save_button.grid(column=2, row=key_index + 1, padx=(5), pady=(5))       


    def destroy(self) -> None:
        if self.last_grab:
            self.last_grab.grab_set()
        return super().destroy()


    def __click_radio_bool(self, variable):
        logger.debug(variable.get())


    def __click_button_cancel(self):
        logger.debug('Button cancel')
        if self.__compare_to_empty(''):
            self.parent.delete(self.selected_item)
        self.destroy()
    

    def __compare_to_empty(self, compare_value=str):
        for value in self.record_value:
            if not value == compare_value:
                return False
        return True


    def __click_button_save(self, event=None):
        logger.debug('Button save')
        new_record = []
        diff_found = False        
        entry_dict_keys = list(self.entry_dict.keys())
        for index in range(len(entry_dict_keys)):
            match self.type_list[index]:
                case 'str' | 'int':
                    if self.type_list[index] == 'int':
                        try:
                            value = int(self.entry_dict[entry_dict_keys[index]].get())
                        except:
                            messagebox.showerror('Save error', f'Value must be an integer')
                            self.lift()
                            self.focus_force()
                            self.entry_dict[entry_dict_keys[index]].focus_force()
                            return
                    else:
                        value = str(self.entry_dict[entry_dict_keys[index]].get())
                case 'path':
                    try:
                        if not exists(self.entry_dict[entry_dict_keys[index]].get()):
                            raise Exception('Path error')
                        value = normpath(self.entry_dict[entry_dict_keys[index]].get())
                    except:
                        messagebox.showerror('Save error', f'Invalid or inexistent path')
                        self.lift()
                        self.focus_force()
                        self.entry_dict[entry_dict_keys[index]].focus_force()
                        return
                case 'boolean':
                    value = self.entry_dict[entry_dict_keys[index]].get()
                case 'combo_box':
                    value = self.entry_dict[entry_dict_keys[index]].get()
            new_record.append(value)
            if not self.record_value[index] == value:
                diff_found = True
        if diff_found == True:
            self.parent.item(self.selected_item, values=new_record)
        logger.debug(f'Button save done')
        self.destroy()


    def __browse_files(self, button_id=str):
        logger.debug('Browser files')
        logger.debug(button_id)
        file_path = filedialog.askdirectory(initialdir='/', title='Select the file path')
        if file_path:
            self.entry_dict[button_id].delete(0, tkinter.END)
            self.entry_dict[button_id].insert(tkinter.END, str(normpath(file_path)))
        self.lift()
        logger.debug(f'File path {file_path}')

class Config_Frame(tkinter.Frame):
    def __init__(self, config=Configuration_Values, config_frame_value=Config_Frame_Values, *args, **kwargs) -> None:
        tkinter.Frame.__init__(self, *args, **kwargs)
        self.config = config
        self.labels = config_frame_value.labels_entry_type.keys()
        self.entry_type = config_frame_value.labels_entry_type.values()
        self.treeview_columns = config_frame_value.treeview_columns
        self.entry_list = {}
        button_dict = {}
        config_values = list(self.config.__dict__.values())

        row_value = 0
        for i in range(len(self.labels)):
            ttk.Label(self, text=self.labels[i], justify='left').grid(column=0, row=i, padx=(5), pady=(5, 0))
            match self.entry_type[i]:
                case 'str':
                    entry = ttk.Entry(self, width=40, justify='center')                
                    entry.grid(column=1, row=row_value, columnspan=3, sticky='nesw', padx=(5), pady=(5, 0))
                    entry.insert(tkinter.END, str(config_values[i]))
                case 'int':
                    valid_command = (self.register(self.__validade_values))
                    entry = ttk.Entry(self, width=40, justify='center', validate='key', validatecommand=(valid_command, '%P'))                
                    entry.grid(column=1, row=row_value, columnspan=3, sticky='nesw', padx=(5), pady=(5, 0))
                    entry.insert(tkinter.END, config_values[i])   
                    button_dict[self.labels[i]] = valid_command
                case 'path':
                    entry = ttk.Entry(self, width=40, justify='center')                
                    entry.grid(column=1, row=row_value, columnspan=2, sticky='nesw', padx=(5), pady=(5, 0))
                    browse_button = tkinter.Button(self, text='...', width=3)
                    browse_button.grid(column=3, row=i, padx=(0, 5), pady=(5, 0))
                    button_dict[f'{self.labels[i]}'] = browse_button
                    button_dict[f'{self.labels[i]}'].configure(command=lambda info=self.labels[i]: self.__browse_files(info))
                    entry.insert(tkinter.END, str(config_values[i]))
                case 'boolean':
                    entry = tkinter.BooleanVar()
                    entry.set(config_values[i] if not config_values[i] == '' else False)
                    boolean_name = ('True', 'False')
                    radio_bool_button = {}
                    for i in range(len(boolean_name)):
                        radio_bool_button[i] = tkinter.ttk.Radiobutton(self, text=boolean_name[i], value=eval(boolean_name[i]), variable=entry, command=lambda variable=entry: self.__click_radio_bool(variable))
                        radio_bool_button[i].grid(column=1 + i, row=row_value)
                case 'treeview':
                    entry = ttk.Treeview(self, columns=tuple(self.treeview_columns.keys()), show='headings')
                    for key, value in self.treeview_columns.items():
                        entry.heading(key, text=value)
                        entry.column(key, minwidth=10, width=100)
                    for tree_settings in config_values[i]:
                        entry.insert('', tkinter.END, values=(tuple(tree_settings.__dict__.values())))
                    entry.grid(column=1, row=row_value, columnspan=3, sticky='nesw', padx=(5), pady=(5, 0))
                    entry.bind('<Double-1>', lambda info=self.labels[i]: self.__tree_item_edit(info))
                    entry.bind("<Return>", lambda info=self.labels[i]: self.__tree_item_edit(info))
                    row_value += 1

                    add_button = tkinter.Button(self, text='Add', command=lambda info=self.labels[i]: self.__click_button_add(info), width=15)
                    add_button.grid(column=2, row=row_value, padx=(5, 0), pady=(0,5))
                    button_dict[f'{self.labels[i]}_add']
                    edit_button = tkinter.Button(self, text='Edit', command=lambda info=self.labels[i]: self.__click_button_edit(info), width=15)
                    edit_button.grid(column=3, row=row_value, padx=(0), pady=(0, 5))
                    button_dict[f'{self.labels[i]}_edit']
                    delete_button = tkinter.Button(self, text='Delete', command=lambda info=self.labels[i]: self.__click_button_delete(info), width=15)
                    delete_button.grid(column=4, row=row_value, padx=(0), pady=(0, 5))
                    button_dict[f'{self.labels[i]}_delete']
                case _:
                    entry = ttk.Entry(self, width=40, justify='center')                
                    entry.grid(column=1, row=row_value, columnspan=3, sticky='nesw', padx=(5), pady=(5, 0))
                    entry.insert(tkinter.END, str(config_values[i]))
            row_value += 1
            self.entry_list[self.labels[i]] = entry
        self.columnconfigure(1, weight=1)
    

    def __tree_item_edit(self, entry_label=str, event=None):
        try:
            if self.row_config.state() == 'normal':
                self.row_config.focus_force()
        except Exception as error:
            logger.debug(error)
            try:
                self.entry_list[entry_label].selection()[0]
                self.row_config = Edit_Values(self.entry_list[entry_label], 
                                tuple(self.treeview_columns.keys()),
                                tuple(self.treeview_columns.values()),
                                'Edit settings')
            except:
                messagebox.showerror('Edit error', 'No row is selected')
        logger.debug('Double click')


    def __click_button_add(self, entry_label=str):
        logger.debug('Click button add')
        empty_values = []
        for _ in range(len(self.entry_list[entry_label])):
            empty_values.append('')
        self.self.entry_list[entry_label].insert('', tkinter.END, values=(tuple(empty_values)))
        children_list = self.self.entry_list[entry_label].get_children()
        self.self.entry_list[entry_label].selection_set(children_list[-1])
        self.__tree_item_edit(None)


    def __click_button_edit(self):
        logger.debug('Click button edit')
        self.__tree_item_edit(self)


    def __click_button_delete(self, entry_label=str) -> bool:
        try:
            selected_item = self.entry_list[entry_label].selection()[0]
            logger.debug(selected_item)
            if messagebox.askquestion('Delete', f'Do you really want to delete the item {selected_item}'):
                self.entry_list[entry_label].delete(selected_item)
                return True
            return False
        except:
            messagebox.showerror('Edit error', 'No row is selected')


    def __click_radio_bool(self, variable):
        logger.debug(variable.get())


    # Return updated config values in list form
    # def return_config_updated(self) -> dict:
    #     new_config = []
    #     for i in range(len(self.labels)):
    #         match self.entry_type[i]:
    #             case 'str':
    #                 new_config.append(str(self.entry_list[self.labels[i]].get()))
    #             case 'int':
    #                 new_config.append(int(self.entry_list[self.labels[i]].get()))
    #             case 'path':
    #                 new_config.append(normpath(self.entry_list[self.labels[i]].get()))
    #             case 'boolean':
    #                 new_config.append(eval(str(self.entry_list[self.labels[i]].get())))
    #             case 'treeview':
    #                 treeview_entry = self.entry_list[self.labels[i]]
    #                 new_config.append([treeview_entry.item(value)['values'] for value in treeview_entry.get_children()])
    #     return new_config


    # Return updated config values in dict form
    def return_config_updated(self) -> dict:
        new_config = {}
        for i in range(len(self.labels)):
            match self.entry_type[i]:
                case 'str':
                    new_config[self.labels[i]] = str(self.entry_list[self.labels[i]].get())
                case 'int':
                    new_config[self.labels[i]] = int(self.entry_list[self.labels[i]].get())
                case 'path':
                    new_config[self.labels[i]] = normpath(self.entry_list[self.labels[i]].get())
                case 'boolean':
                    new_config[self.labels[i]] = eval(str(self.entry_list[self.labels[i]].get()))
                case 'treeview':
                    treeview_entry = self.entry_list[self.labels[i]]
                    new_config[self.labels[i]] = [treeview_entry.item(value)['values'] for value in treeview_entry.get_children()]
        return new_config


    def __browse_files(self, button_id=str):
        logger.debug('Browser files')
        logger.debug(button_id)
        file_path = filedialog.askdirectory(initialdir='/', title='Select the file path')
        if file_path:
            self.entry_list[button_id].delete(0, tkinter.END)
            self.entry_list[button_id].insert(tkinter.END, str(normpath(file_path)))
        self.focus_force()
        self.lift()
        logger.debug(f'File path {file_path}')


    def __validade_values(self, value=str):
        if value.isnumeric() or value == '':
            logger.debug(f'{value} is true')
            return True
        else:
            logger.debug(f'{value} is false')
            return False

class Tree_Config_Frame(tkinter.Frame):
    def __init__(self, 
                config=Configuration_Values, 
                file_manag_values=dict, 
                values_type=tuple, 
                edit_win_title=str | None, 
                drop_down_list=None | dict,
                *args, **kwargs) -> None:
        tkinter.Frame.__init__(self, *args, **kwargs)
        self.config = config
        self.values_type = values_type
        self.edit_win_title = edit_win_title
        self.drop_down_list = drop_down_list
        file_manag_column = tuple(list(file_manag_values.keys()))
        self.file_manag_descri = tuple(list(file_manag_values.values()))
        self.file_manag_tree = ttk.Treeview(self, columns=file_manag_column, show='headings')
        for i in range(len(file_manag_column)):
            self.file_manag_tree.heading(file_manag_column[i], text=self.file_manag_descri[i])
            self.file_manag_tree.column(file_manag_column[i], minwidth=10, width=100)
        for directory_list in self.config.directory_list:
            self.file_manag_tree.insert('', tkinter.END, values=(tuple(directory_list.__dict__.values())))
        self.file_manag_tree.bind('<Double-1>', self.__tree_item_edit)
        self.file_manag_tree.bind("<Return>", self.__tree_item_edit)
        self.file_manag_tree.grid(column=1, 
                        row=0, 
                        columnspan=4,
                        sticky='nesw', 
                        padx=(5, 0), 
                        pady=(5, 0))
        y_scrollbar = ttk.Scrollbar(self, orient=tkinter.VERTICAL, command=self.file_manag_tree.yview)
        self.file_manag_tree.configure(yscroll=y_scrollbar.set)
        y_scrollbar.grid(row=0, 
                        column=5, 
                        sticky='ns',
                        padx=(0, 5),
                        pady=(5, 0))
        self.file_manag_tree.columnconfigure(0, weight=1)
        self.file_manag_tree.rowconfigure(0, weight=1)
        self.add_button = tkinter.Button(self, text='Add', command=self.__click_button_add, width=15)
        self.add_button.grid(column=2, row=1, padx=(5, 0), pady=(0,5))
        self.edit_button = tkinter.Button(self, text='Edit', command=self.__click_button_edit, width=15)
        self.edit_button.grid(column=3, row=1, padx=(0), pady=(0, 5))
        self.delete_button = tkinter.Button(self, text='Delete', command=self.__click_button_delete, width=15)
        self.delete_button.grid(column=4, row=1, padx=(0), pady=(0, 5))

    
    def __tree_item_edit(self, event):
        try:
            if self.file_config.state() == 'normal':
                self.file_config.focus_force()
        except Exception as error:
            logger.debug(error)
            try:
                self.file_manag_tree.selection()[0]
                self.file_config = Edit_Values(self.file_manag_tree, 
                                self.file_manag_descri,
                                self.values_type,
                                self.edit_win_title if not self.edit_win_title == None else 'Edit values',
                                drop_down_list=self.drop_down_list)
            except:
                messagebox.showerror('Edit error', 'No row is selected')
        logger.debug('Double click')


    def return_config_updated(self) -> list:
        move_settings_list = [self.file_manag_tree.item(value)['values'] for value in self.file_manag_tree.get_children()]
        return move_settings_list


    def __click_button_add(self):
        empty_values = []
        for _ in range(len(self.file_manag_descri)):
            empty_values.append('')
        self.file_manag_tree.insert('', tkinter.END, values=(tuple(empty_values)))
        children_list = self.file_manag_tree.get_children()
        self.file_manag_tree.selection_set(children_list[-1])
        self.__tree_item_edit(None)


    def __click_button_edit(self):
        self.__tree_item_edit(self)


    def __click_button_delete(self) -> bool:
        try:
            selected_item = self.file_manag_tree.selection()[0]
            logger.debug(selected_item)
            if messagebox.askquestion('Delete', f'Do you really want to delete the item {selected_item}'):
                self.file_manag_tree.delete(selected_item)
                return True
            return False
        except:
            messagebox.showerror('Edit error', 'No row is selected')

class Config_Window(tkinter.Tk):
    def __init__(self, config=Configuration_Values, 
                min_size=tuple,
                config_path=str,
                frame_dict=dict,
                *args, **kwargs) -> None:
        '''
        Default main configuration window        
        ''' 
        tkinter.Tk.__init__(self, *args, **kwargs)
        self.config = config
        self.config_path = config_path
        self.title('Configuration')
        self.minsize(width=min_size[0], height=min_size[1])
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.config_frame_dict = {}
        if len(frame_dict.keys()) > 1:
            self.tab_control = ttk.Notebook(self)
            for frame_name, frame_value in frame_dict.items():
                self.config_frame_dict[frame_name] = Config_Frame(self.config[frame_name], frame_value)
                self.tab_control.add(self.config_frame_dict[frame_name], text=frame_name)
            self.tab_control.grid(column=0, 
                            row=0, 
                            columnspan=6, 
                            sticky='nesw', 
                            padx=(5, 0), 
                            pady=(5, 0))    
        else:
            self.config_frame_dict[frame_name] = Config_Frame(self.config, frame_dict.values()[0])
            self.config_frame_dict[frame_name].grid(column=0, 
                            row=0, 
                            columnspan=6, 
                            sticky='nesw', 
                            padx=(5, 0), 
                            pady=(5, 0))        

        # Buttons
        cancel_button = tkinter.Button(self, text='Cancel', command=self.__click_button_cancel, width=15)
        cancel_button.grid(column=4, row=1, padx=(5), pady=(0, 5))    
        save_button = tkinter.Button(self, text='Save', command=self.__click_button_save, width=15)
        save_button.grid(column=5, row=1, padx=(5), pady=(0, 5))


        self.protocol('WM_DELETE_WINDOW', self.__on_window_close)
        

    def __click_button_cancel(self):
        logger.debug('Cancel click')
        self.__on_window_close()


    def __click_button_save(self):
        logger.debug('Save clicked')

        if len(self.config_frame_dict) > 1:
            configuration_values = {}
            for key, value in self.config_frame_dict.items():
                configuration_values[key] = Configuration_Frame.check_create_insertion(value.return_config_updated)
            new_config = Configuration_Values.check_create_insertion(configuration_values)
        else:
            new_config = Configuration_Values.check_create_insertion(self.config_frame_dict[0])
            '''
            Build universal way to save configuration values
            '''
        if not self.config.__eq__(new_config):
            logger.debug('Not equals')
            json_config.save_json_config(self.config_path, new_config.convert_to_dict())
        self.destroy()


    def __on_window_close(self):
        logger.debug('On close click')
        self.destroy()

# Basic About class
class About(tkinter.Toplevel):
    def __init__(self, title=str, label_values=str, image_file=str, *args, **kwargs) -> None:
        tkinter.Toplevel.__init__(self, *args, **kwargs)
        self.last_grab = self.grab_current()
        self.grab_set()
        self.geometry('450x400')
        self.title(title)
        self.resizable(width=False, height=False)
        image = Image.open(image_file)
        image_tk = ImageTk.PhotoImage(image=image)
        image_label = tkinter.Label(self, image=image_tk, justify='center')
        image_label.image = image_tk
        image_label.grid(column=0, row=0, columnspan=2, padx=(10), pady=(5, 0))

        text_label = tkinter.Label(self, text=label_values, justify='left')
        text_label.grid(column=0, row=1, rowspan=2, sticky='nw', padx=(5), pady=(5, 0))

        ok_button = tkinter.Button(self, text='Ok', width=15, command=self.__pressed_ok_button)
        ok_button.grid(column=1, row=2, sticky='se', padx=(10), pady=(5, 10))

        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=2)
        self.protocol('WM_DELETE_WINDOW', self.__on_window_close)    
        
    def destroy(self) -> None:
        if self.last_grab:
            self.last_grab.grab_set()
        return super().destroy()


    def __pressed_ok_button(self):
        self.__on_window_close()
    

    def __on_window_close(self):
        self.destroy()
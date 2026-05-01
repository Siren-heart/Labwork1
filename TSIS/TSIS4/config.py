import os
from configparser import ConfigParser

def load_config(filename='database.ini', section='postgresql'):
    # Узнаем точный путь к папке, где лежит этот скрипт
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, filename)
    
    parser = ConfigParser()
    # Читаем файл по точному пути
    parser.read(file_path)
    
    config = {}
    if parser.has_section(section):
        for param in parser.items(section):
            config[param[0]] = param[1]
    else:
        # Теперь, если он не найдет файл или заголовок, он выдаст понятную ошибку
        raise Exception(f'Section {section} not found in the {file_path} file')
        
    return config
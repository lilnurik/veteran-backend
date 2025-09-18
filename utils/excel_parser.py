"""
Excel parser utility for importing comrades data from Excel files.
Supports importing multiple comrades at once from standardized Excel format.
"""

import pandas as pd
import json
from datetime import datetime
from typing import List, Dict, Any, Tuple


class ExcelParserError(Exception):
    """Custom exception for Excel parsing errors"""
    pass


class ComradeExcelParser:
    """Parser for comrades data from Excel files"""
    
    # Required columns for Excel import
    REQUIRED_COLUMNS = [
        'Фамилия',  # Last name
        'Имя',      # First name  
        'Воинская часть',  # Unit
        'Регион',   # Region
        'Год службы с'  # Year of service from
    ]
    
    # Optional columns
    OPTIONAL_COLUMNS = [
        'Отчество',      # Middle name
        'Год службы по', # Year of service to
        'Звание',        # Rank
        'Телефон',       # Phone
        'Email',         # Email
        'Адрес',         # Address
        'Дополнительная информация'  # Additional info
    ]
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_excel_file(self, file_path: str) -> Tuple[bool, List[str]]:
        """
        Validate that the Excel file has the correct format
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            errors = []
            
            # Check if file is empty
            if df.empty:
                errors.append("Excel файл пуст")
                return False, errors
            
            # Check required columns
            missing_columns = []
            for col in self.REQUIRED_COLUMNS:
                if col not in df.columns:
                    missing_columns.append(col)
            
            if missing_columns:
                errors.append(f"Отсутствуют обязательные колонки: {', '.join(missing_columns)}")
            
            # Check if there's at least one valid row
            if len(df) == 0:
                errors.append("В файле нет данных для импорта")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            return False, [f"Ошибка чтения Excel файла: {str(e)}"]
    
    def parse_excel_file(self, file_path: str) -> Tuple[List[Dict[str, Any]], List[str], List[str]]:
        """
        Parse Excel file and extract comrades data
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            Tuple of (comrades_data, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        comrades_data = []
        
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Validate file format first
            is_valid, validation_errors = self.validate_excel_file(file_path)
            if not is_valid:
                self.errors.extend(validation_errors)
                return [], self.errors, self.warnings
            
            # Process each row
            for index, row in df.iterrows():
                try:
                    comrade_data = self._parse_row(row, index + 1)
                    if comrade_data:
                        comrades_data.append(comrade_data)
                except Exception as e:
                    self.errors.append(f"Строка {index + 1}: {str(e)}")
            
            return comrades_data, self.errors, self.warnings
            
        except Exception as e:
            self.errors.append(f"Ошибка обработки файла: {str(e)}")
            return [], self.errors, self.warnings
    
    def _parse_row(self, row: pd.Series, row_number: int) -> Dict[str, Any]:
        """
        Parse a single row from Excel file
        
        Args:
            row: Pandas Series representing a row
            row_number: Row number for error reporting
            
        Returns:
            Dictionary with comrade data
        """
        comrade_data = {}
        
        # Check for empty rows
        if row.isna().all():
            return None
        
        # Required fields
        last_name = self._get_string_value(row, 'Фамилия', row_number, required=True)
        first_name = self._get_string_value(row, 'Имя', row_number, required=True)
        unit = self._get_string_value(row, 'Воинская часть', row_number, required=True)
        region = self._get_string_value(row, 'Регион', row_number, required=True)
        year_from = self._get_year_value(row, 'Год службы с', row_number, required=True)
        
        if not all([last_name, first_name, unit, region, year_from]):
            raise ValueError("Пропущены обязательные поля")
        
        comrade_data.update({
            'firstName': first_name,
            'lastName': last_name,
            'unit': unit,
            'region': region,
            'yearOfServiceFrom': year_from
        })
        
        # Optional fields
        middle_name = self._get_string_value(row, 'Отчество', row_number, required=False)
        if middle_name:
            comrade_data['middleName'] = middle_name
        
        year_to = self._get_year_value(row, 'Год службы по', row_number, required=False)
        if year_to:
            comrade_data['yearOfServiceTo'] = year_to
        
        rank = self._get_string_value(row, 'Звание', row_number, required=False)
        if rank:
            comrade_data['rank'] = rank
        
        additional_info = self._get_string_value(row, 'Дополнительная информация', row_number, required=False)
        if additional_info:
            comrade_data['additionalInfo'] = additional_info
        
        # Contact info
        contact_info = {}
        phone = self._get_string_value(row, 'Телефон', row_number, required=False)
        if phone:
            contact_info['phone'] = phone
        
        email = self._get_string_value(row, 'Email', row_number, required=False)
        if email:
            contact_info['email'] = email
        
        address = self._get_string_value(row, 'Адрес', row_number, required=False)
        if address:
            contact_info['address'] = address
        
        if contact_info:
            comrade_data['contactInfo'] = contact_info
        
        return comrade_data
    
    def _get_string_value(self, row: pd.Series, column: str, row_number: int, required: bool = False) -> str:
        """Get string value from row, handling NaN values"""
        if column not in row.index:
            if required:
                raise ValueError(f"Отсутствует колонка '{column}'")
            return None
        
        value = row[column]
        if pd.isna(value):
            if required:
                raise ValueError(f"Пустое значение в обязательном поле '{column}'")
            return None
        
        # Special handling for phone numbers to preserve leading +
        if column == 'Телефон' and isinstance(value, (int, float)):
            # If it's a number, it likely lost the + prefix
            return f"+{int(value)}"
        
        return str(value).strip()
    
    def _get_year_value(self, row: pd.Series, column: str, row_number: int, required: bool = False) -> int:
        """Get year value from row, handling various formats"""
        if column not in row.index:
            if required:
                raise ValueError(f"Отсутствует колонка '{column}'")
            return None
        
        value = row[column]
        if pd.isna(value):
            if required:
                raise ValueError(f"Пустое значение в обязательном поле '{column}'")
            return None
        
        try:
            # Handle different formats
            if isinstance(value, (int, float)):
                year = int(value)
            elif isinstance(value, str):
                # Remove any extra characters and convert
                year_str = ''.join(filter(str.isdigit, value))
                if not year_str:
                    raise ValueError(f"Неверный формат года в поле '{column}': {value}")
                year = int(year_str)
            else:
                raise ValueError(f"Неверный тип данных в поле '{column}': {type(value)}")
            
            # Validate year range
            current_year = datetime.now().year
            if year < 1900 or year > current_year:
                raise ValueError(f"Год должен быть в диапазоне 1900-{current_year}, получен: {year}")
            
            return year
            
        except (ValueError, TypeError) as e:
            if required:
                raise ValueError(f"Ошибка в поле '{column}': {str(e)}")
            self.warnings.append(f"Строка {row_number}: Пропущен год в поле '{column}': {value}")
            return None
    
    def create_sample_excel(self, file_path: str) -> None:
        """
        Create a sample Excel file with correct format for import
        
        Args:
            file_path: Path where to save the sample file
        """
        sample_data = {
            'Фамилия': ['Иванов', 'Петров', 'Сидоров'],
            'Имя': ['Иван', 'Петр', 'Алексей'],
            'Отчество': ['Петрович', 'Иванович', 'Александрович'],
            'Воинская часть': ['Воинская часть 12345', 'Авиабаза Хурба', '201-я мотострелковая дивизия'],
            'Регион': ['Ташкентская область', 'Хабаровский край', 'Московская область'],
            'Год службы с': [1990, 1985, 1992],
            'Год службы по': [1992, 1987, 1994],
            'Звание': ['Сержант', 'Старший лейтенант', 'Рядовой'],
            'Телефон': ['+998901234567', '+79161234567', '+79991234567'],
            'Email': ['ivanov@example.com', 'petrov@example.com', 'sidorov@example.com'],
            'Адрес': ['г. Ташкент, ул. Примерная 123', 'г. Хабаровск, ул. Тестовая 456', 'г. Москва, ул. Образцовая 789'],
            'Дополнительная информация': ['Служил в танковых войсках', 'Военный летчик', 'Связист']
        }
        
        df = pd.DataFrame(sample_data)
        df.to_excel(file_path, index=False)
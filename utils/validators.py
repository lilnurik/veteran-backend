from datetime import datetime

def validate_multilang_field(data, field_name, required=True):
    """Validate multilingual field structure"""
    errors = {}
    
    if field_name not in data:
        if required:
            errors[field_name] = f"{field_name} is required"
        return errors
    
    field_data = data[field_name]
    if not isinstance(field_data, dict):
        errors[field_name] = f"{field_name} must be an object"
        return errors
    
    for lang in ['ru', 'uz', 'en']:
        if lang not in field_data:
            if required:
                errors[f"{field_name}.{lang}"] = f"{field_name} in {lang} is required"
        elif not field_data[lang] or not field_data[lang].strip():
            if required:
                errors[f"{field_name}.{lang}"] = f"{field_name} in {lang} cannot be empty"
    
    return errors

def validate_date_field(data, field_name, required=True):
    """Validate date field in YYYY-MM-DD format"""
    errors = {}
    
    if field_name not in data:
        if required:
            errors[field_name] = f"{field_name} is required"
        return errors
    
    date_str = data[field_name]
    if not date_str:
        if required:
            errors[field_name] = f"{field_name} cannot be empty"
        return errors
    
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        errors[field_name] = f"{field_name} must be in YYYY-MM-DD format"
    
    return errors

def validate_contact_info(contact_data):
    """Validate contact info structure"""
    errors = {}
    
    if not isinstance(contact_data, dict):
        return {'contactInfo': 'Contact info must be an object'}
    
    # Optional fields validation
    if 'phone' in contact_data and contact_data['phone']:
        phone = contact_data['phone'].strip()
        if not phone.startswith('+') or len(phone) < 10:
            errors['contactInfo.phone'] = 'Phone must start with + and be at least 10 characters'
    
    if 'email' in contact_data and contact_data['email']:
        email = contact_data['email'].strip()
        if '@' not in email or '.' not in email:
            errors['contactInfo.email'] = 'Invalid email format'
    
    return errors

def validate_year_range(year_from, year_to=None):
    """Validate year range"""
    errors = {}
    current_year = datetime.now().year
    
    if not isinstance(year_from, int) or year_from < 1900 or year_from > current_year:
        errors['yearOfServiceFrom'] = f'Year from must be between 1900 and {current_year}'
    
    if year_to is not None:
        if not isinstance(year_to, int) or year_to < 1900 or year_to > current_year:
            errors['yearOfServiceTo'] = f'Year to must be between 1900 and {current_year}'
        elif year_from and year_to < year_from:
            errors['yearOfServiceTo'] = 'Year to cannot be earlier than year from'
    
    return errors

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Environments vars
security_user = os.environ.get('SECURITY_USER')

"""
    Security password has to be encrypted with generate_password_hash, and added
    to environment system vars
    
    Example to encrypt the password:
    
    hashed_password = generate_password_hash("yourPassword", method='sha256')
    
"""
password_security_user = os.environ.get('PASSWORD_SECURITY_USER')


###########################################################################################

"""
       True if authentication is OK, False otherwise.
"""
def authenticate_user(username,password):
    
    check_password = check_password_hash(password_security_user,password)
    
    if(check_password and security_user == username):
        return True
    else:
        return False

###########################################################################################
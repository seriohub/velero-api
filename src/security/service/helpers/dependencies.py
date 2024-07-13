from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
# from helpers.printer import PrintHelper

# print_ls = PrintHelper('[lib.dependencies]')

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/token')

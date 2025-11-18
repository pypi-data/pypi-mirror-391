import time
import shutil
from paper_inbox.modules.const import BEAT 
from paper_inbox.modules.tui.utils import spinner

@spinner("Checking if UV is installed...")
def is_uv_installed():
    time.sleep(BEAT)
    has_uv = True if shutil.which("uv") else False
    return has_uv

@spinner("Checking if CUPS is installed...")
def is_cups_installed():
    time.sleep(BEAT)
    has_cups = True if shutil.which("lpstat") else False
    return has_cups

@spinner("Checking if wkhtmltopdf is installed...")
def is_wkhtmltopdf_installed():
    time.sleep(BEAT)
    has_wkhtmltopdf = True if shutil.which("wkhtmltopdf") else False
    return has_wkhtmltopdf

@spinner("Checking if LibreOffice is installed...")
def is_libreoffice_installed():
    time.sleep(BEAT)
    has_libreoffice = True if shutil.which("libreoffice") else False
    return has_libreoffice
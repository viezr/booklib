'''
Unzip fb2.zip files.
'''
from os import path
from tempfile import mkdtemp
from zipfile import ZipFile


def unzip_fb2(file: str, prefix: str = "unzip_fb2_") -> [str, None]:
    '''
    Unzip fb2.zip files to temporary folder and return path to file.
    '''
    tmp_file = tmp_path = tmp_filename = None
    fb2zip = ZipFile(file)
    files = fb2zip.namelist()
    for infile in files:
        if infile.endswith(".fb2"):
            try:
                tmp_filename = infile
                tmp_path = path.normpath(mkdtemp(prefix=prefix))
                tmp_file = path.join(tmp_path, tmp_filename)
                fb2zip.extract(infile, tmp_path)
            except:
                return None
    if tmp_file:
        return tmp_file
    return None

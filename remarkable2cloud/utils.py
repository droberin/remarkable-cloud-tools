from io import BytesIO
from _io import BufferedReader
from zipfile import ZipFile, ZIP_DEFLATED


def construct_zip_payload(files: list):
    buf = BytesIO()
    with ZipFile(buf, mode="w", compression=ZIP_DEFLATED, allowZip64=False, compresslevel=0) as zip_file:
        for document in files:
            if type(document['content']) == BufferedReader:
                zip_file.writestr(document['name'], document['content'].read())
            else:
                zip_file.writestr(document['name'], document['content'])
    return buf

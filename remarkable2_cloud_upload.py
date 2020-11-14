from remarkable2cloud import ReMarkableCloud, ReMarkableConfiguration
from sys import exit
from os.path import isfile
import argparse
import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install('INFO', logger=logger)

rM_config = None
try:
    rM_config = ReMarkableConfiguration()
except ValueError as e:
    logger.error(e)
    exit(1)

parser = argparse.ArgumentParser(description='upload files to reMarkable2 via Cloud.')
parser.add_argument('-d', '--device', dest='device_name', default="reMarkable2",
                    help='Chooses target device. (Default: reMarkable2 / "config file default")')
parser.add_argument('filename')
args = parser.parse_args()
device_name = args.device_name
filename = args.filename

rM = None
if not isfile(filename):
    logger.critical(f"Could not find file {filename}")
    exit(1)

try:
    rM = ReMarkableCloud(rM_config.get_device_token(device_name))
except ValueError as e:
    logger.critical(f"Error loading configuration for device {device_name}")
    exit(2)

uploaded_uuid = rM.upload_file(filename)
if not uploaded_uuid:
    logger.error(f"Failed to upload")
    exit(1)
logger.info('Upload process finished.')

import logging
import os
import time
from utils.github import Github
from utils.image import SkateParkImage

logging.basicConfig(level=os.getenv('LOG', 'DEBUG'))
logger = logging.getLogger(__name__)


SkatePark = SkateParkImage()
park_list = SkatePark.get_name_list()

for park in park_list:
    logger.info(park)
    try:
        b64_file = SkatePark.get_image(location=park)

        logger.info(
            "B64 file True") if b64_file is not None else logger.info("False")
    except Exception as e:
        logger.warning(f'Park: {park} crawler error')
        logger.warning(e)

    github = Github()
    logger.info('Skate Park is : ' + park)
    get_result = github.get_record(path=f"images/{park}/default.png")
    logger.info('select data is: ' + str(get_result.get("content") is not None))
    file_sha = get_result.get('sha')
    if b64_file is not None and get_result.get('content') is not None:
        delete_result = github.delete_file(park, "default", sha=file_sha)
        logger.info('Delete file data status: ' +
                    str(delete_result.get("content")))
    time.sleep(1)
    if b64_file is not None:
        upload_result = github.upload_file(park, "default", b64_file)
        logger.info('Upload file status: ' +
                    str(upload_result.get("content") is not None))
    time.sleep(1)

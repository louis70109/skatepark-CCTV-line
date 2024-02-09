import logging
import os
import time
import requests
from utils.common import get_current_time_period
from utils.github import Github
from utils.image import SkateParkImage

logger = logging.getLogger(__name__)


SkatePark = SkateParkImage()
park_list = SkatePark.get_name_list()

for park in park_list:
    logger.info(park)
    try:
        b64_file = SkatePark.get_image(location=park)
        current_timestamp = get_current_time_period()
        try:
            github = Github()
            res = requests.put(
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {os.getenv('GITHUB')}"
                },
                json={
                    "message": "✨ Commit from CCTV LINE Bot",
                    "committer": {"name": "NiJia Lin", "email": "louis70109@gmail.com"},
                    "content": b64_file,
                    "branch": "master"},
                url=f"https://api.github.com/repos/{github.repo_name}/contents/images/{park}/{current_timestamp}.png"
            )
            response_msg = res.json()
            print(response_msg)
            time.sleep(5)
        except Exception as e:
            logger.warning(f'Image upload to GitHub error, Error is: {e}')
    except:
        continue

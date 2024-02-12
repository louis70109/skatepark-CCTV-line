import logging
import requests
import base64
import os
from datetime import datetime
logger = logging.getLogger(__name__)

class Github:
    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.repo_name = 'louis70109/ideas-tree'  # change to your repo name
        self.file = self.today + '.md'
        self.github = os.getenv('GITHUB', None)

    def get_record(self, path=None) -> dict:
        if path is None:
            path = self.file
        git_url = f"https://api.github.com/repos/{self.repo_name}/contents/{path}"
        logger.info(git_url)
        res = requests.get(
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"token {self.github}"
            },
            url=git_url
        )
        if res.status_code >= 400:
            logger.debug(f'❌ GitHub repo record is None. Info: {res.json()}')

        return res.json()

    def new_or_update_record(self, text: str, today_record: str = None, sha: str = None) -> dict:
        git_url = f"https://api.github.com/repos/{self.repo_name}/contents/{self.file}"

        text = self.markdown_to_html(text)

        update_sha = {}
        # If contain SHA, means content exist.
        if sha != None:
            record = base64.b64decode(today_record).decode('UTF-8')
            text = f'{record}<br />{text}'
            update_sha = {'sha': sha}

        res = requests.put(
            headers={
                "Accept": "application/vnd.github.VERSION.raw",
                "Authorization": f"token {self.github}"
            },
            json={
                "message": f"✨{self.today} Commit",
                "committer": {"name": "NiJia Lin", "email": os.getenv('EMAIL')},
                "content": base64.b64encode(text.encode('UTF-8')).decode('utf-8'),
                "branch": "master", **update_sha},
            url=git_url
        )
        if res.status_code >= 400:
            logger.warning(f'❌ GitHub Record create || update fail. Info: {res.json()}')
            return None
        return res.json()

    def upload_file(self, folder, file_name, b64_file):
        try:
            res = requests.put(
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {self.github}"
                },
                json={
                    "message": "✨ Commit from CCTV LINE Bot",
                    "committer": {"name": "NiJia Lin", "email": "louis70109@gmail.com"},
                    "content": b64_file,
                    "branch": "master"},
                url=f"https://api.github.com/repos/{self.repo_name}/contents/images/{folder}/{file_name}.png"
            )
            response_msg = res.json()
            logger.debug('GitHub upload file is: ')
            logger.debug(response_msg)
            return response_msg
        except Exception as e:
            logger.warning(f'Image upload to GitHub error, Error is: {e}')
    
    def delete_file(self, folder, file_name, sha):
        try:

            res = requests.delete(
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {self.github}"
                },
                json={
                    "message": "✨ Delete from CCTV LINE Bot",
                    "committer": {"name": "NiJia Lin", "email": "louis70109@gmail.com"},
                    "branch": "master",'sha': sha},
                url=f"https://api.github.com/repos/{self.repo_name}/contents/images/{folder}/{file_name}.png"
            )
            response_msg = res.json()
            logger.debug('GitHub Delete file is: ')
            logger.debug(response_msg)
            return response_msg
        except Exception as e:
            logger.warning(f'Image upload to GitHub error, Error is: {e}')

    @staticmethod
    def markdown_to_html(contents):
        res = requests.post(headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"token {self.github}"
        }, url="https://api.github.com/markdown",
        json={"text": contents})
        
        if res.status_code == 200:
            return res.text
        if res.status_code>=400:
            logger.warning(f'❌ Markdown format error. Info: {res.json()}')
            return None
    
    @staticmethod
    def record_judgement():
        pass
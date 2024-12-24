from config import *

import requests
import logging
import os

from tqdm import tqdm

import re
import time

# Configure logging
logging.basicConfig(
    filename=LOG_PATH, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def save_pdf(paper_id, save_path):
    max_retries = MAX_RETRY
    retry_delay = 1  # initial delay in seconds

    for attempt in range(max_retries):
        try:
            response = requests.get(f"{DOWNLOAD_API}/pdf/{paper_id}")
            if response.status_code == 200:
                with open(f"{save_path}/{paper_id}/{paper_id}.pdf", "wb") as f:
                    f.write(response.content)
                return  # success, exit the function
            else:
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries}: Failed to download {paper_id}, status code: {response.status_code}"
                )
        except Exception as e:
            logger.error(
                f"Attempt {attempt + 1}/{max_retries}: Error downloading {paper_id}: {str(e)}"
            )

        if attempt < max_retries - 1:  # don't sleep on the last attempt
            time.sleep(retry_delay)
            retry_delay *= 2  # exponential backoff

    logger.error(f"Failed to download {paper_id} after {max_retries} attempts")


def save_tex(paper_id, save_path):
    max_retries = MAX_RETRY
    retry_delay = 1  # initial delay in seconds

    for attempt in range(max_retries):
        try:
            response = requests.get(f"{DOWNLOAD_API}/src/{paper_id}")
            if response.status_code == 200:
                filename = response.headers.get("content-disposition", "").split(
                    "filename="
                )[-1]
                if not filename:
                    filename = f"{paper_id}.tar.gz"
                with open(f"{save_path}/{paper_id}/{filename}", "wb") as f:
                    f.write(response.content)
                return  # success, exit the function
            else:
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries}: Failed to download {paper_id}, status code: {response.status_code}"
                )
        except Exception as e:
            logger.error(
                f"Attempt {attempt + 1}/{max_retries}: Error downloading {paper_id}: {str(e)}"
            )

        if attempt < max_retries - 1:  # don't sleep on the last attempt
            time.sleep(retry_delay)
            retry_delay *= 2  # exponential backoff

    logger.error(f"Failed to download {paper_id} after {max_retries} attempts")


def download_paper(paper_id):
    if not os.path.exists(os.path.join(DOWNLOAD_PATH, paper_id)):
        os.makedirs(os.path.join(DOWNLOAD_PATH, paper_id))
    save_pdf(paper_id, DOWNLOAD_PATH)
    save_tex(paper_id, DOWNLOAD_PATH)


def read_paper_list(path):
    # traverse the path contains csv files
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".csv"):
                with open(os.path.join(root, file), "r") as f:
                    lines = f.readlines()
                    for line in lines[1:]:
                        paper_id = re.match(r"(\d+\.\d+)", line).group(1)
                        title = re.match(r'.*?"(.*?)"', line).group(1)
                        yield paper_id, title


def download_all_papers(path):
    for paper_id, title in tqdm(read_paper_list(path)):
        download_paper(paper_id)
        logger.info(f"Downloaded {title}")


if __name__ == "__main__":
    download_all_papers(LIST_PATH)

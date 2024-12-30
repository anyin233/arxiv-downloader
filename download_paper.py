from config import *

import requests
import logging
import os

from tqdm import tqdm

import re
import time

import argparse
import shutil

# Configure logging
logging.basicConfig(
    filename=LOG_PATH, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def save_paper(paper_id, DOWNLOAD_PATH):
    max_retries = MAX_RETRY
    retry_delay = 1  # initial delay in seconds

    for attempt in range(max_retries):
        try:
            if os.path.exists(f"{DOWNLOAD_PATH}/{paper_id}/{paper_id}.pdf"):
                return # already downloaded
            # clear all the file under the folder
            for file in os.listdir(f"{DOWNLOAD_PATH}/{paper_id}"):
                file_path = os.path.join(f"{DOWNLOAD_PATH}/{paper_id}", file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            response = requests.get(f"{DOWNLOAD_API}/{paper_id}")
            if response.status_code == 200:
                filename = response.headers.get("content-disposition", "").split(
                    "filename="
                )[-1]
                if not filename:
                    filename = f"{paper_id}.zip"
                with open(f"{DOWNLOAD_PATH}/{paper_id}/{filename}", "wb") as f:
                    f.write(response.content)
                # unzip the file
                # check if the destination folder contains {paper_id}.pdf
                os.system(
                    f"unzip {DOWNLOAD_PATH}/{paper_id}/{filename} -d {DOWNLOAD_PATH}/{paper_id}"
                )
                # remove the zip file
                os.remove(f"{DOWNLOAD_PATH}/{paper_id}/{filename}")
                return  # success, exit the function
            else:
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries}: Failed to download {paper_id}, status code: {response.status_code}"
                )
        except Exception as e:
            logger.error(
                f"Attempt {attempt + 1}/{max_retries}: Error downloading {paper_id}: {str(e)}"
            )

        if attempt < max_retries - 1:  # don't sleep on the
            time.sleep(retry_delay)
            retry_delay *= 2


def download_paper(paper_id, download_path):
    if not os.path.exists(os.path.join(download_path, paper_id)):
        os.makedirs(os.path.join(download_path, paper_id))
    save_paper(paper_id, download_path)


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


def download_all_papers(args):
    path = args.list_path
    download_path = args.download_path
    for paper_id, title in tqdm(read_paper_list(path)):
        download_paper(paper_id, download_path)
        logger.info(f"Downloaded {title}")


def parse_args():
    parser = argparse.ArgumentParser(description="Download papers from arXiv")
    parser.add_argument(
        "--list_path",
        type=str,
        default=LIST_PATH,
        help="Path to the list of papers",
    )
    parser.add_argument(
        "--download_path",
        type=str,
        default=DOWNLOAD_PATH,
        help="Path to download the papers",
    )
    parser.add_argument(
        "--log_path",
        type=str,
        default=LOG_PATH,
        help="Path to the log file",
    )
    parser.add_argument(
        "--max_retry",
        type=int,
        default=MAX_RETRY,
        help="Maximum number of retries",
    )
    parser.add_argument(
        "--download_api",
        type=str,
        default=DOWNLOAD_API,
        help="API to download the papers",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    download_all_papers(args)

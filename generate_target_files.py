import os 
import re
import argparse
import subprocess
import shutil
from tqdm import tqdm
import logging
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  handlers=[
    logging.FileHandler('run.log')
  ]
)
logger = logging.getLogger(__name__)

CHAT_MODEL_NAME="o1-preview"

def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument("-i", "--input", type=str, help="Path to the papers")
  parser.add_argument("-l", "--list", type=str, help="Path to the list of papers")

  return parser.parse_args()

def read_paper_list(path):
    with open(path, "r") as f:
      return [line.strip() for line in f.readlines()]
    
      
def check_pandoc():
  if os.system("pandoc --version") != 0:
    print("Please install pandoc first")
    exit(1)
  
def process_single_file(path, paper_id):
  # Get the name of source code pack
  file_list = os.listdir(path)
  source_file = None
  for file in file_list:
    if file.endswith(".tar.gz") or file.endswith(".zip") or file.endswith(".tar"):
      source_file = file
      break
  if source_file is None:
    logging.error(f"No source code pack in {path}")
    return -1
  # Unpack the source code pack
  temp_dirname = "tmp/tmp_{}".format(paper_id)
  if os.path.exists(temp_dirname):
    shutil.rmtree(temp_dirname, ignore_errors=True)
  os.makedirs(temp_dirname, exist_ok=True)
  source_file = os.path.join(path, source_file)
  if file.endswith(".zip"):
    os.system(f"unzip {source_file} -d {temp_dirname} > /dev/null 2>&1")
  elif file.endswith(".tar.gz"):
    os.system(f"tar -zxvf {source_file} -C {temp_dirname} > /dev/null 2>&1") 
  elif file.endswith(".tar"):
    os.system(f"tar -xvf {source_file} -C {temp_dirname} > /dev/null 2>&1")
  else:
    extension = source_file.split(".")[-1]
    logging.error(f"Unsupported extension {extension}")
    return -2
  # Find main tex file
  # What is main tex file?
  # Main tex file is the file that contains \begin{document}
  main_tex = None
  for root, dirs, files in os.walk(temp_dirname):
    for file in files:
      if file.endswith(".tex"):
        with open(os.path.join(root, file), "r") as f:
          content = f.read()
          if "\\begin{document}" in content:
            main_tex = file
            break
  if main_tex is None:
    logging.error(f"No main tex file in {path}")
    return -3
  
  bib_file = None
  for root, dirs, files in os.walk(temp_dirname):
    for file in files:
      if file.endswith(".bib"):
        bib_file = os.path.join(root, file)
        # Convert absolute path to relative path from tmp directory
        bib_file = os.path.relpath(bib_file, temp_dirname)
        break
  if bib_file is None:
    logging.warning(f"No bib file in {path}")
  
  # Convert tex to markdown
  command_to_markdown = ["pandoc", "-f", "latex", "-t", "markdown", "-C", "--bibliography", bib_file, "--reference-links", "--reference-location", "document", main_tex, "-o", f"{paper_id}.md"]
  
  # print(" ".join(command_to_markdown))
  try:
    subprocess.run(command_to_markdown, cwd=temp_dirname, capture_output=True, timeout=120)
  except subprocess.TimeoutExpired:
    logger.error(f"Pandoc conversion timed out after 120s for {paper_id}")
    return -4
  shutil.move(f"{temp_dirname}/{paper_id}.md", f"{path}/{paper_id}.md")
  if os.path.exists(temp_dirname):
    shutil.rmtree(temp_dirname, ignore_errors=True)
  return

def main():
  args = parse_args()
  check_pandoc()
  paper_list = read_paper_list(args.list)
  print("Total number of papers: ", len(paper_list))
  # Use number of CPU cores for thread count
  num_threads = multiprocessing.cpu_count()
  
  def process_paper(paper_id):
    try:
      process_single_file(os.path.join(args.input, paper_id), paper_id)
    except Exception as e:
      logger.error(f"Error processing {paper_id}: {e}")

  with ThreadPoolExecutor(max_workers=16) as executor:
    futures = [executor.submit(process_paper, paper_id) for paper_id in paper_list]
    for future in tqdm(futures, total=len(paper_list)):
      try:
        future.result(timeout=360)
      except TimeoutError:
        logger.error("Processing paper timed out after 120s") 
  return

# check_pandoc()
# process_single_file("/data/yyw/datasets/arxiv-paper/2407.00001", "2407.00001")
if __name__ == "__main__":
  main()
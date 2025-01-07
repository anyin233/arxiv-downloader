from tqdm import tqdm
import os
import argparse

def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument("-i", "--input", type=str, help="Path to the list of papers")

  return parser.parse_args()

def read_paper_list(path):
    # traverse the path contains csv files
    id_list = []
    print("Reading paper list")
    pbar = tqdm(os.listdir(path))
    for dirs in pbar:
      pbar.set_description(f"Processing {dirs}, Total papers: {len(id_list)}")
      paper_id = dirs
      file_list = os.listdir(os.path.join(path, dirs))
      have_source = False
      for file in file_list:
        if file.endswith(".tar.gz") or file.endswith(".zip") or file.endswith(".tar"):
          have_source = True
          break
      if have_source:
        id_list.append(paper_id)
    return id_list
  
if __name__ == "__main__":
  args = parse_args()
  id_list = read_paper_list(args.input)
  print("Total papers:", len(id_list))
  with open("paper_list.txt", "w") as f:
    for paper_id in id_list:
      f.write(f"{paper_id}\n")
  print("Paper list saved to paper_list.txt")
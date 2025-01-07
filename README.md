# arxiv paper downloader

## Prerequisites


> **Important❗❗❗**: Please deploy your own cloudflare worker with script in [this repo](https://github.com/anyin233/arxiv-download-worker)

### Edit your config.py

```python
# Variables for list generator
BASE_URL = "https://arxiv.org" # url of arxiv
FIELD = "physics" # field, can be found here: https://arxiv.org/category_taxonomy 
START_YEAR = "2024"
END_YEAR = "2024"
LIST_PATH = "./year_list" # path to put your list

DOWNLOAD_API = # endpoint of your own worker
DOWNLOAD_PATH = # path to save your paper
LOG_PATH = "./warning.log"
MAX_RETRY = 5
```

### Install Dependiences

```bash
pip install -r requirements.txt
```

## How to use 

### 1. Generate paper list

```bash
python build_list.txt
```

### 2. Download papers

```bash
python download_paper.py
```

### 3. Structure of Paper

```
<output_dir>
|
|--<arxiv_paper_id>
|--|--<arxiv_paper_id>.pdf
|--|--<source_code_of_paper>
|
|--<arxiv_paper_id>
|--|--<arxiv_paper_id>.pdf
|--|--<source_code_of_paper>
|
|--<arxiv_paper_id>
|--|--<arxiv_paper_id>.pdf
|--|--<source_code_of_paper>
```

## Some useful tools

### Paper2md

> `<output_dir>` in the 3. Structure of Paper == `/path/to/papers` here

**Usage:**

1. Build task lists

```bash
python utils/paper2md/process_dataset_list.py -i /path/to/papers
```

2. Transform them to markdown

```bash
python utils/paper2md/generate_target_file -i /path/to/papers -l paper_list.txt
```

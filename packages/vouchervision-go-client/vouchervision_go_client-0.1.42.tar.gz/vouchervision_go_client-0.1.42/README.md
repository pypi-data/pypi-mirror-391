# VoucherVisionGO Client

This repository contains only the client component of [VoucherVisionGO](https://github.com/Gene-Weaver/VoucherVisionGO), a tool for automatic label data extraction from museum specimen images.

## About
Last synchronized: Fri Jun 20 18:07:41 UTC 2025

This is a mirror of the `client.py` file from the main VoucherVisionGO repository. It is automatically synchronized when the original file is updated to ensure you always have the latest version.

## Purpose

This repository is designed for users who only need the client component without the full VoucherVisionGO codebase, allowing for:
- Easier integration into existing projects
- Smaller footprint
- Focused functionality
- Simple installation process

## Information 
VoucherVision is designed to transcribe museum specimen labels. Please see the [VoucherVision Github](https://github.com/Gene-Weaver/VoucherVision) for more information. 

As of March 2025, the University of Michigan is allowing free access to VoucherVision. The API is hosted on-demand. It takes about 1 minute for the server to wake up, then subsequent calls are much faster. The API is parallelized and scalable, making this inference much faster than the regular VoucherVision deployment. The tradeoff is that you have less control over the transcription methods. The API supports Google's "gemini-1.5-pro" and "gemini-2.0-flash" for OCR and uses "gemini-2.0-flash" for parsing the unformatted text into JSON. If you want pure speed, use only "gemini-2.0-flash" for both tasks. 

If you want to transcribe different fields, reach out and I can help you develop a prompt or upload your existing prompt to make it available on the API. 

## Requirements

- Python 3.10 or higher
- External dependencies (see installation options below)

## Authentication

To use the API you need to apply for an authorization token. Go to the [login page](https://vouchervision-go-738307415303.us-central1.run.app/login) and submit your info. 
Copy the token and store it in a safe location. Never put the token directly into your code. Always use environment variables or secrets. 

## Installation

Choose one of the following installation methods:

### Option 1: Install in your own Python environment from the [PyPi repo](https://pypi.org/project/vouchervision-go-client/)

Install
```bash
pip install vouchervision-go-client[full]
```

Upgrade
```bash
pip install --upgrade vouchervision-go-client[full]
```

> Note: You may need to install these packages too:

```bash
pip install requests pandas termcolor tabulate tqdm
```

### Option 2: Using pip (Install from source locally)

```bash
# Clone
git clone https://github.com/Gene-Weaver/VoucherVisionGO-client.git
cd VoucherVisionGO-client
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Option 3: Using conda (Install from source locally)
```bash
# Clone
git clone https://github.com/Gene-Weaver/VoucherVisionGO-client.git
cd VoucherVisionGO-client
# Create a virtual environment
conda create -n vvgo-client python=3.10
conda activate vvgo-client

# Install dependencies
pip install -r requirements.txt
```

# Usage Guide (Option 1)

### Programmatic Usage
You can also use the client functions in your own Python code. Install VoucherVisionGO-client from PyPi:

```python
import os
from client import process_vouchers

if __name__ == '__main__':
  auth_token = os.environ.get("your_auth_token") # Add auth token as an environment variable or secret

	process_vouchers(
    server="https://vouchervision-go-738307415303.us-central1.run.app/", 
    output_dir="./output", 
    prompt="SLTPvM_default_chromosome.yaml", 
    image="https://swbiodiversity.org/imglib/seinet/sernec/EKY/31234100396/31234100396116.jpg", 
    llm_model="gemini-2.5-pro-preview-03-25",  # Specify the LLM model
    directory=None, 
    file_list=None, 
    verbose=True, 
    save_to_csv=True, 
    max_workers=4,
    auth_token=auth_token)  

	process_vouchers(
    server="https://vouchervision-go-738307415303.us-central1.run.app/", 
    output_dir="./output2", 
    prompt="SLTPvM_default_chromosome.yaml", 
    image=None, 
    llm_model=None, # Use the default LLM
    directory="D:/Dropbox/VoucherVisionGO/demo/images", 
    file_list=None, 
    verbose=True, 
    save_to_csv=True, 
    max_workers=4,
    auth_token=auth_token)  

```

To get the JSON packet for a single specimen record:

```python
import os
from client import process_image, ordereddict_to_json, get_output_filename

if __name__ == '__main__':
  auth_token = os.environ.get("your_auth_token") # Add auth token as an environment variable or secret

	image_path = "https://swbiodiversity.org/imglib/seinet/sernec/EKY/31234100396/31234100396116.jpg"
	output_dir = "./output"
	output_file = get_output_filename(image_path, output_dir)
	fname = os.path.basename(output_file).split(".")[0]

	result = process_image(fname=fname,
    server_url="https://vouchervision-go-738307415303.us-central1.run.app/", 
    image_path=image_path, 
    output_dir=output_dir, 
    verbose=True, 
    engines= ["gemini-2.0-flash"],
    prompt="SLTPvM_default_chromosome.yaml",
    auth_token=auth_token)

	# Convert to JSON string
	output_str = ordereddict_to_json(result, output_type="json")
	print(output_str)

	# Or keep it as a python dict
	output_dict = ordereddict_to_json(result, output_type="dict")
	print(output_dict)
```

### Viewing prompts from the command line if you install using PyPi
To see an overview of available prompts:
```bash
vv-prompts --server https://vouchervision-go-738307415303.us-central1.run.app/ --view --auth-token "your_auth_token"
```

To see the entire chosen prompt:
```bash
vv-prompts --server https://vouchervision-go-738307415303.us-central1.run.app/ --prompt "SLTPvM_default.yaml" --raw --auth-token "your_auth_token"
```

### Running VoucherVision from the command line if you install using PyPi

Process a single image
```bash
vouchervision --server https://vouchervision-go-738307415303.us-central1.run.app/ 
  --image https://swbiodiversity.org/imglib/seinet/sernec/EKY/31234100396/31234100396116.jpg 
  --output-dir ./output 
  --prompt SLTPvM_default_chromosome.yaml 
  --verbose 
  --save-to-csv
  --auth-token "your_auth_token"
```

Process a directory of images
```bash
vouchervision --server https://vouchervision-go-738307415303.us-central1.run.app/ 
  --directory ./demo/images 
  --output-dir ./output2 
  --prompt SLTPvM_default_chromosome.yaml 
  --verbose 
  --save-to-csv 
  --max-workers 4
  --auth-token "your_auth_token"
```

Changing OCR engine
```bash
vouchervision --server https://vouchervision-go-738307415303.us-central1.run.app/ 
  --image https://swbiodiversity.org/imglib/seinet/sernec/EKY/31234100396/31234100396116.jpg 
  --output-dir ./output3 
  --engines "gemini-2.0-flash"
  --auth-token "your_auth_token"
```

ONLY produce OCR text
```bash
vouchervision --server https://vouchervision-go-738307415303.us-central1.run.app/ 
  --image https://swbiodiversity.org/imglib/seinet/sernec/EKY/31234100396/31234100396116.jpg 
  --output-dir ./output3 
  --engines "gemini-2.0-flash"
  --auth-token "your_auth_token"
  --ocr-only
```

# Usage Guide (Options 2 & 3)
The VoucherVisionGO client provides several ways to process specimen images through the VoucherVision API. Here are the main usage patterns:

### Basic Command Structure
(Don't include the '<' or '>' in the actual commands)
```bash
python client.py --server <SERVER_URL> 
                 --output-dir <OUTPUT_DIR> 
                 --image <SINGLE_IMAGE_PATH_OR_URL> OR --directory <DIRECTORY_PATH> OR --file-list <FILE_LIST_PATH> 
                 --verbose
                 --save-to-csv
                 --engines <ENGINE1> <ENGINE2>
                 --prompt <PROMPT_FILE>
                 --max-workers <NUM_WORKERS>
                 --auth-token <YOUR_AUTH_TOKEN>
```

### Required Arguments
The server url:

* `--server`: URL of the VoucherVision API server

Authentication:

* `--auth-token`: Your authentication token (obtained from the login page)

One of the following input options:

* `--image`: Path to a single image file or URL
* `--directory`: Path to a directory containing images
* `--file-list`: Path to a file containing a list of image paths or URLs

The path to your local output folder:

* `--output-dir`: Directory to save the output JSON results

### Optional Arguments

* `--engines`: OCR engine options. Recommend not including this and just use the defaults. (default: "gemini-1.5-pro gemini-2.0-flash")
* `--prompt`: Custom prompt file to use. We include a few for you to use. If you created a custom prompt, submit a pull request to add it to [VoucherVisionGO](https://github.com/Gene-Weaver/VoucherVisionGO) or reach out and I can add it for you. (default: "SLTPvM_default.yaml")
* `--verbose`: Print all output to console. Turns off when processing bulk images, only available for single image calls.
* `--save-to-csv`: Save all results to a CSV file in the output directory.
* `--max-workers`: Maximum number of parallel workers. If you are processing 100s/1,000s of images increase this to 8, 16, or 32. Otherwise just skip this and let it use default values. (default: 4, max: 32)
* `--ocr-only`: Run only the OCR portion of VoucherVision. This will return the same final JSON packet, but with an empty "formatted_json" field. 

## View Available Prompts

[View the prompts in a web GUI](https://vouchervision-go-738307415303.us-central1.run.app//prompts-ui)

### List all prompts
First row linux/Mac, second row Windows
```bash
curl -H "Authorization: Bearer your_auth_token" "https://vouchervision-go-738307415303.us-central1.run.app/prompts?format=text"
(curl -H "Authorization: Bearer your_auth_token" "https://vouchervision-go-738307415303.us-central1.run.app/prompts?format=text").Content
```

### View a specific prompt
```bash
curl -H "Authorization: Bearer your_auth_token" "https://vouchervision-go-738307415303.us-central1.run.app/prompts?prompt=SLTPvM_default.yaml&format=text"
(curl -H "Authorization: Bearer your_auth_token" "https://vouchervision-go-738307415303.us-central1.run.app/prompts?prompt=SLTPvM_default.yaml&format=text").Content
```

### Getting a specific prompt in JSON format (default)
```bash
curl -H "Authorization: Bearer your_auth_token" "https://vouchervision-go-738307415303.us-central1.run.app/prompts?prompt=SLTPvM_default.yaml"
(curl -H "Authorization: Bearer your_auth_token" "https://vouchervision-go-738307415303.us-central1.run.app/prompts?prompt=SLTPvM_default.yaml").Content
```


## Example Calls

#### Processing a Single Local Image

```bash
python client.py --server https://vouchervision-go-738307415303.us-central1.run.app/ 
  --image "./demo/images/MICH_16205594_Poaceae_Jouvea_pilosa.jpg" 
  --output-dir "./results/single_image" 
  --verbose
  --auth-token "your_auth_token"
```

#### Processing an Image from URL
```bash
python client.py --server https://vouchervision-go-738307415303.us-central1.run.app/ 
  --image "https://swbiodiversity.org/imglib/h_seinet/seinet/KHD/KHD00041/KHD00041592_lg.jpg" 
  --output-dir "./results/url_image" 
  --verbose
  --auth-token "your_auth_token"
```

#### Processing All Images in a Directory
```bash
python client.py --server https://vouchervision-go-738307415303.us-central1.run.app/ 
  --directory "./demo/images" 
  --output-dir "./results/multiple_images" 
  --max-workers 4
  --auth-token "your_auth_token"
```

#### Processing Images from a CSV List
```bash
python client.py --server https://vouchervision-go-738307415303.us-central1.run.app/ 
  --file-list "./demo/csv/file_list.csv" 
  --output-dir "./results/from_csv" 
  --max-workers 8
  --auth-token "your_auth_token"
```

#### Processing Images from a Text File List
```bash
python client.py --server https://vouchervision-go-738307415303.us-central1.run.app/ 
  --file-list "./demo/txt/file_list.txt" 
  --output-dir "./results/from_txt" 
  --auth-token "your_auth_token"
```

#### Using a Custom Prompt
```bash
python client.py --server https://vouchervision-go-738307415303.us-central1.run.app/ 
  --image "https://swbiodiversity.org/imglib/h_seinet/seinet/KHD/KHD00041/KHD00041592_lg.jpg" 
  --output-dir "./results/custom_prompt" 
  --prompt "SLTPvM_default_chromosome.yaml" 
  --verbose
  --auth-token "your_auth_token"
```

#### Saving Results to CSV
```bash
python client.py --server https://vouchervision-go-738307415303.us-central1.run.app/ 
  --directory "./demo/images" 
  --output-dir "./results/with_csv" 
  --save-to-csv
  --auth-token "your_auth_token"
```

#### Running in OCR-only mode
```bash
python client.py --server https://vouchervision-go-738307415303.us-central1.run.app/ 
  --directory "./demo/images" 
  --output-dir "./results/with_csv" 
  --save-to-csv
  --auth-token "your_auth_token"
  --ocr-only
```

## Output
The client saves the following outputs:

* Individual JSON files for each processed image in the specified output directory.
* A consolidated CSV file with all results if --save-to-csv option is used. First column will be the local filename or filename optained from the url.
* Terminal output with processing details if --verbose option is used. 

### An example of the JSON packet returned by the VVGO API

```json
{
  "filename": "31234100396116",
  "ocr_info": {
    "gemini-1.5-pro": {
      "ocr_text": "EASTERN KENTUCKY UNIVERSITY\nHERBARIUM\n060934\n\nKentucky\nLetcher County\nDiapensiaceae\n*Galax aphylla* auct. non L.\nAbove falls.\n\nWhitesburg Q.; Bad Branch. 1.5 miles NE\nof Eolia.\n\nR. Hannan & L. R.\nPhillippe 2022                                      May 31, 1979\n\nIK\n3 1234 10039611 6\nEastern Kentucky University Herbarium\n\n\n*Galax aphylla*\n\n",
      "cost_in": 0.00077875,
      "cost_out": 0.00062,
      "total_cost": 0.00139875,
      "rates_in": 1.25,
      "rates_out": 5.0,
      "tokens_in": 623,
      "tokens_out": 124
    },
    "gemini-2.0-flash": {
      "ocr_text": "EASTERN\nKENTUCKY\nUNIVERSITY\nHERBARIUM\n060934\nINCH\nOPTIRECTILINEAR\nU.S.A.\nKentucky\nEKY\nLetcher County\nDiapensiaceae\nGalax aphylla auct. non L.\nAbove falls.\nWhitesburg Q.; Bad Branch. 1.5 miles NE\nof Eolia.\nR. Hannnan & L. R.\nPhillippe 2022\nMay. 31, 1979\nIK\n3 1234 10039611 6\nEastern Kentucky University Herbarium\n\n\nGalax aphylla\n\n",
      "cost_in": 0.0006815,
      "cost_out": 5.68e-05,
      "total_cost": 0.0007383,
      "rates_in": 0.1,
      "rates_out": 0.4,
      "tokens_in": 6815,
      "tokens_out": 142
    }
  },
  "parsing_info": {
    "model": "gemini-2-0-flash",
    "input": 2136,
    "output": 437,
    "cost_in": 0.0002136,
    "cost_out": 0.00017480000000000002
  },
  "ocr": "\ngemini-1.5-pro OCR:\nEASTERN KENTUCKY UNIVERSITY\nHERBARIUM\n060934\n\nKentucky\nLetcher County\nDiapensiaceae\n*Galax aphylla* auct. non L.\nAbove falls.\n\nWhitesburg Q.; Bad Branch. 1.5 miles NE\nof Eolia.\n\nR. Hannan & L. R.\nPhillippe 2022                                      May 31, 1979\n\nIK\n3 1234 10039611 6\nEastern Kentucky University Herbarium\n\n\n*Galax aphylla*\n\n\ngemini-2.0-flash OCR:\nEASTERN\nKENTUCKY\nUNIVERSITY\nHERBARIUM\n060934\nINCH\nOPTIRECTILINEAR\nU.S.A.\nKentucky\nEKY\nLetcher County\nDiapensiaceae\nGalax aphylla auct. non L.\nAbove falls.\nWhitesburg Q.; Bad Branch. 1.5 miles NE\nof Eolia.\nR. Hannnan & L. R.\nPhillippe 2022\nMay. 31, 1979\nIK\n3 1234 10039611 6\nEastern Kentucky University Herbarium\n\n\nGalax aphylla\n\n",
  "formatted_json": {
    "catalogNumber": "060934",
    "scientificName": "Galax aphylla",
    "genus": "Galax",
    "specificEpithet": "aphylla",
    "scientificNameAuthorship": "auct. non L.",
    "collectedBy": "R. Hannan & L. R. Phillippe",
    "collectorNumber": "2022",
    "identifiedBy": "IK",
    "identifiedDate": "",
    "identifiedConfidence": "",
    "identifiedRemarks": "",
    "identificationHistory": "",
    "verbatimCollectionDate": "May 31, 1979",
    "collectionDate": "1979-05-31",
    "collectionDateEnd": "",
    "habitat": "Above falls.",
    "chromosomeCount": "",
    "guardCell": "",
    "specimenDescription": "",
    "cultivated": "",
    "continent": "North america",
    "country": "Usa",
    "stateProvince": "Kentucky",
    "county": "Letcher County",
    "locality": "Whitesburg Q.; Bad Branch. 1.5 miles NE of Eolia.",
    "verbatimCoordinates": "",
    "decimalLatitude": "",
    "decimalLongitude": "",
    "minimumElevationInMeters": "",
    "maximumElevationInMeters": "",
    "elevationUnits": "",
    "additionalText": "EASTERN KENTUCKY UNIVERSITY\nHERBARIUM\nEastern Kentucky University Herbarium"
  }
}
```

## Advanced Usage

### Using Different OCR Engines

Using BOTH of the best Gemini models for OCR (default)
```bash
python client.py --server https://vouchervision-go-738307415303.us-central1.run.app/ 
  --image "./demo/images/MICH_16205594_Poaceae_Jouvea_pilosa.jpg" 
  --output-dir "./results/custom_engines" 
  --engines "gemini-1.5-pro" "gemini-2.0-flash" 
  --verbose
  --auth-token "your_auth_token"
```

Using only 1 of the best Gemini models for OCR.
```bash
python client.py --server https://vouchervision-go-738307415303.us-central1.run.app/ 
  --image "./demo/images/MICH_16205594_Poaceae_Jouvea_pilosa.jpg" 
  --output-dir "./results/custom_engines" 
  --engines "gemini-2.0-flash" 
  --verbose
  --auth-token "your_auth_token"
```

### Using Different LLM Models

In addition to selecting OCR engines, you can specify which LLM model to use for parsing the OCR text into structured JSON data.

#### From the command line

```bash
# Specify a specific LLM model for processing
python client.py --server https://vouchervision-go-738307415303.us-central1.run.app/ 
  --image "./demo/images/MICH_16205594_Poaceae_Jouvea_pilosa.jpg" 
  --output-dir "./results/custom_llm" 
  --llm-model "gemini-2.5-flash-preview-04-17" 
  --verbose
  --auth-token "your_auth_token"
```

#### From PyPi
```python
import os
from client import process_vouchers

auth_token = os.environ.get("your_auth_token")

process_vouchers(
  server="https://vouchervision-go-738307415303.us-central1.run.app/", 
  output_dir="./output", 
  prompt="SLTPvM_default.yaml", 
  image="https://swbiodiversity.org/imglib/seinet/sernec/EKY/31234100396/31234100396116.jpg", 
  llm_model="gemini-2.5-pro-preview-03-25",  # Specify the LLM model
  verbose=True, 
  save_to_csv=True, 
  auth_token=auth_token
)
```

### Using World Flora Online (WFO) Validation

The `--include-wfo` flag enables taxonomic validation against the World Flora Online database. This feature validates plant names and provides additional taxonomic information in the results.

When WFO validation is enabled, the results will include a WFO_info field containing taxonomic validation data and any corrections or additional information from the World Flora Online database.

#### From the Command Line (Options 2 & 3)

**Single image with WFO validation:**
```bash
python client.py --server https://vouchervision-go-738307415303.us-central1.run.app/ 
  --image "./demo/images/MICH_16205594_Poaceae_Jouvea_pilosa.jpg" 
  --output-dir "./results/with_wfo" 
  --include-wfo 
  --verbose
  --auth-token "your_auth_token"
```

**Directory processing with WFO validation:**
```bash
python client.py --server https://vouchervision-go-738307415303.us-central1.run.app/ 
  --directory "./demo/images" 
  --output-dir "./results/bulk_wfo" 
  --include-wfo 
  --max-workers 4
  --auth-token "your_auth_token"
```

**Combining with custom prompt and LLM model:**
```bash
python client.py --server https://vouchervision-go-738307415303.us-central1.run.app/ 
  --image "https://swbiodiversity.org/imglib/seinet/sernec/EKY/31234100396/31234100396116.jpg" 
  --output-dir "./results/advanced_wfo" 
  --prompt "SLTPvM_default_chromosome.yaml" 
  --llm-model "gemini-2.5-pro" 
  --include-wfo 
  --verbose
  --auth-token "your_auth_token"
```

#### From PyPi (Option 1)
**Command line with PyPi installation:**
```bash
vouchervision --server https://vouchervision-go-738307415303.us-central1.run.app/ 
  --image https://swbiodiversity.org/imglib/seinet/sernec/EKY/31234100396/31234100396116.jpg 
  --output-dir ./output 
  --include-wfo 
  --verbose 
  --auth-token "your_auth_token"
```

**Programmatic usage with PyPi:**
```python
import os
from client import process_vouchers

auth_token = os.environ.get("your_auth_token")

process_vouchers(
  server="https://vouchervision-go-738307415303.us-central1.run.app/", 
  output_dir="./output", 
  prompt="SLTPvM_default.yaml", 
  image="https://swbiodiversity.org/imglib/seinet/sernec/EKY/31234100396/31234100396116.jpg", 
  llm_model="gemini-2.5-pro-preview-03-25",
  include_wfo=True,  # Enable WFO validation
  verbose=True, 
  save_to_csv=True, 
  auth_token=auth_token
)
```

**Single image processing with WFO:**
```python
import os
from client import process_image, ordereddict_to_json, get_output_filename

auth_token = os.environ.get("your_auth_token")

image_path = "https://swbiodiversity.org/imglib/seinet/sernec/EKY/31234100396/31234100396116.jpg"
output_dir = "./output"
output_file = get_output_filename(image_path, output_dir)
fname = os.path.basename(output_file).split(".")[0]

result = process_image(
  fname=fname,
  server_url="https://vouchervision-go-738307415303.us-central1.run.app/", 
  image_path=image_path, 
  output_dir=output_dir, 
  verbose=True, 
  engines=["gemini-2.0-flash"],
  prompt="SLTPvM_default.yaml",
  include_wfo=True,  # Enable WFO validation
  auth_token=auth_token
)

# The result will now include WFO validation data in the WFO_info field
output_dict = ordereddict_to_json(result, output_type="dict")
print("WFO Validation Results:", output_dict.get('WFO_info', 'No WFO data'))
```

#### API Usage
**Using form data:**
```bash
curl -X POST "https://vouchervision-go-738307415303.us-central1.run.app/process" \
  -H "Authorization: Bearer your_auth_token" \
  -F "file=@image.jpg" \
  -F "include_wfo=true"
```

**Using Using URL processing:**
```bash
curl -X POST "https://vouchervision-go-738307415303.us-central1.run.app/process-url" \
  -H "Authorization: Bearer your_auth_token" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/specimen.jpg",
    "include_wfo": true,
    "prompt": "SLTPvM_default.yaml"
  }'
```

## Available LLM Models
You can use any Gemini model that supports vision capabilities:

- gemini-1.5-pro - High quality but slower, will be deprecated soon
- gemini-2.0-flash - Fast with good quality (default)
- gemini-2.5-flash-preview-04-17
- gemini-2.5-pro-preview-03-25 - Highest quality parsing, can use tools, geolocate

For the most up-to-date list of supported models, refer to the [Google AI Gemini API documentation](https://ai.google.dev/gemini-api/docs/models)

### Processing Large Batches with Parallel Workers
For large datasets, you can adjust the number of parallel workers:

```bash
python client.py --server https://vouchervision-go-738307415303.us-central1.run.app/ 
  --file-list "./demo/txt/file_list32.txt" 
  --output-dir "./results/parallel" 
  --max-workers 32 
  --save-to-csv
  --auth-token "your_auth_token"
```


## Contributing
If you encounter any issues or have suggestions for improvements, please open an issue in the main repository [VoucherVisionGO](https://github.com/Gene-Weaver/VoucherVisionGO).

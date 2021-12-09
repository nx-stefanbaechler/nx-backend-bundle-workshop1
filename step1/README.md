# Backend Bundle Workshop 1
## Step 1 - grab & upload documents 

This application will grab the linked documents from https://www.tavernesblanques.es/es/transparencia/ordenanzas and put them into an Amazon bucket - Since the label of the links is more human readable as the name of the file, the label should be added to the bucket as some kind of metadata

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the required packages.

```bash
python3 -m pip install -r requirements.txt
```

copy the `.env.example` to `.env` and edit the values to match your needs
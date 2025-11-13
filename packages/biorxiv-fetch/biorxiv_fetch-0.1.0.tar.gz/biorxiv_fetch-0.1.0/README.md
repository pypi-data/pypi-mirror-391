## Setup

### Authenticate with AWS

Either run via an AWS instance with IAM access, or on another instance with AWS keys installed.

### Authenticate with the AWS CLI:

```
aws configure
```

## Usage

```python
import biorxiv_fetch as br

doi = "xxx.xx/xxxx"
out_dir = "out"
br.fetch_doi(doi, out_dir)
```
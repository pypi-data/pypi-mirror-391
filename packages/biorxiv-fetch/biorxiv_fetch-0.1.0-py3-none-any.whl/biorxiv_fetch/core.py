import os
from typing import Dict, Tuple

import boto3
import requests


def doi_to_data(doi: str) -> Dict:
    """
    Look up metadata for a DOI using the same endpoint and approach
    used in the notebook.
    """
    prefix, suffix = doi.split("/", 1)
    response = requests.get(
        f"https://openrxiv.csf.now/v1/works/{prefix}/{suffix}", timeout=20
    )
    response.raise_for_status()
    return response.json()


def doi_to_s3(doi: str) -> Tuple[str, str]:
    """
    Return (bucket, key) for the latest version of the given DOI.
    """
    data = doi_to_data(doi)
    latest = sorted(data["versions"], key=lambda v: v["version"])[-1]
    return latest["s3Bucket"], latest["s3Key"]


def download_meca(bucket: str, key: str, output_dir: str) -> str:
    """
    Download the MECA archive from S3 (Requester Pays) into output_dir.
    Returns the full path to the downloaded file.
    """
    os.makedirs(output_dir, exist_ok=True)
    destination_path = os.path.join(output_dir, os.path.basename(key))
    s3_client = boto3.client("s3")
    s3_client.download_file(
        Bucket=bucket,
        Key=key,
        Filename=destination_path,
        ExtraArgs={"RequestPayer": "requester"},
    )
    return destination_path


def fetch_doi(doi: str, output_dir: str) -> str:
    """
    High-level API used in the README:
      - Resolves DOI to S3 location
      - Downloads the .meca file into output_dir
      - Returns the local path to the downloaded file
    """
    bucket, key = doi_to_s3(doi)
    return download_meca(bucket, key, output_dir)



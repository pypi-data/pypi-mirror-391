# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# Copyright [2025] The Jackson Laboratory

from typing import Optional, Any, Dict, List
from .dao import UntypedStatus, Input, ToolConf, StorageKey
from .auth import get_access_token

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64


import sys
import os
import time
import requests
import random
import string
from pathlib import Path
import json
from time import sleep

def run_workflow(input: Input, 
                 tool: ToolConf,
                 server_uri: Optional[str] = "https://imagetools-dev.jax.org/api",
                 query_interval=2,
                 subscriber=None) -> UntypedStatus:
    """
    Run a workflow given an input and tool configuration.
    """
    
    # Submit the workflow
    monitor_uri = submit_workflow(input, tool, server_uri, query_interval)
    
    # Monitor until complete
    return monitor_workflow(monitor_uri, query_interval)

def monitor_workflow(monitor_uri: str, query_interval=2, subscriber=None) -> UntypedStatus:
    """
    Monitor a workflow until completion.
    """
    
    status: UntypedStatus = None
    
    # Monitor workflow status
    while not is_final(status):
        try:
            token = get_access_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            response = requests.get(monitor_uri, headers=headers)
            response.raise_for_status()
            status: UntypedStatus = response.json()
            
            if subscriber is not None:
                subscriber(status)
            
            complete: float = status["complete"]
            complete_percent: float = complete * 100.0
            state:str = status["state"]
            message: str = status["message"] 
            sys.stdout.write(f"\r{state} {complete_percent}% {message}")
            sys.stdout.flush()
            if is_final(status):
                break
            
            time.sleep(query_interval)
           
        except Exception:
            break

    return status


def submit_workflow(input: Input, 
                 tool: ToolConf,
                 server_uri: Optional[str] = "https://imagetools-dev.jax.org/api",
                 query_interval=2) -> Any:
    """
    Submit a workflow given an input and tool configuration.
    """
  
    instr = create_instruction(input)
    token = get_access_token()
    
    url = f"{server_uri}/process"
    params = {"type": tool.name}
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    with requests.post(url, params=params, json=instr, headers=headers) as response:
        response.raise_for_status()  # Raises an error for bad responses
        monitor: str = response.json()  # Or response.text if you expect plain text
        monitor_uri = monitor["response"]
        print(f"Monitor URI: {monitor_uri}")
        sleep(2)  # Give server a moment to start processing, not strictly necessary
                  # but gives a better user experience.
        return monitor_uri
    
def delete(file_or_dir: StorageKey,
           server_uri: Optional[str] = "https://imagetools-dev.jax.org/api",
           type: str = "File") -> None:
    """
    Delete a file or directory.
    """
  
    blob: Dict = create_blob(file_or_dir, type)
    token: str = get_access_token()
    
    url = f"{server_uri}/delete"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    with requests.post(url, json=blob, headers=headers) as response:
        response.raise_for_status()  # Raises an error for bad responses


def download(file: StorageKey,
           server_uri: Optional[str] = "https://imagetools-dev.jax.org/api",
           dir: Path = Path("./tmp")) -> Path:
    """
    Delete a file or directory.
    """
  
    blob: Dict = create_blob(file)
    token: str = get_access_token()
    
    url = f"{server_uri}/download"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    os.makedirs(dir, exist_ok=True)
    filename = os.path.basename(file.object)
    output_path = os.path.join(dir, filename)
    
    params = {"info": json.dumps(blob)}
    with requests.get(url, params=params, headers=headers, stream=True) as response:
        response.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    return Path(output_path)

def get_report(uri: str, download_dir="./tmp") -> List[str]:
    image: StorageKey = StorageKey.from_uri(uri) # The first result is the text file with all the paths.
    local_path: Path = Path(download_dir) # Specify the dir where we want it.
    loc: Path = download(image, dir=local_path)
    
    with open(loc, "r", encoding="utf-8") as f:
        lines = f.readlines()
        return lines

def upload(file: Path,
           dir: StorageKey,
           server_uri: Optional[str] = "https://imagetools-dev.jax.org/api") -> Path:
    """
    Delete a file or directory.
    """
  
    token: str = get_access_token()
    
    url = f"{server_uri}/upload"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "uri" : dir.to_uri(),
        "key" : get_upload_key(file)
    }
    
    with open(file, "rb") as f:
        files = {"file": (file.name, f)}
        with requests.post(url, headers=headers, files=files) as response:
            response.raise_for_status()
        
    return file


UPLOAD_KEY = os.getenv("UPLOAD_KEY", "A secret key base64 encoded==")

def get_upload_key(file_path: Path) -> str:
    key = get_key()

    # AES in ECB mode (since Java Cipher.getInstance("AES") defaults to AES/ECB/PKCS5Padding)
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()

    # Prepare plaintext (filename as UTF-8)
    plaintext = file_path.name.encode("utf-8")

    # Apply PKCS7 padding (block size = 128 bits for AES)
    padder = padding.PKCS7(128).padder()
    padded = padder.update(plaintext) + padder.finalize()

    # Encrypt
    encrypted_bytes = encryptor.update(padded) + encryptor.finalize()

    # Return base64 string
    return base64.b64encode(encrypted_bytes).decode("utf-8")
   
def get_key():
    # Decode the base64 key into raw bytes
    key_bytes = base64.b64decode(UPLOAD_KEY)
    return key_bytes

def create_instruction(input: Input) -> Dict:
    instr = {
        "file": create_blob(input.image),
        "request": input.request,
    }
    return instr

def create_blob(storage_key, type: str = "File") -> Dict:
    blob = {
        "name": os.path.basename(storage_key.object),
        "project": {
            "bucket": storage_key.bucket,
            "name": "Python api submission to {}".format(storage_key.bucket),
        },
        "type": type,
        "relPath": storage_key.object,
    }
    return blob
    

def is_final(status: UntypedStatus) -> bool:
    if status is None:
        return False
    state:str = status["state"]
    return state in ("COMPLETE", "ERROR", "CANCELLED")

def is_storage_result(result: str) -> bool:
    
    if "://" in result:
        return True
    return False

def random_string(size: Optional[int] = 4) -> str:
    # Generate a n-character random string (uppercase + lowercase letters)
    rand_str = ''.join(random.choice(string.ascii_letters) for _ in range(size))
    return rand_str

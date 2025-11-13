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
import os

from temporalio import activity
from temporalio.activity import logger

from jax.cs.storage import StorageObject
from .dao import StorageKey


from pathlib import Path
import shutil

###############################################################################
# These activities are provided by universal activities when deployed.
# We have test versions here to make sure they are implemented in test mode.
# We use the term 'dummy' to indicate these are not the real activities.
###############################################################################


@activity.defn(name="io-temporal-download-object")
async def dummy_download_object(
    key: StorageKey, run_id: str, overwrite: bool, ignoreNotExisting: bool
) -> str:

    try:
        dir: Path = get_dir(run_id)
        file: Path = Path(dir, key.object)
        os.makedirs(file.parent, exist_ok=True)
        file.touch()

        uri: str = key.to_uri()
        wrapped = StorageObject(uri)

        with open(file, "wb") as download_file:
            data = wrapped.download_as_bytes()
            download_file.write(data)

        return str(file)
    except Exception as e:
        logger.error(e)
        raise e


@activity.defn(name="io-temporal-upload")
async def dummy_upload(key: StorageKey, file: str, replace: bool) -> str:

    try:
        if not os.path.exists(file):
            return

        local_wrapped: StorageObject = StorageObject(file)
        uri: str = key.to_uri(
            create=True
        )  # Test uri will create local file, otherwise, create does nothing.
        remote_wrapped: StorageObject = StorageObject(uri)
        remote_wrapped.replace(local_wrapped)
        return uri

    except Exception as e:
        logger.error(e)
        raise e


@activity.defn(name="io-temporal-clean")
async def dummy_clean(run_id: str) -> None:

    try:
        dir: Path = get_dir(run_id)
        shutil.rmtree(dir)

    except Exception as e:
        logger.error(e)
        raise e


def get_dir(run_id: str) -> Path:

    CACHE_DIR: str = os.getenv("CACHE_DIR", "cache")
    cache: Path = Path(CACHE_DIR)
    dir: Path = Path(cache, run_id)
    # Make dirs if not existing
    os.makedirs(dir, exist_ok=True)
    return dir

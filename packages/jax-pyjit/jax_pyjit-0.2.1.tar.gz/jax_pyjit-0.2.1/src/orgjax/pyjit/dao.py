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


from dataclasses import dataclass, field
from typing import List, Optional, Any
from pathlib import Path
from enum import Enum
from urllib.parse import urlparse

import os

from . import shared_config



class State:
    SUBMITTED: str = "SUBMITTED"
    RUNNING: str = "RUNNING"
    COMPLETE: str = "COMPLETE"
    ERROR: str = "ERROR"
    NONE: str = "NONE"
    CANCELLED: str = "CANCELLED"


@dataclass
class UntypedStatus:
    """
    Based on cimg-api/org.jax.cimg.api.evt.UntypedStatus
    which we use in Image Tools.
    These fields are shared across multiple tools.
    Do not change them.
    """

    message: Optional[str] = None
    state: str = State.NONE
    complete: float = 0
    errorStack: Optional[str] = None
    workflowId: Optional[str] = None
    results: List[str] = field(default_factory=lambda: [""])
    submissionInput: Optional[str] = None
    userName: Optional[str] = None


class Protocol(str, Enum):
    GS = "GS"
    S3 = "S3"
    NIO = "NIO"


@dataclass
class StorageKey:

    bucket: str
    object: str
    protocol: Optional[str] = None # One of Protocol
    endpoint: Optional[str] = None
    test: Optional[bool] = False
    
    def to_dict(self):
        # This is require to make 
        # json serialization to work.
        return {
            "bucket": self.bucket,
            "object": self.object,
            "protocol": self.protocol,
            "endpoint": self.endpoint,
        }
        
    def clone(self) -> "StorageKey":
        # You can trick python here using a string to let
        # it return a type but you cannot return a StorageKey
        # because we have not defined it yet.
        # Now wash your eyes.
        return StorageKey(
            bucket=self.bucket,
            object=self.object,
            protocol=self.protocol,
            endpoint=self.endpoint,
            test=self.test,
        )

    def set_file_name(self, file_name: str) -> "StorageKey":
        """
        Replace the file name in the object path with the given file_name.
        """
        p = Path(self.object)
        if p.parent == Path('.'):
            self.object = file_name
        else:
            if p.is_dir() or self.object.endswith('/'):
                self.object = str(p / file_name)
            else:
                self.object = str(p.parent / file_name)
        self.object = self.object.replace("\\", "/")
           
        return self
            
    def to_uri(self, create=False) -> str:
        if self._is_local():
            file_path: str = None
            if self.endpoint is None:
                file_path: str = "{}/{}".format(self.bucket, self.object)
            else:
                file_path: str = "{}/{}/{}".format(
                    self.endpoint, self.bucket, self.object
                )

            NIO_STORAGE_ROOT: str = shared_config.NIO_STORAGE_ROOT
            if NIO_STORAGE_ROOT:
                file_path = "{}/{}".format(NIO_STORAGE_ROOT, file_path)

            # Remove double slashes
            file_path = file_path.replace("//", "/")
            file_path = file_path.replace("\\", "/")

            if create:
                path: Path = Path(file_path)
                os.makedirs(path.parent, exist_ok=True)
                path.touch(exist_ok=True)
            return file_path
        else:
            return f"{self.protocol.lower()}://{self.bucket}/{self.object}"

    def _is_local(self) -> bool:
        if self.protocol == Protocol.NIO:
            return True
        if self.test:
            return True

        USE_NIO_STORAGE: bool = shared_config.USE_NIO_STORAGE
        if USE_NIO_STORAGE:
            return True
        return False

    @classmethod
    def from_uri(cls, uri: str) -> "StorageKey":
        """
        Parse a URI and return a StorageKey instance.
        Supports formats like:
          - gs://bucket/object
          - s3://bucket/object
          - nio://bucket/object
          - /local/path/to/object (NIO/local)
        """
        parsed = urlparse(uri)
        if parsed.scheme in ("gs", "s3", "nio"):
            protocol = parsed.scheme.upper()
            bucket = parsed.netloc
            object_ = parsed.path.lstrip("/")
            object_ = object_.replace("\\", "/")
            return cls(bucket=bucket, object=object_, protocol=protocol)
        else:
            # Assume local path (NIO)
            # You may want to split the path differently depending on your conventions
            parts = Path(uri).parts
            if len(parts) >= 2:
                bucket = parts[0]
                object_ = str(Path(*parts[1:]))
            else:
                bucket = ""
                object_ = uri
            object_ = object_.replace("\\", "/")
            return cls(bucket=bucket, object=object_, protocol=Protocol.NIO)

@dataclass
class AbstractRequest:
    info: Optional[Any] = None

    def __eq__(self, other):
        if not isinstance(other, AbstractRequest):
            return False
        return self.info == other.info

    def __hash__(self):
        return hash(self.info)

@dataclass
class Input:
    """
    Input is the single class we send to any workflow in JIT.
    request is the actual request object specific to the workflow.
    """
    image: StorageKey
    request: AbstractRequest
    result: Optional[Any] = None
    userName: Optional[str] = None
    # Tried using field(default=None, metadata=config(field_name="userName")) to make is user_name 
    # but did not work.

class ToolConf:
    """
    Class containing queue name constants.
    """    
    def __init__(self, 
                 name: Optional[str], 
                 queue: Optional[str], 
                 workflow_name: Optional[str], 
                 workflow_query: Optional[str], 
                 namespace: Optional[str] = "cimg-dev"):
        
        self.name = name
        self.queue = queue
        self.workflow_name = workflow_name
        self.workflow_query = workflow_query
        self.namespace = namespace
        
class Tools:
    
    # Not a ProcessType value
    NONE: ToolConf = ToolConf("NONE", "NONE", None, None)
    
    #-------------------------
    # NOTE These strings must match org.jax.cimg.api.dao.ProcessType
    # precisely.
    #-------------------------
    CROP: ToolConf = ToolConf("CROP", "SEGMENTATION_TASK_QUEUE", "Segmentation Workflow", "Segmentation Query")
    FIND: ToolConf = ToolConf("FIND", "FIND_TASK_QUEUE", "Find Workflow", "Find Query")
    HTQUANT: ToolConf = ToolConf("HTQUANT", "HTQUANT_QUEUE", "HtQuant Workflow", "HtQuant Query")
    ALIGNMENT: ToolConf = ToolConf("ALIGNMENT", "SIFT_QUEUE", "Sift Workflow", "Sift Query")
    EDOF: ToolConf = ToolConf("EDOF", "EDOF_QUEUE", "EDOF Workflow", "EDOF Query")
    KIDNEY_CLASSIFIER: ToolConf = ToolConf("KIDNEY_CLASSIFIER", "orchestration-task", "OrchestrationWorkflow", "classifierStatus")
    DECONVOLUTION: ToolConf = ToolConf("DECONVOLUTION", "DECONVOLUTION_QUEUE", "Color Deconvolution Workflow", "Color Deconvolution Query")
    YOLO_SEGDETECT: ToolConf = ToolConf("YOLO_SEGDETECT", "YOLO_SEGDETECT_QUEUE", "YoloSegdetect Workflow", "YoloSegdetect Query")
    RETINAL_LAYER: ToolConf = ToolConf("RETINAL_LAYER", "RETINAL_LAYER_QUEUE", "Retinal Layer Workflow", "Retinal Layer Query")
    STAIN_ADAPTER: ToolConf = ToolConf("STAIN_ADAPTER", "STAIN_ADAPTER_QUEUE", "Stain Adapter Workflow", "Stain Adapter Query")
    CONVERT: ToolConf = ToolConf("CONVERT", "CONVERT_TASK_QUEUE", "Convert Workflow", "Convert Query") 


def blank_key() -> StorageKey:
    return StorageKey("", "", test=True)


@dataclass
class DeconvolutionRequest(AbstractRequest):
    inputPath: Optional[StorageKey] = None

    stain1: List[float] = field(default_factory=lambda: [0.563, 0.720, 0.406])
    stain2: List[float] = field(default_factory=lambda: [0.216, 0.801, 0.558])

    stain1Max: float = 2.0
    stain2Max: float = 1.0

    alpha: int = 1
    beta: float = 0.15
    intensityNorm: int = 240
    grayscale: bool = False

    stain1ImageOutput: Optional[StorageKey] = None
    stain2ImageOutput: Optional[StorageKey] = None
    normalizedImageOutput: Optional[StorageKey] = None
    imageStackOutput: Optional[StorageKey] = None

    def __post_init__(self):
        # Ensure info is set to DECONVOLUTION by default
        if not self.info:
            self.info = Tools.DECONVOLUTION.name

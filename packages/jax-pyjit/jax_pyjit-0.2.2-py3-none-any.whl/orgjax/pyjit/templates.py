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
from typing import Dict
from .dao import Tools, ToolConf


def _create_template_requests() -> Dict:
    
    # TODO Do we want to have proper concrete types for these requests?
    # We could autogenerate them from the Java classes as we did for the
    # typescript JIT client.
    
    # We could also move the existing dao concrete types in all the python
    # tools to dao here then import them into each tool.
    # TODO Submit a ticket to do that.
    
    ret = {}
    
    # Crop
    request = {
        "info": "CROP",
        
        # This is the StorageKey of the folder to be
        # used to hold the results.
        "outputDir": None, # StorageKey
        "bytesPerPixel": 0,
        "cropIndices": None,
        
        # Use this to customize the size of
        # things being detected.
        "particleSettings": {
            "min": 1200000,
            "max": 2147483647,
            "cMin": 0.1,
            "cMax": 1,
            "hardBounds": True,
        },
        
        # This is used to process the image
        # prior to segementation i.e. making the mask.
        "imagePreprocess": {
            "rollingBallRadius": 50,
            "sigma": 100,
            "accuracy": 0.002,
            "autoThreshold": "Otsu",
        },
        "findResolution": -2147483648,
        "optimumFindSize": 16000000,
        "cropResolution": 0,
        
        # The settings for regions
        "regionSettings": {
            "minimumAspectRatio": 0.15,
            "margin": 10,
            "findRegions": True,
            "showRegions": False,
            "reference": None,
            "manualRegionResolution": 0,
            "manualRegions": [],
            "userRegions": None,
            "generateProofImage": True,
            "generatePreviews": True,
            "previewSize": 2048,
            "zip": True,
            "saveAsJson": True,
            "fontSize": 160,
            "cropFoundRegionsAsRectangles": True,
            "forceSquare": False,
            "cropAsGreyScale": False,
            "order": "ROWS",
        },
        "prefix": "",
        
        # Tiling is being used setup here.
        "tileConfiguration": {
            "tileSize": [4096, 4096],
            "order": "IMAGE",
            "clip": True,
            "alwaysTile": False,
            "expandCroppedFiles": True,
            "cropFillColor": None,
        },
        
        # Save the request generated, useful for 
        # using this run with the API later.
        "saveRequest": True,
        "imageJPlugin": False,
    }
    ret[Tools.CROP] = request
    
    # TODO Use concrete python class?
    request = {
        "info" : "DECONVOLUTION",
        "inputPath" : None,
        "stain1" : [ 0.563, 0.72, 0.406 ],
        "stain2" : [ 0.216, 0.801, 0.558 ],
        "stain1Max" : 2.0,
        "stain2Max" : 1.0,
        "alpha" : 1,
        "beta" : 0.15,
        "intensityNorm" : 240,
        "grayscale" : False,
        "stain1ImageOutput" : None,
        "stain2ImageOutput" : None,
        "normalizedImageOutput" : None,
        "imageStackOutput" : None
    }
    ret[Tools.DECONVOLUTION] = request

    # TODO Use concrete python class?
    request = {
      "info" : "YOLO_SEGDETECT",
      "inputPaths" : None,
      "weightsPath" : None,
      "outputPath" : None,
      "downsamplingFactor" : 5,
      "visualize" : False,
      "overlapX" : 0,
      "overlapY" : 0,
      "confidence" : 0.6,
      "iouThreshold" : 0.5,
      "nmsThreshold" : 0.3,
      "saveSegment" : False,
      "level" : 2,
      "db_upsert" : False
    }
    ret[Tools.YOLO_SEGDETECT] = request

    # TODO Use concrete python class?
    request = {
      "info" : "ALIGNMENT",
      
      # StorageKeys
      "align" : None,
      "reference" : None,
      "shg" : None,
      "siftOutput" : None,
      "resizedN" : None,
      "resizedSF" : None,
      "overlayedResult" : None,
      
      # Config
      "transform" : True,
      "flip" : True,
      "downsample" : False,
      "gamma" : 1.0,
    }
    ret[Tools.ALIGNMENT] = request
    
    request = {
        "info" : "EDOF",
      
        # Parameters:
        # -gradient_kernel=(5)
        #        Size of kernel used for computation of image gradients.  Must be 1, 3, 5, 7.
        "gradientKernel" : 5,
        
        # -noise_filter=(3)
        #    Size of median filter used to reduce noise in the z-map. Must be 0, 3 or 5
        "imageNoiseFilter" : 3,

        # -noise_filter=(3)
        #      Size of median filter used to reduce noise in the z-map. Must be 0, 3 or 5
        "zmapNoiseFilter" : 3,

        # -low_pass=(2)
        #    zmap lowpass filter object size.
        "lowPass" : 2,
        
        # It will be hard to know this from the client side
        # because the analysis may run anywhere in temporal.io 
        # distributed computing environment.
        "threads" : 2,
        "dryRun" : False,
        
        # A list of StorageKeys for the input images.
        # It is a list because edof can run either on one
        # image which contains a stack or muliple images 
        # in a directory.
        "input" : [],
        
        # -image=("edof.tif") 
        # StorageKey for the output image file.  Most standard formats are supported.
        "outputImage" : None,
        
        # -zmap=("zmap.tif")
        # StorageKey for the z-map file saved as a 16-bit monochrome image.
        "outputZmap" : None,
      
        # -zmap_input=(none)
        #    StorageKey which when specified, this z-map is used for extraction of the final image.
        "inputZmap" : None,
    }
    ret[Tools.EDOF] = request

    request ={
        "info" : "CONVERT",
      
        # These end up being -<command option> on the
        # BioFormat command.
        # debug("debug"),
        # stich("stitch"),
        # separate("separate"),
        # merge("merge"),
        # expand("expand"),
        # bigtiff("bigtiff"),
        # nobigtiff("nobigtiff"),
        # cache("cache"),
        # nogroup("nogroup"),
        # nolookup("nolookup"), 
        # autoscale("autoscale"),
        # version("version"),
        # noupgrade("no-upgrade"),
        # padded("padded"),
        # nosas("no-sas"),
        # novalid("novalid"),
        # validate("validate"),        
        # precompressed("precompressed"),
        # overwrite("overwrite"),
        # showinf("showinf");
        "options" : [ "overwrite" ],
      
        #  You may use this string to override the reset of the parameters
        #  and provide all the command line apart from the input image and the
        #  output image as a string. Setting this will negative the other
        #  options. This is useful if you want to provide a command line
        #  which is already known. It is not intended to be part of the web UI
        #  but is useful for the CLI.
        "cmd" : None,
        
        "uploadDir" : None, # StorageKey for the dir to which we will upload the converted file(s)
        "useGeoJson" : True,
        
        # If any of the following patterns are present in out_file, they will
        # be replaced with the indicated metadata value from the input file.
        #
        #    Pattern:    Metadata value:
        #    ---------------------------
        #    %s        series index
        #    %n        series name
        #    %c        channel index
        #    %w        channel name
        #    %z        Z index
        #    %t        T index
        #    %A        acquisition timestamp
        #    %x        row index of the tile
        #    %y        column index of the tile
        #    %m        overall tile index
        #
        # For example: "tile_%x_%y.tiff" for the name of each tiled tiff extracted.
        # If you do not set outfile correctly then BioFormats will not generate the
        # correct images in the directory.
        "outFile" : None,
        
        # This is the value of the [-compression codec] option in BioFormats.
        # Set to compress to a specific format.
        "compression" : None,
        
        # The series which we want to extract for conversion from the
        # input file. Usually used (None) which defaults to (0) to extract the first series.
        "series" : None,

        "map" : None,
        
        # [-range start end] option on BioFormats command line.
        "range" : None,
        
        # Set the rectangle to crop from the image.
        # [-crop x,y,w,h] example: request["crop"] = {100,100,400,400}
        # x,y top left corner, w width, h height
        "crop" : None,
        
        # a polygon array of all the regions to crop and use for the converted
        # image example:
        # request["manualRegions"] = [ {
        #         "npoints" : 4,
        #         "xpoints" : [ 0, 0, 100, 100 ],
        #         "ypoints" : [ 0, 100, 100, 0 ]
        #       }, {
        #         "npoints" : 4,
        #         "xpoints" : [ 100, 100, 200, 200 ],
        #         "ypoints" : [ 0, 100, 100, 0 ]
        #       }, {
        #         "npoints" : 4,
        #         "xpoints" : [ 200, 200, 300, 300 ],
        #         "ypoints" : [ 0, 100, 100, 0 ]
        #       } ]
        "manualRegions" : None,
        
        # [-channel channel] option on BioFormats command line.
        "channel" : None,
        
        #[-z Z]
        "z" : None,
        
        # [-timepoint timepoint] 
        "timepoint" : None,
        
        # [-option key value]
        "option" : None,
        
        # [-tilex tileSizeX]
        "tilex" : None,
        
        # [-tiley tileSizeY]
        "tiley" : None,
        
        # [-pyramid-scale scale]
        "pyramidScale" : None,
        
        # [-swap dimensionsOrderString]
        "swap" : None,
        
        # [-fill color] 0-255
        "fill" : None,
        
        # [-pyramid-resolutions numResolutionLevels]
        "pyramidResolutions" : None
    }
    ret[Tools.CONVERT] = request

    return ret

template_request_dict: Dict = _create_template_requests()

def create_template_request(type: ToolConf):
    if type not in template_request_dict:
        raise ValueError(f"No template request for type {type.name}")
    return template_request_dict[type]

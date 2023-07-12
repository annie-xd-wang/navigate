# Copyright (c) 2021-2022  The University of Texas Southwestern Medical Center.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted for academic and research use only (subject to the
# limitations in the disclaimer below) provided that the following conditions are met:

#      * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.

#      * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.

#      * Neither the name of the copyright holders nor the names of its
#      contributors may be used to endorse or promote products derived from this
#      software without specific prior written permission.

# NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY
# THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
from aslm.model.features.auto_tile_scan import CalculateFocusRange # noqa
from aslm.model.features.autofocus import Autofocus # noqa
from aslm.model.features.common_features import (
    ChangeResolution, # noqa
    Snap, # noqa
    WaitToContinue, # noqa
    LoopByCount, # noqa
    PrepareNextChannel, # noqa
    MoveToNextPositionInMultiPostionTable, # noqa
    StackPause, # noqa
    ZStackAcquisition, # noqa
    ConProAcquisition, # noqa
    FindTissueSimple2D, # noqa
)
from aslm.model.features.image_writer import ImageWriter # noqa
from aslm.model.features.restful_features import IlastikSegmentation # noqa
from aslm.model.features.volume_search import VolumeSearch # noqa

def convert_str_to_feature_list(content: str):
    """Convert string to a feature list

    Parameters
    ----------
    content : str
        A string value that represents a feature list.

    Returns
    -------
    feature_list : List
        A list: If the string value can be converted to a valid feature list
        None: If can not.
    """
    def convert_args_to_tuple(feature_list):
        if not feature_list:
            return
        for item in feature_list:
            if type(item) is dict:
                if "args" in item and type(item["args"]) is not tuple:
                    item["args"] = (item["args"],)
            else:
                convert_args_to_tuple(item)

    try:
        exec_result = {}
        exec(f"result={content}", globals(), exec_result)
        if type(exec_result["result"]) is not list:
            print("Please make sure the feature list is a list!")
            return None
        # 'args' should be tuple
        convert_args_to_tuple(exec_result["result"])
        return exec_result["result"]
    except Exception as e:
        print("Can't build this feature list!", e)
        return None
    
def convert_feature_list_to_str(feature_list):
    """Convert a feature list to string

    Parameters
    ----------
    feature_list : List
        A valid feature list.

    Returns
    -------
    result : str
        The string of a valid feature list.
    """
    result = '['
    def f(feature_list):
        if not feature_list:
            return
        nonlocal result
        for item in feature_list:
            if type(item) is dict:
                result += '{' + f'"name": {item["name"].__name__},'
                if "args" in item:
                    result += f'"args": {str(item["args"])}'
                result += '},'
            elif type(item) is tuple:
                result += '('
                f(item)
                result += '),'
            elif type(item) is list:
                result += '['
                f(item)
                result += '],'
    
    f(feature_list)
    result += ']'
    return result
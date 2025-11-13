#
# (c) 2025, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from typing import Optional

from nexium_api import BaseRequestData


class GetAllRtmpsRequestData(BaseRequestData):
    pass


class GetRtmpRequestData(BaseRequestData):
    id_: int


class CreateRtmpRequestData(BaseRequestData):
    name: str
    value: str
    is_default: bool


class UpdateRtmpRequestData(BaseRequestData):
    id_: int
    is_default: bool
    name: Optional[str] = None
    value: Optional[str] = None


class DeleteRtmpRequestData(BaseRequestData):
    id_: int

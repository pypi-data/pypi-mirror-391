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


from nexium_api import route

from .base import Router
from .. import GetAllRtmpsRequestData, GetAllRtmpsResponseData, GetRtmpRequestData, GetRtmpResponseData, \
    CreateRtmpRequestData, CreateRtmpResponseData, DeleteRtmpResponseData, DeleteRtmpRequestData, UpdateRtmpRequestData, \
    UpdateRtmpResponseData


class RtmpRouter(Router):
    facade_service = 'RtmpFacadeService'
    prefix = '/rtmps'

    @route(
        path='/get-all',
        request_data=GetAllRtmpsRequestData,
        response_data=GetAllRtmpsResponseData,
        response_field='rtmps'
    )
    async def get_all(self):
        pass

    @route(
        path='/get',
        request_data=GetRtmpRequestData,
        response_data=GetRtmpResponseData,
        response_field='rtmp'
    )
    async def get(self):
        pass

    @route(
        path='/create',
        request_data=CreateRtmpRequestData,
        response_data=CreateRtmpResponseData,
        response_field='rtmp'
    )
    async def create(self):
        pass

    @route(
        path='/update',
        request_data=UpdateRtmpRequestData,
        response_data=UpdateRtmpResponseData,
        response_field='rtmp'
    )
    async def update(self):
        pass

    @route(
        path='/delete',
        request_data=DeleteRtmpRequestData,
        response_data=DeleteRtmpResponseData,
    )
    async def delete(self):
        pass

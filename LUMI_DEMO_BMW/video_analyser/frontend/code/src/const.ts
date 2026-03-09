// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// Licensed under the 【火山方舟】原型应用软件自用许可协议
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at 
//     https://www.volcengine.com/docs/82379/1433703
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License. 

export const ScreenWidth = 430;

export const ScreenHeight = 800;

export const BaseURL =
    process.env.NODE_ENV === 'development' ? '/api' : APP_CONTEXT.FAAS_URL;

const ASR_APP_ID = APP_CONTEXT.ASR_APP_ID;
const ASR_ACCESS_TOKEN = APP_CONTEXT.ASR_ACCESS_TOKEN;

export const AsrURL = `wss://openspeech.bytedance.com/api/v3/sauc/bigmodel?api_access_key=${ASR_ACCESS_TOKEN}&api_app_key=${ASR_APP_ID}&api_resource_id=volc.bigasr.sauc.duration`;

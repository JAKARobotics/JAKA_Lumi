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

import { BaseURL } from '@/const';

export function fetchVlmImg(ctxId: string, base64data: string) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => {
    controller.abort('timeout 1s');
  }, 1000);

  //
  const myHeaders = new Headers();
  myHeaders.append('Content-Type', 'application/json');
  // X-Context-Id: abc-123-wzs'
  myHeaders.append('X-Context-Id', ctxId);

  const raw = JSON.stringify({
    messages: [
      {
        role: 'user',
        content: [
          {
            type: 'text',
            text: '',
          },
          {
            type: 'image_url',
            image_url: {
              url: base64data,
            },
          },
        ],
      },
    ],
    model: 'bot-20241114164326-xlcc9',
  });

  fetch(BaseURL + '/v3/bots/chat/completions', {
    signal: controller.signal,
    method: 'POST',
    body: raw,
    headers: myHeaders,
  }).finally(() => {
    clearTimeout(timeoutId);
  });
}

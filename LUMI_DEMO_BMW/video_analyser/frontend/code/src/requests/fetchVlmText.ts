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

import { ChatCompletionChunk } from '@/types/llm';
import { BaseURL } from '@/const';
import { PostSSE } from '@/requests/PostSSE';
/**
 * 从服务器获取VLM文本数据
 * @param ctxId
 * @param base64data
 * @param text 要发送到服务器的文本
 * @param onChunkReceive 接收到数据块时的回调函数
 * @param onFinish 数据传输完成时的回调函数
 */
export const fetchVlmText = async (
  ctxId: string,
  base64data: string,
  text: string,
  onChunkReceive: (res: ChatCompletionChunk) => void,
  onFinish: (reqId: string) => void,
) => {
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
            text,
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
    stream: true,
  });

  const eventSource = new PostSSE(`${BaseURL}/v3/bots/chat/completions`, {
    body: raw,
    headers: myHeaders,
    onMessage: data => {
      const jsonResult = JSON.parse(data) as ChatCompletionChunk;
      baseChunkInfo = jsonResult;
      reqId = jsonResult?.id;

      const { transcript: content, data: audio } =
        jsonResult.choices[0].delta.audio || {};
      audioChunks = audio ? [...audioChunks, audio] : audioChunks;

      onChunkReceive({
        ...jsonResult,
        choices: [
          {
            ...jsonResult.choices[0],
            delta: {
              audio: {
                transcript: content,
                data: '',
              },
            },
          },
        ],
      });

      if (audioChunks.length && content) {
        sendFinalAudioChunk();
      }
    },
    onError: error => {
      onFinish(reqId);
    },
    onEnd: () => {
      sendFinalAudioChunk();
      onFinish(reqId);
    },
  });

  eventSource.connect()

  let reqId = '';
  let audioChunks: string[] = [];
  let baseChunkInfo: ChatCompletionChunk | undefined;

  const sendFinalAudioChunk = () => {
    if (audioChunks.length) {
      onChunkReceive({
        id: reqId,
        ...baseChunkInfo,
        choices: [
          {
            delta: {
              audio: {
                transcript: '',
                data: audioChunks.join(''),
              },
            },
          },
        ],
      } as ChatCompletionChunk);
      audioChunks = [];
      baseChunkInfo = undefined;
    }
  };
};

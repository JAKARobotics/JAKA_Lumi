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

import type { ASRResponseData } from '@/hooks/LabASR';
import {
  encodeAudioOnlyRequest,
  encodeFullClientRequest,
  parseResponse,
} from '@/hooks/LabASR/utils';
import { toast } from '@/utils/toast';
import { useRef } from 'react';
import { AsrURL } from '@/const';

export const useAsrWs = ({
  onAsrResp,
}: { onAsrResp: (res_json: any) => void }) => {
  const wsRef = useRef<WebSocket>();
  const retryCountRef = useRef(0);
  const connect = () => {
    return new Promise((resolve, reject) => {
      const socket = new WebSocket(AsrURL);

      socket.onopen = () => {
        const build = encodeFullClientRequest({
          user: {
            uid: 'ARK_VLM_DEMO',
          },
          audio: {
            format: 'pcm',
            rate: 16000,
            bits: 16,
            channel: 1,
          },
          request: {
            // @ts-expect-error
            model_name: 'bigmodel',
            result_type: 'single',
            show_utterances: true,
            // vad_segment_duration 失效
            // 强制判停时间
            end_window_size: 600,
            // 强制语音时间
            force_to_speech_time: 1500,
          },
        });
        socket.send(build);
        resolve(socket);
      };

      socket.onmessage = async e => {
        try {
          const res_json: ASRResponseData = await parseResponse(e.data);
          if (res_json.isError) {
            // 报错隐式重连 3 次
            retryCountRef.current = retryCountRef.current + 1;
            if (retryCountRef.current > 3) {
              toast('ASR 服务异常，请刷新后重试');
              return;
            }
            wsRef.current?.close();
            await connect();
          }
          onAsrResp?.(res_json);
        } catch (error) {
          console.error(error);
          reject(error);
        }
      };

      socket.onerror = error => {
        console.error('WebSocket error:', error);
        reject(error);
      };

      wsRef.current = socket;
    });
  };
  return {
    readyState: wsRef.current?.readyState,
    sendAudio: (pcm: Blob) => {
      const data = encodeAudioOnlyRequest(pcm);
      wsRef.current?.send(data);
    },
    connect,
    close: () => {
      wsRef.current?.close();
      wsRef.current = undefined;
    },
  };
};

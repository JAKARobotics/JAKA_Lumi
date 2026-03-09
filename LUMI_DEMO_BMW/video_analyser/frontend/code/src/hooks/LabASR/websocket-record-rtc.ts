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

import RecordRTC, { StereoAudioRecorder } from 'recordrtc';

import {
  encodeFullClientRequest,
  encodeAudioOnlyRequest,
  parseResponse,
} from './utils';
import { ASRResponseData, IClientRequestData } from './types';

interface WebsocketRecordRtcParams {
  onVadStop?: () => void;
  onStart?: () => void;
  onMessage?: (data: string, fullData: ASRResponseData) => void;
  onClose?: () => void;
  onError?: (errMsg: string) => void;
  onWSError?: (errMsg: Event) => void;
}

interface ConnectParams {
  url: string;
  config: IClientRequestData;
  debug?: boolean;
}

export function WebsocketRecordRtc(params: WebsocketRecordRtcParams = {}) {
  const context = {
    ...params,
    webSocket: undefined as WebSocket | undefined,
    mediaStream: undefined as MediaStream | undefined,
    recorder: undefined as RecordRTC | undefined,
    audioContext: undefined as AudioContext | undefined,
    vad: undefined as any | undefined,
  };
  /**
   *
   * @param url 服务端提供Socket服务的URL接口
   * @param postData Socket建立连接时发送到服务端的数据
   * @param onStart Socket连接建立成功时的回调函数
   * @param onMessage Socket包到达时的处理函数
   * @param onClose Socket连接关闭时的回调函数
   */
  function connect({ url, config, debug = false }: ConnectParams) {
    const { onStart, onMessage, onClose, onError, onWSError } = context;
    const socket = new WebSocket(url);
    context.webSocket = socket;

    socket.onopen = () => {
      debug && console.info('socket connected');
      const build = encodeFullClientRequest(config);
      socket.send(build);
      onStart?.();
    };

    socket.onmessage = async e => {
      try {
        const res_json: ASRResponseData = await parseResponse(e.data);
        const text = res_json?.result?.text ?? '';
        onMessage?.(text, res_json);
      } catch (error) {
        onError?.(JSON.stringify(error));
        console.error(error);
      }
    };

    socket.onclose = () => {
      debug && console.info('socket onclose disconnected');
      onClose?.();
    };

    socket.onerror = err => {
      debug && console.info('socket onerror disconnected');
      onWSError?.(err);
    };
  }

  async function startRecord(
    options?: RecordRTC.Options,
    handleRecordResult?: (RecordResult: Blob) => void,
  ) {
    const { onVadStop } = context;

    context.mediaStream = await window.navigator.mediaDevices.getUserMedia({
      audio: true,
    });

    context.audioContext = new AudioContext();

    context.recorder = new RecordRTC(context.mediaStream, {
      type: 'audio',
      recorderType: StereoAudioRecorder,
      mimeType: 'audio/wav',
      numberOfAudioChannels: 1,
      desiredSampRate: 16000,
      disableLogs: true,
      timeSlice: 100,
      ...options,
      ondataavailable(recordResult: Blob) {
        const socket = context.webSocket;
        if (!socket) {
          return;
        }

        handleRecordResult?.(recordResult);

        const pcm = recordResult.slice(44);
        const data = encodeAudioOnlyRequest(pcm);
        if (socket.readyState === socket.OPEN) {
          socket.send(data);
        }
      },
    });
    context.recorder.startRecording();
  }

  function stopRecord() {
    const { recorder, webSocket, mediaStream } = context;

    if (!recorder) {
      return;
    }

    recorder.stopRecording(() => {
      context.vad?.destroy();
      if (!webSocket) {
        return;
      }
      webSocket.close();

      mediaStream?.getAudioTracks().forEach(track => track.stop());
    });
  }

  return Object.freeze({
    connect,
    startRecord,
    stopRecord,
  });
}

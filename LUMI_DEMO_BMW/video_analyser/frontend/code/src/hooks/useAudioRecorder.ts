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

import { MutableRefObject, useEffect, useRef } from 'react';
import RecordRTC, { StereoAudioRecorder } from 'recordrtc';
import { useAsrWs } from '@/hooks/useAsrWs';
import { handleAsrResp } from '@/utils/handleAsrResp';
import { AudioData } from '@/types/asr';
import { useTrackUserSpeakWave } from '@/hooks/useTrackUserSpeakWave';
import { EChatState } from '@/providers/ChatProvider/context';

const forceDefiniteDuration = 500; // 2s 不返回新的识别结果 强制结束

export const useAudioRecorder = (
  setUserAudioWaveHeights: any,
  chatState: EChatState,
  streamRef: MutableRefObject<MediaStream | undefined>,
  onTextUpdateCb: (text: string) => void,
  onAsrDefinite: (text: string) => void,
) => {
  const isRecordingRef = useRef(false);
  const recorderRef = useRef<RecordRTC | null>(null);

  // const currentIdxRef = useRef(0);

  const lastedSpeakDuration = useRef(0); // 上次语音的时间，前端用来提前判停，但依赖接口返回消息，如果直接不返回就无法判断
  const lastedAsrResult = useRef('');
  const isAlreadyDefinite = useRef(false);

  // asr 有时会很久都不返回消息，如果此时已经有 text 了，就直接 definite
  const lastMsgTimeRef = useRef(0);
  const timerRef = useRef(0);

  const startCheckHealth = () => {
    timerRef.current = window.setInterval(() => {
      if (isAlreadyDefinite.current) {
        return;
      }
      const duration = Date.now() - lastMsgTimeRef.current;
      if (duration > forceDefiniteDuration) {
        if (lastedAsrResult.current) {
          onAsrDefinite(lastedAsrResult.current);
          lastedAsrResult.current = '';
          isAlreadyDefinite.current = true;
        }
      }
    }, 2000);
  };
  useEffect(() => {
    return () => {
      timerRef.current && clearInterval(timerRef.current);
    };
  }, []);

  const audioContextRef = useRef<AudioContext>();

  // 记录从开始录制，到 definite 之间的时间差
  const currentText = useRef('');
  const startTimeRef = useRef(0);

  const { close, connect, sendAudio, readyState } = useAsrWs({
    onAsrResp: (resp: AudioData) => {
      // asr 接口，可能在 definite 之后，还会有其他的 resp，需要在 definite 之后，直接断开
      lastMsgTimeRef.current = Date.now();
      const duration = resp?.audio_info?.duration;
      handleAsrResp(
        resp,
        text => {
          if (text !== currentText.current) {
            currentText.current = text;
            startTimeRef.current = Date.now();
          }

          if (text !== lastedAsrResult.current) {
            lastedAsrResult.current = text;

            lastedSpeakDuration.current = duration;
          } else {
            if (!text) {
              return;
            }
            // 这次结果和上次结果相同
            const gapDuration = duration - lastedSpeakDuration.current; // 用户没有说话的时间间隔
            if (gapDuration > forceDefiniteDuration) {
              // 强制结束
              if (!isAlreadyDefinite.current) {
                onAsrDefinite(text);
                isAlreadyDefinite.current = true;
              }
              currentText.current == '';
              return;
            }
          }
          onTextUpdateCb(text);
        },
        text => {
          currentText.current == '';
          if (!isAlreadyDefinite.current) {
            onAsrDefinite(text);
            isAlreadyDefinite.current = true;
          }
        },
      );
    },
  });

  const { startTrack, stopTrack } = useTrackUserSpeakWave(
    audioContextRef,
    streamRef,
    setUserAudioWaveHeights,
    chatState,
  );

  const startRecording = async () => {
    if (streamRef.current) {
      if (readyState !== WebSocket.OPEN) {
        await connect();
      }
      isAlreadyDefinite.current = false; //reset
      audioContextRef.current = new AudioContext();

      recorderRef.current && recorderRef.current.destroy();

      recorderRef.current = new RecordRTC(streamRef.current, {
        type: 'audio',
        recorderType: StereoAudioRecorder,
        mimeType: 'audio/wav',
        numberOfAudioChannels: 1,
        desiredSampRate: 16000,
        disableLogs: true,
        timeSlice: 100,
        ondataavailable(recordResult: Blob) {
          const ctx = audioContextRef.current;
          if (ctx) {
            ctx.resume();
          }

          const pcm = recordResult.slice(44);

          sendAudio(pcm);
        },
      });
      isRecordingRef.current = true;
      recorderRef.current.startRecording();
      startTrack();
      startCheckHealth();
    }
  };

  const stopRecording = () => {
    if (recorderRef.current) {
      recorderRef.current.stopRecording();
      isRecordingRef.current = false;
      const ctx = audioContextRef.current;
      if (ctx) {
        ctx.suspend();
        stopTrack();
      }
      // 停止时 关闭 websocket
      close();

      clearInterval(timerRef.current);
      timerRef.current = 0;
    }
  };

  return {
    startRecording,
    stopRecording,
    // , pauseRecording, resumeRecording,
    connectAsrWs: async () => {
      await connect();
    },
  };
};

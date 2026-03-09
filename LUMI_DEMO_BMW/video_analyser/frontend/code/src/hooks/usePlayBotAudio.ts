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

import { useState, useEffect, useRef, useCallback } from 'react';
import { base64ToArrayBuffer } from '@/utils/base64ToArrayBuffer';

interface UseAudioPlayerResult {
  isPlaying: boolean; // 是否正在播放
  isPaused: boolean; // 是否暂停
  play: () => void; // 开始播放
  pause: () => void; // 暂停播放
  resume: () => void; // 恢复播放
  stop: () => void; // 停止播放
  addAudio: (base64data: string) => void; // 添加音频数据
  resetAudio: () => void; // 重置音频数据
  audioContext: AudioContext | null; // AudioContext 对象
  markAudioDataFinished: () => void; // 标记音频数据全部加完
}

/**
 * 音频播放器 Hook
 * @returns {UseAudioPlayerResult} 音频播放器的状态和控制方法
 */
export const usePlayBotAudio = (
  onAudioEnded?: () => void,
  isQueue?: boolean,
): UseAudioPlayerResult => {
  const [isPlaying, setIsPlaying] = useState<boolean>(false); // 是否正在播放
  const [isPaused, setIsPaused] = useState<boolean>(false); // 是否暂停
  const audioContextRef = useRef<AudioContext | null>(null); // AudioContext 对象的引用
  const sourceRef = useRef<AudioBufferSourceNode | null>(null); // AudioBufferSourceNode 对象的引用
  const audioDataRef = useRef<string[]>([]); // 待播放的音频数据数组

  //  如果是队列，则需要标记音频数据全部加完，否则不执行 onEnded 回调
  const audioDataFinishedRef = useRef(false);

  const markAudioDataFinished = () => {
    audioDataFinishedRef.current = true;
  };

  /**
   * 初始化 AudioContext 和清理函数
   */
  useEffect(() => {
    audioContextRef.current = new AudioContext();

    return () => {
      if (audioContextRef.current) {
        audioContextRef.current.close();
        audioContextRef.current = null;
      }
    };
  }, []);

  /**
   * 播放下一个音频
   */
  const playNextAudio = useCallback(async () => {
    if (audioDataRef.current.length > 0 && audioContextRef.current) {
      const b64 = audioDataRef.current.shift();

      if (b64) {
        sourceRef.current = audioContextRef.current.createBufferSource();
        console.log('#b64', b64);
        const arrayBuffer = base64ToArrayBuffer(b64);
        const audioData = await audioContextRef.current.decodeAudioData(
          new Uint8Array(arrayBuffer).buffer,
        );
        sourceRef.current.buffer = audioData;
        sourceRef.current.connect(audioContextRef.current.destination);
        if (sourceRef.current) {
          sourceRef.current.addEventListener('ended', () => {
            playNextAudio();
          });
        }

        sourceRef.current.start(0);
        setIsPlaying(true);
        setIsPaused(false);
      }
    } else {
      setIsPlaying(false);
      setIsPaused(false);
      // 如果不是队列，则直接执行 onEnded 回调
      const shouldExecEndCallback = !isQueue || audioDataFinishedRef.current;

      if (shouldExecEndCallback) {
        onAudioEnded?.();
        audioDataFinishedRef.current = false; // reset
      }
    }
    return () => {
      if (sourceRef.current) {
        sourceRef.current.removeEventListener('ended', playNextAudio);
      }
    };
  }, [onAudioEnded]);

  /**
   * 开始播放音频
   */
  const play = useCallback(() => {
    if (!isPlaying) {
      playNextAudio();
    }
  }, [isPlaying, playNextAudio]);

  /**
   * 暂停播放音频
   */
  const pause = useCallback(() => {
    if (isPlaying && !isPaused && sourceRef.current) {
      sourceRef.current.stop();
      setIsPaused(true);
      setIsPlaying(false);
    }
  }, [isPlaying, isPaused]);

  /**
   * 恢复播放音频
   */
  const resume = useCallback(() => {
    if (isPlaying && isPaused && sourceRef.current) {
      sourceRef.current.start();
      setIsPaused(false);
    }
  }, [isPlaying, isPaused]);

  /**
   * 停止播放音频
   */
  const stop = useCallback(() => {
    if (isPlaying && sourceRef.current) {
      sourceRef.current.stop();
      setIsPlaying(false);
      setIsPaused(false);
    }
  }, [isPlaying]);

  /**
   * 添加音频数据
   * @param {ArrayBuffer} audioData - 音频数据
   */
  const addAudio = useCallback(
    async (base64data: string) => {
      if (!audioContextRef.current) {
        return;
      }
      audioDataRef.current.push(base64data);
    },
    [isPlaying, playNextAudio],
  );

  /**
   * 重置音频数据
   */
  const resetAudio = useCallback(() => {
    if (sourceRef.current) {
      sourceRef.current.stop();
      setIsPlaying(false);
      setIsPaused(false);
    }
    audioDataRef.current = [];
  }, [sourceRef.current]);
  return {
    markAudioDataFinished,
    audioContext: audioContextRef.current,
    isPlaying,
    isPaused,
    play,
    pause,
    resume,
    stop,
    addAudio,
    resetAudio,
  };
};

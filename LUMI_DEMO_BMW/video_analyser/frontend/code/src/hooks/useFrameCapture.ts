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

import { ScreenHeight, ScreenWidth } from '@/const';
import { canvasHelper } from '@/utils/canvasDrawHelper';
import { RefObject, useRef } from 'react';

export const useFrameCapture = (
  videoRef: RefObject<HTMLVideoElement>,
  onFrameCap: (base64data: string) => void,
) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const intervalIdRef = useRef<number | null>(null);

  const capture = () => {
    let dataURL = '';
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current;
      const video = videoRef.current;
      //
      canvas.width = ScreenWidth;
      canvas.height = ScreenHeight;

      const ctx = canvas.getContext('2d');

      if (ctx) {
        const [sx, sy, sw, sh] = canvasHelper.aspectFill(
          video.videoWidth,
          video.videoHeight,
          ScreenWidth,
          ScreenHeight,
        );
        ctx.drawImage(video, sx, sy, sw, sh, 0, 0, ScreenWidth, ScreenHeight); // 相当于 object-fit: cover
        dataURL = canvas.toDataURL('image/png');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
    }
    return dataURL;
  };
  const captureFrame = () => {
    const dataURL = capture();
    if (dataURL) {
      onFrameCap(dataURL);
    }
  };

  const startCapture = () => {
    if (intervalIdRef.current) {
      window.clearInterval(intervalIdRef.current);
      intervalIdRef.current = null;
    }
    intervalIdRef.current = window.setInterval(captureFrame, 1000);
  };

  const stopCapture = () => {
    if (intervalIdRef.current) {
      window.clearInterval(intervalIdRef.current);
    }
  };

  return { canvasRef, startCapture, stopCapture, capture };
};

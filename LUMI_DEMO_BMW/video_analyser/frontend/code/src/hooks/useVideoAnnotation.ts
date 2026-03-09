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

import { RefObject, useCallback } from 'react';
import { useFrameCapture } from './useFrameCapture';
import { ScreenHeight, ScreenWidth } from '@/const';
import { AnnoRef } from '@/components/DrawingBoard';

const drawPath = (
  ctx: CanvasRenderingContext2D,
  points: [number, number][],
) => {
  if (points.length < 2) return;
  ctx.beginPath();
  ctx.moveTo(points[0][0], points[0][1]);

  for (let i = 1; i < points.length; i++) {
    ctx.lineTo(points[i][0], points[i][1]);
  }

  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = 4;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  ctx.stroke();
};

export const useVideoAnnotation = (
  videoRef: RefObject<HTMLVideoElement>,
  annoRef: RefObject<AnnoRef>,
  onFrameCap: (base64data: string) => void,
) => {
  const {
    canvasRef: frameCanvasRef,
    capture,
    startCapture,
    stopCapture,
  } = useFrameCapture(videoRef, onFrameCap);

  const captureAnnotatedFrame = useCallback(async () => {
    const frameBase64 = capture();
    const anno = annoRef.current;
    if (frameBase64 && anno) {
      const points = anno.getAnnotations();
      const finalImage = await mergeAnnotation(frameBase64, points);
      anno.clearAnnotations();
      return finalImage;
    }
    return '';
  }, [capture]);

  // 合并视频帧和标注
  const mergeAnnotation = useCallback(
    async (
      frameBase64: string,
      points: [number, number][],
    ): Promise<string> => {
      return new Promise((resolve, reject) => {
        const canvas = document.createElement('canvas');
        canvas.width = ScreenWidth;
        canvas.height = ScreenHeight;

        const img = new Image();
        const ctx = canvas.getContext('2d');

        img.onload = () => {
          if (!ctx) {
            reject(new Error('Failed to get canvas context'));
            return;
          }
          ctx.drawImage(img, 0, 0, ScreenWidth, ScreenHeight);
          drawPath(ctx, points);
          const finalImage = canvas.toDataURL('image/jpeg');
          resolve(finalImage);
        };

        img.onerror = () => {
          reject(new Error('Failed to load image'));
        };

        img.src = frameBase64;
      });
    },
    [],
  );

  return {
    frameCanvasRef,
    startCapture,
    stopCapture,
    captureAnnotatedFrame,
  };
};

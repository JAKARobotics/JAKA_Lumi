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

import React, {
  useRef,
  useEffect,
  PropsWithChildren,
  forwardRef,
  useImperativeHandle,
} from 'react';
import { ScreenHeight, ScreenWidth } from '@/const';

export interface DrawingBoardProps {
  disabled?: boolean;
}
export interface AnnoRef {
  clearAnnotations: () => void;
  getAnnotations: () => [number, number][];
  removeDisplayedPaths: () => void;
}

const getOffsetPosition = (e: MouseEvent | TouchEvent) => {
  if ('touches' in e) {
    const touch = e.touches[0];
    return [touch.clientX, touch.clientY];
  } else {
    return [e.offsetX, e.offsetY];
  }
};

export const DrawingBoard = forwardRef<
  AnnoRef,
  PropsWithChildren<DrawingBoardProps>
>(({ children, disabled }, ref) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const isDrawingRef = useRef<boolean>(false);
  const lastXRef = useRef<number>(0);
  const lastYRef = useRef<number>(0);
  const lineWidthRef = useRef<number>(5);
  const pathsRef = useRef<any[]>([]);
  const tempPathsRef = useRef<any[]>([]);
  const annotationsRef = useRef<[number, number][]>([]);
  // 记录所有的标注
  const recordAnno = (x: number, y: number) => {
    annotationsRef.current = [...annotationsRef.current, [x, y]];
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');

    if (canvas && ctx) {
      canvas.width = ScreenWidth;
      canvas.height = ScreenHeight;

      const startDrawing = (e: MouseEvent | TouchEvent) => {
        e.stopPropagation();
        isDrawingRef.current = true;
        const [offsetX, offsetY] = getOffsetPosition(e);
        [lastXRef.current, lastYRef.current] = [offsetX, offsetY];
        recordAnno(offsetX, offsetY);
      };

      const draw = (e: MouseEvent | TouchEvent) => {
        if (!isDrawingRef.current || !ctx) return;

        const [offsetX, offsetY] = getOffsetPosition(e);
        recordAnno(offsetX, offsetY);

        ctx.strokeStyle = '#fff';
        ctx.lineWidth = lineWidthRef.current;
        ctx.lineCap = 'round';
        ctx.shadowBlur = 10;
        ctx.shadowColor = '#fff';

        ctx.beginPath();
        ctx.moveTo(lastXRef.current, lastYRef.current);
        ctx.lineTo(offsetX, offsetY);
        ctx.stroke();

        tempPathsRef.current.push({
          from: { x: lastXRef.current, y: lastYRef.current },
          to: { x: offsetX, y: offsetY },
          width: lineWidthRef.current,
          opacity: 1,
          timestamp: Date.now(),
        });

        [lastXRef.current, lastYRef.current] = [offsetX, offsetY];

        lineWidthRef.current += 0.2;
        if (lineWidthRef.current > 6) {
          lineWidthRef.current = 6;
        }
      };

      const stopDrawing = () => {
        isDrawingRef.current = false;
        lineWidthRef.current = 5;
      };

      canvas.addEventListener('mousedown', startDrawing);
      canvas.addEventListener('mousemove', draw);
      canvas.addEventListener('mouseup', stopDrawing);
      canvas.addEventListener('mouseout', stopDrawing);

      canvas.addEventListener('touchstart', startDrawing);
      canvas.addEventListener('touchmove', draw);
      canvas.addEventListener('touchend', stopDrawing);
      canvas.addEventListener('touchcancel', stopDrawing);

      return () => {
        canvas.removeEventListener('mousedown', startDrawing);
        canvas.removeEventListener('mousemove', draw);
        canvas.removeEventListener('mouseup', stopDrawing);
        canvas.removeEventListener('mouseout', stopDrawing);

        canvas.removeEventListener('touchstart', startDrawing);
        canvas.removeEventListener('touchmove', draw);
        canvas.removeEventListener('touchend', stopDrawing);
        canvas.removeEventListener('touchcancel', stopDrawing);
      };
    }
  }, []);

  const clearAnnotations = () => {
    annotationsRef.current = [];
  };
  const getAnnotations = () => {
    return annotationsRef.current;
  };
  const removeDisplayedPaths = () => {
    const startTime = Date.now();
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    if (!canvas || !ctx) {
      return;
    }
    const animate = () => {
      const elapsedTime = Date.now() - startTime;
      const opacity = 1 - elapsedTime / 1000;

      if (opacity <= 0) {
        pathsRef.current = [];
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        return;
      }

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      pathsRef.current.forEach(path => {
        ctx.lineWidth = path.width;
        ctx.lineCap = 'round';
        ctx.strokeStyle = `rgba(255, 255, 255, ${opacity})`;

        ctx.beginPath();
        ctx.moveTo(path.from.x, path.from.y);
        ctx.lineTo(path.to.x, path.to.y);
        ctx.stroke();
      });

      requestAnimationFrame(animate);
    };

    requestAnimationFrame(animate);
  };

  useImperativeHandle(ref, () => {
    return {
      getAnnotations,
      clearAnnotations,
      removeDisplayedPaths,
    };
  });

  return (
    <div
      className={
        'absolute left-0 top-0 w-full h-full  border-blue-400 rounded-md border overflow-hidden'
      }
    >
      {children}
      <canvas
        ref={canvasRef}
        className={'absolute left-0 top-0 w-full h-full z-20 touch-none '}
      />
    </div>
  );
});

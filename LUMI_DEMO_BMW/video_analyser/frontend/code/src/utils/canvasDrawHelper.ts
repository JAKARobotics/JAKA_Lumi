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

/**
 * 保持纵横比缩放图片
 * @description 只保证图片的短边能完全显示出来。也就是说，图片通常只在水平或垂直方向是完整的，另一个方向将会发生截取。
 * @param imageWidth
 * @param imageHeight
 * @param canvasWidth
 * @param canvasHeight
 * @returns
 */
const aspectFill = (
  imageWidth: number,
  imageHeight: number,
  canvasWidth: number,
  canvasHeight: number,
) => {
  const imageRate = imageWidth / imageHeight;
  const canvasRate = canvasWidth / canvasHeight;
  let [sx, sy, sw, sh] = [] as number[];
  if (imageRate >= canvasRate) {
    sw = imageHeight * canvasRate;
    sh = imageHeight;
    sx = (imageWidth - sw) / 2;
    sy = 0;
  } else {
    sh = imageWidth / canvasRate;
    sw = imageWidth;
    sx = 0;
    sy = (imageHeight - sh) / 2;
  }
  return [sx, sy, sw, sh] as [number, number, number, number];
};

export const canvasHelper = {
  aspectFill,
};

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
 * 获取最佳的视频流配置
 * @description 其中宽高不超过 1920 * 1080，帧率不超过 25。因为太大了会导致卡顿
 * @param stream 初始媒体流
 * @param videoDevices 视频输入设备列表
 * @param screenWidth 屏幕宽度
 * @param screenHeight 屏幕高度
 */
export const getBestVideoSettings = async (
  stream: MediaStream,
  videoDevices: MediaDeviceInfo[],
  screenWidth: number,
  screenHeight: number,
): Promise<{
  deviceId: string;
  maxHeight: number;
  maxWidth: number;
  maxFramerate: number;
}> => {
  const tracks = stream.getTracks();
  let deviceId = '';
  let maxHeight = 0;
  let maxWidth = 0;
  let maxFramerate = 30;
  const aspectRatio = screenWidth / screenHeight;

  for (const track of tracks) {
    const capabilities = track.getCapabilities();
    const { height, width, deviceId: _deviceId, frameRate } = capabilities;
    // 获取最大帧率,不超过 25

    if (videoDevices.some(device => device.deviceId === _deviceId)) {
      maxFramerate = Math.min(frameRate?.max || maxFramerate, maxFramerate);
      deviceId = _deviceId || '';
      // 获取最大高度,不超过 1920
      maxWidth = Math.min(height?.max || 0, 1920);
      // 根据宽高比计算最大宽度,不超过 1080
      maxHeight = Math.min(maxWidth * aspectRatio, 1080);
      //   maxHeight = height?.max || 0;
      //   maxWidth = aspectRatio * maxHeight;
    }
  }

  return { deviceId, maxHeight, maxWidth, maxFramerate };
};

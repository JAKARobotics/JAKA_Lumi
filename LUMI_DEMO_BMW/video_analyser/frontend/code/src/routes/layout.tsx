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

import setRootPixel from '@arco-design/mobile-react/tools/flexible';
import { Outlet, useNavigate } from '@modern-js/runtime/router';

import './index.css';
import '@arco-design/mobile-react/esm/style';
import '@arco-design/web-react/dist/css/arco.css';
// import 'vconsole';
setRootPixel();
import React, { useEffect } from 'react';
import VConsole from 'vconsole';
import { ScreenHeight, ScreenWidth } from '@/const';
// const vConsole = new VConsole();

export default function Layout() {
  const navigate = useNavigate();
  useEffect(() => {
    navigate('/chat/auth');
  }, []);
  return (
    <div className={'w-screen h-screen flex justify-center items-center '}>
      <div
        className={'relative overflow-hidden'}
        style={{
          width: ScreenWidth,
          height: ScreenHeight,
        }}
      >
        <Outlet />
      </div>
    </div>
  );
}

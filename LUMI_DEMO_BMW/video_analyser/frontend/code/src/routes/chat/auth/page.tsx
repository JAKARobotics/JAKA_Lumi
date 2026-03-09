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

import { Logo } from '@/images/Logo';
import './index.css';
import { ChatContext } from '@/providers/ChatProvider/context';
import { useNavigate } from '@modern-js/runtime/router';
import { useContext } from 'react';
import { usePreviewConfig } from '@/hooks/usePreviewConfig';
import { Button, Switch } from '@arco-design/web-react';

const Demo = () => {
  const navigate = useNavigate();
  const { start } = useContext(ChatContext);
  const { previewConfig, setPreviewConfig } = usePreviewConfig();
  async function enterFullscreenPortrait() {
    try {
      await document.documentElement.requestFullscreen();
      if (screen.orientation && screen.orientation?.lock) {
        await screen.orientation?.lock('portrait');
      }
    } catch (error) {
      console.error('Error entering fullscreen or locking orientation:', error);
    }
  }
  const handleClick = async () => {
    // try {
    //   await enterFullscreenPortrait();
    // } catch (error) {}
    await start();
    navigate('/chat');
  };
  return (
    <div
      className={
        'absolute left-0 top-0 w-full h-full bg-[#333] flex flex-col items-center justify-center  border-blue-400 rounded-md border'
      }
    >
      <Logo />
      <div className={'demo mt-[24px] mb-[44px]'}>VLM DEMO</div>
      <div className="text-white text-[16px] font-medium flex flex-col gap-1 mb-2">
        <div className={'flex items-center gap-1'}>
          <span>打断</span>
          <Switch
            checked={previewConfig.showInterruptBtn}
            onChange={v =>
              setPreviewConfig(prev => ({ ...prev, showInterruptBtn: v }))
            }
          />
        </div>
        <div className={'flex items-center gap-1'}>
          <span>字幕</span>
          <Switch
            checked={previewConfig.showCaption}
            onChange={v =>
              setPreviewConfig(prev => ({ ...prev, showCaption: v }))
            }
          />
        </div>
      </div>
      <Button
        onClick={() => {
          handleClick();
        }}
        shape={'round'}
        className={'w-[200px]'}
      >
        试用 Demo
      </Button>
    </div>
  );
};

export default Demo;

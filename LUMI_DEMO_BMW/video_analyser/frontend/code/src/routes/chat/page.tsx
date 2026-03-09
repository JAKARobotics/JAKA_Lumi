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

import { BotThinkingBtn } from '@/components/BotThinkingBtn';
import { ChatBubbleList } from '@/components/ChatBubbleList';
import { DrawingBoard } from '@/components/DrawingBoard';
import { InterruptBtn } from '@/components/InterruptBtn';
import VoiceBubble, { BubbleState } from '@/components/VoiceBubble';
import { ScreenHeight, ScreenWidth } from '@/const';
import { IconClose } from '@/images/IconClose';
import { ChatContext, EChatState } from '@/providers/ChatProvider/context';
import { useNavigate } from '@modern-js/runtime/router';
import React, { useContext, useEffect } from 'react';
import { Border } from '@/components/Border';
import { useSpring, animated } from 'react-spring';
import clsx from 'classnames';
import { usePreviewConfig } from '@/hooks/usePreviewConfig';
const Chat = () => {
  const { previewConfig } = usePreviewConfig();
  const {
    annoRef,
    interrupt,
    stop,
    userPrompt,
    botContent,
    chatState,
    playVideoWithStream,
    videoRef,
    frameCanvasRef,
  } = useContext(ChatContext);
  const navigate = useNavigate();
  useEffect(() => {
    if (chatState === EChatState.Idle) {
      navigate('/chat/auth');
      return;
    }
  }, [chatState]);
  useEffect(() => {
    playVideoWithStream();
  }, []);

  const handleInterrupt = () => {
    interrupt();
  };

  const handleClose = () => {
    stop();
    navigate('/chat/auth');
  };

  const showBorder = chatState === EChatState.BotThinking;

  const borderStyles = useSpring({
    from: { opacity: 0 },
    to: { opacity: showBorder ? 1 : 0 },
    config: { duration: 500 },
  });
  const videoStyles = useSpring({
    width: showBorder ? ScreenWidth - 14 : ScreenWidth,
    height: showBorder ? ScreenHeight - 14 : ScreenHeight,
    top: showBorder ? 7 : 0,
    left: showBorder ? 7 : 0,
    right: showBorder ? 7 : 0,
    bottom: showBorder ? 7 : 0,
    borderRadius: showBorder ? 7 : 0,
    config: { duration: 300 },
  });

  return (
    <DrawingBoard
      ref={annoRef}
      disabled={chatState !== EChatState.UserSpeaking}
    >
      <div
        className={
          'z-10 opacity-60 absolute top-0 w-full h-[360px] bg-gradient-to-t from-black/20 to-black/100'
        }
      />
      <IconClose
        onClick={() => handleClose()}
        className={'absolute top-[42px] left-[42px] z-30'}
      />
      <animated.video
        style={videoStyles}
        className={clsx(
          'absolute object-cover z-10 border-blue-400 rounded-md border',
          showBorder ? 'rounded-[7px]' : '',
        )}
        muted
        ref={videoRef}
        autoPlay
        playsInline
      />
      {/* 用于抽帧 */}
      <canvas
        ref={frameCanvasRef}
        style={{ display: 'none' }}
        className={'w-full h-full'}
      />
      {previewConfig.showCaption && (
        <ChatBubbleList
          className={'absolute bottom-[200px] z-20'}
          userContent={userPrompt}
          botContent={botContent}
        />
      )}
      {/*底部*/}
      <div className={'absolute w-full bottom-0 h-[360px]'}>
        {/*底部控制按钮*/}
        <div
          className={'w-full flex justify-center absolute bottom-[80px] z-30'}
        >
          {chatState === EChatState.UserSpeaking && (
            <VoiceBubble state={BubbleState.RECORDING} />
          )}
          {chatState === EChatState.BotSpeaking &&
            previewConfig.showInterruptBtn && (
              <InterruptBtn onClick={handleInterrupt} />
            )}
          {chatState === EChatState.BotThinking && <BotThinkingBtn />}
        </div>
        <div
          className={
            'z-10 absolute bottom-0 w-full h-[360px] bg-gradient-to-b from-black/0 to-black/60'
          }
        />
      </div>
      {showBorder && (
        <animated.div style={borderStyles}>
          {showBorder && <Border />}
        </animated.div>
      )}
    </DrawingBoard>
  );
};
export default Chat;

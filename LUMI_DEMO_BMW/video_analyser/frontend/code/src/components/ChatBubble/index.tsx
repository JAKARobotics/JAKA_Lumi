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

import clsx from 'classnames';
import s from './index.module.less';
import { IconDoubao } from '@/images/IconDoubao';
import { ChatContext, EChatState } from '@/providers/ChatProvider/context';
import { useContext } from 'react';
import { animated, useTransition } from 'react-spring';

export interface IChatBubbleProps {
  role: 'user' | 'bot';
  content: string;
}

export const ChatBubble = ({ role, content }: IChatBubbleProps) => {
  const { chatState } = useContext(ChatContext);

  const userBubbleTransitions = useTransition(!!content, {
    from: { opacity: 0, transform: 'translateY(-20px)' },
    enter: { opacity: 1, transform: 'translateY(0)' },
    leave: { opacity: 0, transform: 'translateY(-20px)' },
    config: { duration: 150 },
  });

  const botBubbleTransitions = useTransition(
    chatState !== EChatState.UserSpeaking,
    {
      from: { opacity: 0, transform: 'translateY(-20px)' },
      enter: { opacity: 1, transform: 'translateY(0)' },
      leave: { opacity: 0, transform: 'translateY(-20px)' },
      config: { duration: 150 },
    },
  );

  if (role === 'user') {
    return userBubbleTransitions((style, item) =>
      item ? (
        <animated.div
          style={style}
          className={clsx(
            'p-[12px] text-white text-[16px] max-w-[80vw] h-fit',
            s.bubbleUser,
          )}
        >
          <div>{content}</div>
        </animated.div>
      ) : null,
    );
  }

  return botBubbleTransitions((style, item) =>
    item ? (
      <animated.div
        style={style}
        className={clsx(
          'p-[12px] text-white text-[16px] max-w-[80vw] h-fit',
          s.bubbleBot,
        )}
      >
        {chatState === EChatState.BotThinking ? (
          <div className={'flex items-center justify-center'}>
            <IconDoubao /> <div className="text-white text-[16px]">...</div>
          </div>
        ) : (
          <div>{content}</div>
        )}
      </animated.div>
    ) : null,
  );
};

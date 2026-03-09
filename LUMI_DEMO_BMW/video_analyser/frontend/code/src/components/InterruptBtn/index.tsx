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

export const InterruptBtn = ({ onClick }: { onClick: () => void }) => {
  return (
    <div
      onClick={onClick}
      className={
        'flex flex-col justify-center items-center gap-[4px] text-white text-[16px] font-medium'
      }
    >
      <div className={'w-[20px] h-[20px] bg-white rounded-[6px]'} />
      <div>点击打断</div>
    </div>
  );
};

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

export const IconClose = ({
  onClick,
  className,
}: { onClick: () => void; className: string }) => {
  return (
    <svg
      className={className}
      onClick={onClick}
      width="28"
      height="28"
      viewBox="0 0 28 28"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <g id="Group">
        <path
          id="Vector"
          d="M7.30933 4.44142L8.6475 6.35359C7.02138 7.49198 5.80055 9.11917 5.16236 10.9988C4.52417 12.8784 4.50186 14.9125 5.09868 16.8057C5.69549 18.6988 6.88034 20.3524 8.4811 21.5262C10.0819 22.7 12.0152 23.3328 14.0002 23.3328C15.9852 23.3328 17.9185 22.7 19.5192 21.5262C21.12 20.3524 22.3048 18.6988 22.9017 16.8057C23.4985 14.9125 23.4762 12.8784 22.838 10.9988C22.1998 9.11917 20.979 7.49198 19.3528 6.35359L20.691 4.44142C22.2286 5.51642 23.4839 6.94678 24.3502 8.61093C25.2165 10.2751 25.6682 12.1238 25.6668 13.9999C25.6668 20.4434 20.4437 25.6666 14.0002 25.6666C7.55667 25.6666 2.3335 20.4434 2.3335 13.9999C2.33215 12.1238 2.78382 10.2751 3.65012 8.61093C4.51642 6.94678 5.77173 5.51642 7.30933 4.44142ZM12.8335 13.9999V2.33325H15.1668V13.9999H12.8335Z"
          fill="#fff"
        />
      </g>
    </svg>
  );
};

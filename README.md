# CRay

### 1.概述：
基于Reflexion框架+DeepSeek API实现一个代码编写助手。

### 2.实验：
在HumanEval coding benchmark上进行测试

### 3.实验对比：
1）Reflexion+DeepSeek比纯DeepSeek的提升

2）当前最强开源编码大模型DeepSeek与通用大模型GPT-4在代码编写能力上的对比

### 4.工程：
基于上述“Reflexion框架+DeepSeek API”的技术方案，实现一个“LeetCode解题助手”，使用最新的LeetCode题目进行评测。实现了简单的文字交互界面，命令行调用。

目前能比较好的解决leetcode的“简单”级别问题。

现在的技术框架是Reflexion+DeepSeek API，作为对比，对于LeetCode简单问题，单纯调用DeepSeek API的成功率大概5/9，加入Reflexion后能达到8/9

### 5.相关资源：
Paper：Reflexion: Language Agents with Verbal Reinforcement Learning 
( [NeurIPS 2023] ，https://arxiv.org/abs/2303.11366) 

Reflexion：https://github.com/noahshinn/reflexion 

DeepSeek API：https://platform.deepseek.com/api-docs/zh-cn/

### 6.To Setup & Run

1) Clone this repo and move to the programming_runs directory:
```bash
git clone https://github.com/CRay2005/Reflexion-DeepSeek && cd ./programming_runs
```

2) Install the module dependencies into your environment:
```bash
conda create -n your_env_name python=X.X
pip install -r requirements.txt
```

3) Set `OPENAI_API_KEY` environment variable to your DeepSeek API key:
```bash
#./reflexion/programming_runs/generators/model.py
export OPENAI_API_KEY=<your key>
```
去DeepSeek申请一个api-key

https://platform.deepseek.com/api-docs/zh-cn/

然后用申请到的api-key替换model.py文件里的API_KEY

### 7.其它
关于openai库安装的说明

官网的介绍是pip install openai。不过它没说Python版本最好<=3.8。

若Python版本过高，到达了3.11，会出现以下报错：

ImportError: cannot import name 'OpenAI' from 'openai'

因此请直接使用Python==3.8。

更新（2024/07/16）

现在openai更新了，python高版本也可支持，直接运行这行指令试试吧：

pip install openai --upgrade


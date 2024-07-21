# CRay

## 1.概述：
<p>《论文《Reflexion: Language Agents with Verbal Reinforcement Learning》提出了一个新框架Reflexion，通过语言反馈来加强Agent的能力使其能够快速有效地从试错中学习。<p>
<p>基于该论文的Reflexion理论框架和提供的代码，接入当前在数学和代码生成方面表现优异的开源模型DeepSeek。验证了Reflexion框架结合DeepSeek模型在HumanEval测试数据集上的效果。实验数据表明该方法与DeepSeek模型结合的效果并不太理想。<p>
<p>基于实验结果分析，实现了一个代码编写助手LC-Assistant，对模型进一步进行了局部优化，可将准确率从84.5%提升到91.3%。为了进一步验证改进后的方法和工具，从LeetCode平台选择9道编程题，直接使用DeepSeek模型可正确解出5道题，使用LC-Assistan可正确解出8道题。<p>

## 2.实验对比：
<p>在HumanEval coding benchmark上进行测试。从以下方面进行了测试对比：<p>
<p>1）Reflexion+DeepSeek与DeepSeek的实验对比。<p>
<p>对比分析上述两个程序的运行结果，发现加入Reflexion后，模型的解题能力反而下降了。<p>
<p>进一步分析日志，我们发现论文Reflexion工作流程在接入不同处理能力的LLM场景下可能存在的缺陷。由于DeepSeek和大多数LLM模型一样，有可能会出现幻觉，导致在调用LLM生成测试用例时，有可能生成错误的测试用例。基于错误测试用例进行的自我反思自然会损害而不是提升LLM的代码编写效果。<p>
<p>一分析HumanEval数据集中136条测试数据的Reflexion结果，有25条测试数据返回结果为失败。这25条测试数据中，有14条是因为DeepSeek返回了错误的测试 case。<p>

2）对Reflexion进行局部优化后的实验对比。
<p>对Reflecxion框架进行了如下改进:在生成单元测试用例时，我们直接使用HumanEval数据集中提供的测试示例，而不是调用LLM去生成单元测试用例。<p>
<p>使用改进的框架重新运行上述25条返回结果为失败的测试数据，结果如下:<p>
<p>50%(7/14)由不正确的单元测试用例引起的错误，通过改进的方法可以得到正确答案；<p>
<p>36.4%(4/11)单元测试用例正确但最终代码生成结果错误的测试数据，通过改进的方法也可以得到正确答案。<p>
<p>调整后方案在HumanEval Pass@1通过率可达91.3%((136+7+4)/161)。<p>

## 3.工程：
<p>基于上述“Reflexion框架+DeepSeek API”的技术方案，实现一个“LeetCode解题助手”，使用最新的LeetCode题目进行评测。实现了简单的文字交互界面，命令行调用。<p>

```bash
#programming_runs/ lc_assistant.py
ALL_COMMANDS_LST = [
'l <file> - load function-sig in <file>', 
'l <number> - load the <number>-th test case in human-eval dataset, count from 0', 
't - add unit test', 
'r - run reflexion loop', 
'c - clear function-sig and test cases', 
'e - evaluate human-eval case', 
'h - give me some hint']
```

<p>目前能比较好的解决leetcode的“简单”级别问题。<p>
<p>现在的技术框架是Reflexion+DeepSeek API，作为对比，对于LeetCode简单问题，单纯调用DeepSeek API的成功率大概5/9，加入Reflexion后能达到8/9<p>

## 4.相关资源：
<p><strong>Paper：</strong>Reflexion: Language Agents with Verbal Reinforcement Learning 

( [NeurIPS 2023] ，https://arxiv.org/abs/2303.11366) <p>
<p><strong>Reflexion：</strong>https://github.com/noahshinn/reflexion <p>
<p><strong>DeepSeek API：</strong>https://platform.deepseek.com/api-docs/zh-cn/<p>

## 5.To Setup & Run

（1）Clone this repo and move to the programming_runs directory:
```bash
git clone https://github.com/CRay2005/Reflexion-DeepSeek && cd ./programming_runs
```

（2）Install the module dependencies into your environment:
```bash
conda create -n your_env_name python=X.X
pip install -r requirements.txt
```

（3）Set `DEEPSEEK_API_KEY` environment variable to your DeepSeek API key:

<p>在DeepSeek申请一个api-key<p>
<p>https://platform.deepseek.com/api-docs/zh-cn/<p>

```bash
export DEEPSEEK_API_KEY=<your key>
```

```bash
#programming_runs/model.py
API_KEY = os.getenv("DEEPSEEK_API_KEY")
DeepSeekClient = OpenAI(api_key=API_KEY,base_url='https://api.deepseek.com/v1')
```


## 6.其它
<p>关于openai库安装的说明<p>
<p>官网的介绍是pip install openai。不过它没说Python版本最好<=3.8。若Python版本过高，到达了3.11，会出现以下报错：<p>
<p>ImportError: cannot import name 'OpenAI' from 'openai'<p>
<p>因此请直接使用Python==3.8。<p>
<p><strong>更新（2024/07/16）</strong><p>
<p>现在openai更新了，python高版本也可支持：<p>

```bash
pip install openai --upgrade
```


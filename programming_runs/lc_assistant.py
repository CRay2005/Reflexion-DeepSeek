from utils import enumerate_resume, make_printv, write_jsonl, resume_success_count, read_jsonl
from executors import executor_factory
from generators import generator_factory, model_factory
from generators.py_generate import py_is_syntax_valid

from typing import List
from sys import stdin, stdout, stderr

# zhangqi
DEFAULT_TEMP = 1.0

def flushout(s, color='w'):
    if color=='r':
        s = f'\033[91m{s}\033[0m'
    elif color=='g':
        s = f'\033[92m{s}\033[0m'
    stdout.write(s)
    stdout.flush()

def flusherr(s):
    flushout(s, color='r')

def generate_utests_from_funcsig(fsig:str) -> List[str]:
    '''
    generate unit-tests from function signature
    '''
    res = []
    flag = 0
    testcase = ''
    for line in fsig.split('\n'):
        line = line.strip()
        if flag==0 and line.startswith('>>>'):
            flag = 1
            testcase += 'assert ' + line.strip('> ')
        elif flag==1:
            testcase += ' == ' + line
            flag = 0
            if not py_is_syntax_valid(testcase):
                flusherr(f'Invalid test case! {testcase}')
            else:
                res.append(testcase)
            testcase = ''

    return res

def add_hint_to_prompt(prompt, hint, hinted=True):
    lst = prompt.split('\n')
    hints = [f'    {hint}'] if hinted else ['', '    Hints:', f'    {hint}']
    for i in range(len(lst)-1, -1, -1):
        line = lst[i].strip()
        if len(line)>0:
            return '\n'.join(lst[:i] + hints + lst[i:])



ALL_COMMANDS_LST = ['l <file> - load function-sig in <file>', 
        'l <number> - load the <number>-th test case in human-eval dataset, count from 0', 
        't - add unit test', 
        'r - run reflexion loop', 
        'c - clear function-sig and test cases', 
        'e - evaluate human-eval case', 
        'h - give me some hint']
ALL_COMMANDS = '\n'.join(ALL_COMMANDS_LST)
VALID_COMMAND_SET = set([cmd.strip().split(' ')[0] for cmd in ALL_COMMANDS_LST])
print (f'VALID_COMMAND_SET = {VALID_COMMAND_SET}')  # TEST

HUMANEVAL_DATASET = read_jsonl('./benchmarks/humaneval-py.jsonl')
print (f'HUMANEVAL_DATASET loaded, {len(HUMANEVAL_DATASET)} cases') 

def cli_chat(
    model_name: str,
    language: str,
    max_iters: int = 3,
    verbose: bool = False,
):
    exe = executor_factory(language, is_leet=False)
    gen = generator_factory(language)
    model = model_factory(model_name)

    print_v = make_printv(verbose)

    prompt = ''
    utests = []
    item = None
    cur_func_impl = ''
    hinted = False

    flushout(f'-------- LeetCode Assistant --------\n{ALL_COMMANDS}\n')
    while True:
        flushout('>>> ')
        line = stdin.readline().strip()
        if len(line)==0:
            flushout('\n')
            continue
        
        cmd_fields = [f for f in line.split(' ') if len(f)>0]
        #print_v(f'command = {cmd_fields}')
        cmd = cmd_fields[0]
        if cmd not in VALID_COMMAND_SET:
            flusherr(f'Invalid commmand! \n')
            continue

        if cmd=='l':
            if len(cmd_fields)<2:
                flusherr('Please indicate <file> or <number> to load!!\n')
                continue

            para = cmd_fields[1]
            num, fname = -1, ''
            try:
                num = int(para)
            except Exception:
                fname = para
            
            prompt = ''
            if len(fname)==0:
                # load <number>
                if num>=len(HUMANEVAL_DATASET) or num<0:
                    flusherr(f'Error: invalid <number>! {num}\n')

                item = HUMANEVAL_DATASET[num]
                prompt = item['prompt']

            else:
                # load <file>
                try:
                    with open(fname) as fin:
                        prompt = ''.join(fin.readlines())
                except Exception:
                    flusherr(f'Error: cannot open file! {ffname}\n')

            if len(prompt)==0:
                continue

            utests = generate_utests_from_funcsig(prompt)
            flushout(f'Function signature loaded: \n--------\n{prompt}')
            flushout(f'Test cases: \n--------\n{utests}\n')
            continue

        if cmd=='c':
            prompt, utests, item, cur_func_impl= '', [], None, ''
            hinted = False
            continue

        if cmd=='h':
            if len(prompt)==0:
                flusherr('Please load function-sig first!\n')
                continue

            flushout('Input hint here:\n')
            flushout('>>> ')
            hint = stdin.readline().strip()
            if len(hint)==0:
                continue

            prompt = add_hint_to_prompt(prompt, hint, hinted)
            hinted = True
            flushout(f'Function signature updated: \n--------\n{prompt}\n')
            continue

        if cmd=='t':
            if len(prompt)==0:
                flusherr('Please load function-sig first!\n')
                continue
            flushout('Input unit test here, with following format:\nassert function_name(arg1, arg2, ...) == target_value\n')
            flushout('>>> ')
            utest = stdin.readline().strip()
            if not py_is_syntax_valid(utest):
                flusherr(f'Invalid test case! ')
                continue
            if len(utest)>0 and utest not in utests:
                utests.append(utest)
            print_v(f'unit tests={utests}')
            continue

        if cmd=='e':
            if len(cur_func_impl)==0:
                flusherr('Please generate an implentation first!\n')
                continue
            if item is None:
                flusherr('Not a test case in human-eval dataset, please evaluate it manually!\n')
                continue
            is_passing = exe.evaluate(item['entry_point'], cur_func_impl, item['test'], timeout=10)
            if is_passing:
                flushout('Passed!\n', color='g')
            else:
                flushout('Failed!\n', color='r')
            continue

        if cmd=='r':
            if len(prompt)==0 or len(utests)==0:
                flusherr('Please load function-sig and test cases first!\n')
                continue
            # first attempt
            cur_func_impl = gen.func_impl(prompt, model, "simple", temperature=DEFAULT_TEMP)
            assert isinstance(cur_func_impl, str)
            is_passing, feedback, _ = exe.execute(cur_func_impl, utests)
            print_v(feedback)

            # if solved, exit early
            if is_passing:
                flushout(f'---- Generated Code ---- iter[1]\n{cur_func_impl}\n\n')
                continue

            # use self-reflection to iteratively improve
            cur_iter = 1
            cur_feedback = feedback
            while cur_iter < max_iters:
                # get self-reflection
                reflection = gen.self_reflection(
                    cur_func_impl, cur_feedback, model)

                # apply self-reflection in the next attempt
                cur_func_impl = gen.func_impl(
                    func_sig=prompt,
                    model=model,
                    strategy="reflexion",
                    prev_func_impl=cur_func_impl,
                    feedback=cur_feedback,
                    self_reflection=reflection,
                    temperature=DEFAULT_TEMP,
                )
                assert isinstance(cur_func_impl, str)

                # check if all internal unit tests pass
                is_passing, cur_feedback, _ = exe.execute(
                    cur_func_impl, utests)

                # if solved, check if it passes the real tests, exit early
                if is_passing or cur_iter == max_iters - 1:
                    flushout(f'---- Generated Code ---- iter[{cur_iter+1}]\n{cur_func_impl}\n\n')
                    break

                cur_iter += 1
            continue



if __name__=='__main__':
    cli_chat('deepseek', 'py', max_iters=5, verbose=True)



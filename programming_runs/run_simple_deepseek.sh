python main.py \
  --run_name "simple_deepseek_coder_k1" \
  --root_dir "root" \
  --dataset_path ./benchmarks/humaneval-py.jsonl \
  --strategy "simple" \
  --language "py" \
  --model "deepseek" \
  --pass_at_k "1" \
  --max_iters "1" \
  --verbose

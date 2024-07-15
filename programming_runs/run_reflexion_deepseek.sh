python main.py \
  --run_name "reflexion_deepseek_coder_t1_k3_sp1_mi4" \
  --root_dir "root" \
  --dataset_path ./benchmarks/humaneval-py.jsonl \
  --strategy "reflexion" \
  --language "py" \
  --model "deepseek" \
  --pass_at_k "3" \
  --max_iters "4" \
  --verbose

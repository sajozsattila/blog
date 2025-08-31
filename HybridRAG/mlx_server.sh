python -m app.main \
  --model-path mlx-community/Qwen3-8B-6bit \
  --model-type lm \
  --context-length 8192 \
  --max-concurrency 1 \
  --queue-timeout 300 \
  --queue-size 100
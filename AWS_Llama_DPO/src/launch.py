import os
import argparse
import subprocess
from peft import AutoPeftModelForCasualLM
import torch

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # SageMaker specific arguments
    parser.add_argument("--hugingface_token", type=str, defaul=None)
    parser.add_argument("--aws_region", type=str, defaul=None)
    parser.add_argument("--model-dir", type=str, defaul=os.environ["SM_MODEL_DIR"])
    parser.add_argument("--dataset_path", type=str, defaul="lvwerra/stack-exchange-paired")
    parser.add_argument("--model_name", type=str, defaul="meta-llama/Llama-3.2-3B-Instruct")

    args = parser.parse_args()

    # set HuggingFace Token
    os.environ["HF_TOKEN"] = args.hugingface_token

    # set AWS region
    os.environ["AWS_DEFAULT_REGION"] = args.aws_region

    # donwload original model
    training_command = [
        "accelerate", "launch", "sft_llama.py",
        "--output_dir", "./sft",
        "--max_steps", "500",
        "--logging_steps", "10",
        "--save_steps", "10",
        "--per_device_train_batch_size", "4",
        "--per_device_eval_batch_size", "1",
        "--gradient_accumulation_steps", "2",
        "--gradient_checkpointing", "False",
        "--group_by_length", "False",
        "--learning_rate", "1e-4",
        "--lr_scheduler_type", "cosine"",
        "--warmup_steps", "100",
        "--weight_decay", "0.05",
        "--optim", "paged_adamw_32bit"",
        "--bf16", "False",                   # AWS EC2 g5 instance do not support bf16
        "--fp16", "True",                    # AWS EC2 g5 instance support fp16
        "--remove_unused_columns", "False",
        "--run_name", "sft_llama2",
        "--report_to", "none",               # disable WanDB
        "--dataset_name", args.dataset_path, # s3 location of the training data
        "--model_name", args.model_name
    ]
    subprocess.call(training_command)

    # DPO training
    dpo_command = [
        "accelerate", "launch", "dpo_llama.py",
        "--model_name_or_path", "sft/final_checkpoint",
        "--output_dir", "dpo",
        "--num_proc", "48",
        "--report_to", "none",                    # disable WanDB
        "--dataset_name", args.dataset_path,      # s3 location of the training data
        "--model_name", args.model_name
    ]
    subprocess.call(dpo_command)

    # merge
    merge_command = [
        "python", "merge_peft_adapter.py",
        "--base_model_name", args.model_name,
        "--adapter_model_name", "dpo/final_checkpoint/",
        "--output_name", "llama-2-dpo"
    ]
    subprocess.call(merge_command)


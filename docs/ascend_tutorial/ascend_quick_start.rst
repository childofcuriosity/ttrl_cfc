verl x Ascend
===================================

Last updated: 06/17/2025.

verl includes support for Huawei Ascend devices.

Supported hardware
-----------------------------------

Atlas 200T A2 Box16

Atlas 900 A2 PODc


Installation
-----------------------------------

Base environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+-----------+-------------+
| software  | version     |
+-----------+-------------+
| Python    | == 3.10     |
+-----------+-------------+
| CANN      | == 8.1.RC1  |
+-----------+-------------+
| torch     | == 2.5.1    |
+-----------+-------------+
| torch_npu | == 2.5.1.RC1|
+-----------+-------------+


vllm & vllm-ascend
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Build and install vllm and vllm-ascend using the commands below. Choose the installation command for your hardware.

.. code-block:: bash
    
    # vllm
    git clone -b v0.7.3 --depth 1 https://github.com/vllm-project/vllm.git
    cd vllm
    pip install -r requirements-build.txt

    # for Atlas 200T A2 Box16
    VLLM_TARGET_DEVICE=empty pip install -e . --extra-index https://download.pytorch.org/whl/cpu/
    
    # for Atlas 900 A2 PODc
    VLLM_TARGET_DEVICE=empty pip install -e .

.. code-block:: bash
    
    # vllm-ascend
    git clone -b v0.7.3.post1 --depth 1 https://github.com/vllm-project/vllm-ascend.git
    cd vllm-ascend
    export COMPILE_CUSTOM_KERNELS=1
    python setup.py install

Install verl
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    git clone https://github.com/volcengine/verl.git
    cd verl
    pip install -r requirements-npu.txt
    pip install -e .

Other dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+--------------+---------------+
| software     | description   |
+--------------+---------------+
| transformers | v4.52.4       |
+--------------+---------------+
| flash_attn   | not supported |
+--------------+---------------+
| liger-kernel | not supported |
+--------------+---------------+
| tensordict   | 0.8.3 (ARM)   |
+--------------+---------------+

1. Enabling --flash_attention_2 through transformers requires transformers >= 4.52.0.
2. Enabling FlashAttention through flash_attn is not supported.
3. liger-kernel is not supported.
4. ARM servers require tensordict 0.8.3. Install it manually after the other dependencies if needed.
5. x86 servers require the CPU version of torchvision.

.. code-block:: bash

    pip install torchvision==0.20.1+cpu --index-url https://download.pytorch.org/whl/cpu


Quick start
-----------------------------------
Before using the environment for other runs, train Qwen2.5-0.5B with GRPO to check the installation.

1. Download the dataset and preprocess it into Parquet, including the fields needed to compute RL rewards.

.. code-block:: bash

    python3 examples/data_preprocess/gsm8k.py --local_dir ~/data/gsm8k

2. Run training.

.. code-block:: bash

    set -x

    export VLLM_ATTENTION_BACKEND=XFORMERS

    python3 -m verl.trainer.main_ppo \
        algorithm.adv_estimator=grpo \
        data.train_files=$HOME/data/gsm8k/train.parquet \
        data.val_files=$HOME/data/gsm8k/test.parquet \
        data.train_batch_size=128 \
        data.max_prompt_length=512 \
        data.max_response_length=128 \
        data.filter_overlong_prompts=True \
        data.truncation='error' \
        actor_rollout_ref.model.path=Qwen/Qwen2.5-0.5B-Instruct \
        actor_rollout_ref.actor.optim.lr=5e-7 \
        actor_rollout_ref.model.use_remove_padding=False \
        actor_rollout_ref.actor.entropy_coeff=0.001 \
        actor_rollout_ref.actor.ppo_mini_batch_size=64 \
        actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=20 \
        actor_rollout_ref.actor.use_kl_loss=True \
        actor_rollout_ref.actor.kl_loss_coef=0.001 \
        actor_rollout_ref.actor.kl_loss_type=low_var_kl \
        actor_rollout_ref.model.enable_gradient_checkpointing=True \
        actor_rollout_ref.actor.fsdp_config.param_offload=False \
        actor_rollout_ref.actor.fsdp_config.optimizer_offload=False \
        actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=40 \
        actor_rollout_ref.rollout.enable_chunked_prefill=False \
        actor_rollout_ref.rollout.tensor_model_parallel_size=2 \
        actor_rollout_ref.rollout.name=vllm \
        actor_rollout_ref.rollout.gpu_memory_utilization=0.6 \
        actor_rollout_ref.rollout.n=5 \
        actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=40 \
        actor_rollout_ref.ref.fsdp_config.param_offload=True \
        algorithm.kl_ctrl.kl_coef=0.001 \
        trainer.critic_warmup=0 \
        trainer.logger=['console'] \
        trainer.project_name='verl_grpo_example_gsm8k' \
        trainer.experiment_name='qwen2_7b_function_rm' \
        trainer.n_gpus_per_node=8 \
        trainer.nnodes=1 \
        trainer.save_freq=-1 \
        trainer.test_freq=5 \
        trainer.total_epochs=1 \
        trainer.device=npu $@


Current support
-----------------------------------

+-----------+-------------------------+-------------+-------------------+----------------------+
| algorithm |         model           | rewards mae |  throughput ratio |        hardware      |
+-----------+-------------------------+-------------+-------------------+----------------------+
|   GRPO    | Qwen2.5-7B-instruct     |    0.38%    |        0.588      |  Atlas 200T A2 Box16 |
+-----------+-------------------------+-------------+-------------------+----------------------+
|   GRPO    | Qwen2.5-32B-instruct    |    0.30%    |        0.685      |  Atlas 200T A2 Box16 |
+-----------+-------------------------+-------------+-------------------+----------------------+
|   GRPO    | Qwen2.5-VL-3B-instruct  |    3.14%    |        0.470      |  Atlas 200T A2 Box16 |
+-----------+-------------------------+-------------+-------------------+----------------------+
|   GRPO    | Qwen2.5-VL-7B-instruct  |    3.30%    |        0.380      |  Atlas 200T A2 Box16 |
+-----------+-------------------------+-------------+-------------------+----------------------+
|   GRPO    | Qwen2.5-VL-32B-instruct |    0.79%    |        0.568      |  Atlas 200T A2 Box16 |
+-----------+-------------------------+-------------+-------------------+----------------------+
|   DAPO    | Qwen2.5-7B-instruct     |    3.83%    |        pending    |  Atlas 200T A2 Box16 |
+-----------+-------------------------+-------------+-------------------+----------------------+
|  SFT-PEFT | Qwen2.5-0.5B-instruct   |    0.06%    |        0.305      |  Atlas 900 A2 PODc   |
+-----------+-------------------------+-------------+-------------------+----------------------+

Accuracy comparison
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For SFT, the expected mean absolute error between Ascend and A100 losses under the same configuration is <= 2%. The figure below shows the calculation. See the `accuracy calculation guide <https://www.hiascend.com/document/detail/zh/Pytorch/600/ptmoddevg/trainingmigrguide/LMaccuracy_0001.html>`_ for details.

.. image:: https://github.com/eric-haibin-lin/verl-community/blob/main/docs/loss_comparison.png?raw=true
   :alt: loss_comparison

For RL algorithms such as GRPO, the expected mean absolute error between Ascend and A100 rewards under the same configuration is <= 4%, based on experience. Use the calculation shown above.


Throughput comparison
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Average "perf/throughput" over the first four logged steps for Ascend NPU and A100 separately. The throughput ratio is the NPU mean divided by the A100 mean.



Roadmap
-----------------------------------

See the `roadmap <https://github.com/volcengine/verl/discussions/900>`_ for progress on additional features.



Notice
-----------------------------------
The Ascend support code in verl is provided as reference examples. For commercial use, contact the provider through official channels.

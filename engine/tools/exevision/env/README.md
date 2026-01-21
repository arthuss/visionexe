# env

Conda environment + uv workflow for local Qwen3-VL models.

## Create env
```
conda env create -f env/conda-vl.yml
conda activate exevision-vl
```

## Install Python deps (uv)
```
uv pip install -r env/requirements-vl.txt
```

## Install PyTorch
Choose one:
- GPU (CUDA 12.1 example):
  ```
  conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
  ```
- CPU:
  ```
  conda install pytorch torchvision torchaudio cpuonly -c pytorch
  ```

## Model paths
Local models live in:
- engine/tools/exevision/Models/Qwen3-VL-Embedding-2B
- engine/tools/exevision/Models/Qwen3-VL-Reranker-2B
- engine/tools/exevision/Models/Qwen3-VL-2B-Instruct

## Worker services
After activation, start the HTTP workers via `scripts/` (see QUICKSTART.md).

wsl -d Ubuntu24Old -u root -- bash -lc 'cd ~/diffusion-pipe && source ~/miniconda3/etc/profile.d/conda.sh && conda activate diffusion-pipe && python  tools/qwen_wan_batch_app.py'

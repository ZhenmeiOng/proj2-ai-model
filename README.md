## After cloning this repo, run:

``` shell
conda create -n llama-env python=3.10
conda activate llama-env
pip install -r requirements.txt
```

- so the name of our virtual environment will be `llama-env`.
- when you set up your python environment, the dependencies in `requirement.txt` will be installed automatically.
- the packages installed in `llama-env` so far: `PyTorch`, `transformers`, `gradio`, and `accelerate`.
- but of course, you guys are free to change anything you think suitable. This is just a starter.


## Installing Llama 2 7B model:
- refer to this website: https://ai.meta.com/blog/5-steps-to-getting-started-with-llama-2/ 
- since our virtual environment already has `transformers`, `gradio`, and `accelerate` installed, we can start from step 2.
- Note: `gradio` is library for building a web interface to interact with Llama 2, but we can use other platform.
- After applying for access to Meta and having accepted their License, they will bring you to a website where they show you to run the commands below:
  1. `pip install llama-stack`
  2. `llama model list --show-all` (use this since we are installing Llama 2, an older version)
  3. `llama model download --source meta --model-id Llama-2-7b`
  4. You will be asked to paste a unique URL you received in your email.
     
- now clone the model:
```shell
git clone https://github.com/facebookresearch/llama
```
- install `wget` and `md5sum` if not installed already:
```shell
# check if it's installed:
wget --version
md5sum --version
# install using HomeBrew
brew install wget
```
- Note: On macOS, md5sum may not be installed by default, but macOS has a similar command called md5. You can use md5 directly instead of md5sum.
-  then run `sh download.sh`
- paste URL from email (don't press Enter without pasting the URL)
- choose the model variants: `7B,7B-chat`
<br />
I tried to run a simple python script but ran into many errors. but you guys can try to figure it out, or if you have a better solution, please let us know!

## Running Frontend:
```shell
cd frontend
```
```shell
npm install
```
```shell
npm run dev
```
- then copy the link `http://localhost:5173/`
- 

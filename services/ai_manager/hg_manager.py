from typing import Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, BitsAndBytesConfig
from trl import SFTTrainer
from datasets import load_dataset
from peft import LoraConfig, PeftModel

import json
import os
import threading
from datetime import datetime



LLM_DATA_FOLDER = os.path.join(os.path.dirname(__file__), 'llm_data')
DATASETS_FOLDER = os.path.join(LLM_DATA_FOLDER, 'datasets')
LOGS_FOLDER = os.path.join(LLM_DATA_FOLDER, 'logs')
CHECKPOINTS_FOLDER = os.path.join(LLM_DATA_FOLDER, 'checkpoints')
ADAPTERS_FOLDER = os.path.join(LLM_DATA_FOLDER, 'adapters')


def printSimLog(*logs):
    print( f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]  ', *logs )

def getDatasetList(datasetsDir: str=None) -> dict[str, str]:
    if datasetsDir is None: datasetsDir = DATASETS_FOLDER
    datasets = next(os.walk(DATASETS_FOLDER))[2] # getting files names

    return {
        os.path.splitext(filename)[0]: os.path.join(datasetsDir, filename) \
        for filename in datasets
    }


def trainModel( modelName: str,
                datasetName: str, datasetsDir: Optional[str]=None,
                reportTo: Optional[str]="tensorboard",
                fromCheckpoint: Optional[str]=None,
                bf16Mode: bool=False, fp16Mode: bool=True,
                HUGGINGFACE_TOKEN: str|bool=True, threads: int=6) -> None:
    torch.set_num_threads(threads)
    torch.set_num_interop_threads(2)

    printSimLog('Loading configs...')
    # CONFIGS
    datasetsList = getDatasetList(datasetsDir)
    datasetPath = datasetsList.get(datasetName)
    if not datasetPath: raise Exception(f'Dataset {datasetName} not found!')

    resumeFromCheckpoint = fromCheckpoint is not None
    checkpointsName = modelName.lower() + '___' + datasetName.lower() if not resumeFromCheckpoint \
                        else resumeFromCheckpoint
    fullCheckpointPath = os.path.join(CHECKPOINTS_FOLDER, checkpointsName)

    fullLogsPath = os.path.join(LOGS_FOLDER, checkpointsName)
    fullAdapterPath = os.path.join(ADAPTERS_FOLDER, checkpointsName)

    printSimLog(f'Logs: {fullLogsPath}')
    printSimLog(f'Adapter: {fullAdapterPath}')
    printSimLog(f'Checkpoints: {fullCheckpointPath}')

    printSimLog(f'Loading model {modelName}...')
    # model_name = "meta-llama/Meta-Llama-3-8B-Instruct"
    model = AutoModelForCausalLM.from_pretrained(
        modelName,
        device_map="cpu",
        token = HUGGINGFACE_TOKEN,
        cache_dir = None,
        # quantization_config=BitsAndBytesConfig(
        #     load_in_4bit = True,
        #     bnb_4bit_use_double_quant = True,
        #     bnb_4bit_quant_type = 'nf4',
        #     bnb_4bit_compute_dtype = torch.float16
        # ),
        # dtype=torch.float16,
        trust_remote_code=False,
        use_safetensors=True
    )

    model.gradient_checkpointing_enable()

    # YOU NEED TO SET TOKEN AS A ENV VARIABLE VIA " export HF_HUB_TOKEN="TOKEN" "
    tokenizer = AutoTokenizer.from_pretrained(modelName)

    printSimLog(f'Loading dataset {datasetName}...')

    def datasetFormatting(example: dict[str, str]):
        return json.dumps({
            "prompt": [{"role": "user", "content": example["instruction"]}],
            "completion": [
                {
                    "role": "assistant",
                    "content": example["output"],
                }
            ],
        })

    dataset = load_dataset( os.path.dirname(datasetPath), data_files=os.path.basename(datasetPath) )

    printSimLog(f'Loading objects...')

    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=[
            'up_proj', 'down_proj', 'gate_proj',
            'k_proj', 'q_proj', 'v_proj', 'o_proj'
        ]
    )

    training_args = TrainingArguments(
        output_dir=fullLogsPath,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=16,
        dataloader_num_workers=2,
        eval_strategy="no",
        logging_steps=1,
        warmup_steps=10,
        logging_strategy="steps",
        learning_rate=2e-4,
        fp16=False,
        bf16=False,
        report_to=reportTo
    )

    # starting tensorboard
    if reportTo == "tensorboard":
        printSimLog('Starting TensorBoard in daemon mode...')

        def startTensorboard(logDir: str, port: str) -> None:
            from tensorboard import program

            tb = program.TensorBoard()
            tb.configure(argv=[None, '--logdir', logDir, '--port', port, '--load_fast', 'true'])

            url = tb.launch()
            print(f"TensorBoard has been started on {url}")

        threading.Thread(target=startTensorboard, args=(fullLogsPath, '6006'), daemon=True).start()


    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset["train"],
        peft_config=lora_config,
        formatting_func=datasetFormatting,
        processing_class=tokenizer,
        args=training_args,
    )


    printSimLog('Ready. Training model...')
    trainer.train(resume_from_checkpoint=resumeFromCheckpoint)

    printSimLog(f'Training done. Saving to {fullAdapterPath}')
    trainer.model.save_pretrained(fullAdapterPath)
    printSimLog(f'Done and saved.')



class ModelRequestsManager:
    def __init__(self, modelName: str, adapterName: Optional[str] = None, HUGGINGFACE_TOKEN: Optional[str] = None):
        self.modelName = modelName
        self.adapterName = adapterName

        self._model = AutoModelForCausalLM.from_pretrained(
            modelName,
            device_map="cpu",
            token = HUGGINGFACE_TOKEN,
            cache_dir = None
        )
        self._tokenizer = AutoTokenizer.from_pretrained(modelName)

        self._lora_model = PeftModel.from_pretrained(
            self._model, os.path.join(ADAPTERS_FOLDER, self.adapterName)
        )


    def request(self, text: str) -> dict[str, str]:
        request = json.dumps({"role": "user", "content": text})
        requestTokens = self._tokenizer(text, return_tensors='pt')


        response = self._lora_model.generate(
            **requestTokens,
            max_new_tokens = 200,
            do_sample = True,
            temperature = 1.3
        )
        responseInText = self._tokenizer.batch_decode(response, skip_special_tokens=True)

        print(responseInText)
from transformers import AutoModelForCausalLM, AutoTokenizer
import warnings
from transformers.utils import logging as transformers_logging
import torch
from Util import to_openai_messages
from ChatResponse import ChatResponse
from langchain_core.prompt_values import ChatPromptValue

MODEL_NAME = "Qwen/Qwen2.5-Coder-3B-Instruct"

class ChatQwen:
    
  def __init__(self):
    # Suppress warnings
    warnings.filterwarnings("ignore")
    transformers_logging.set_verbosity_error()

    self.model = AutoModelForCausalLM.from_pretrained(
      MODEL_NAME,
      torch_dtype="auto",
      device_map="auto",
      low_cpu_mem_usage=True,
      # Suppress specific warning sources
      offload_folder="offload",
      offload_state_dict=True
    )
    self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)


  def invoke(self, prompt: ChatPromptValue) -> ChatResponse:
    messages = to_openai_messages(prompt)
    text = self.tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

    generated_ids = self.model.generate(
        **model_inputs,
        max_new_tokens=512
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
  
    # Print GPU memory usage after model generation
    if torch.cuda.is_available():
      print(f"GPU memory after generation: {torch.cuda.memory_allocated(0) / 1024**2:.2f} MB")
      print(f"Max GPU memory used: {torch.cuda.max_memory_allocated(0) / 1024**2:.2f} MB")
  
    return ChatResponse(content=response)



# def invoke_qwen_model() -> str:

#   prompt = "write a quick sort algorithm."
#   messages = [
#       {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
#       {"role": "user", "content": prompt}
#   ]



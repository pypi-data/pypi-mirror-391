import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')


class SimpleModelExecutor:
    """
    A minimal, naive ModelExecutor that loads a standard Hugging Face
    model and runs a forward pass.
    
    It does NOT use a KV cache.
    """

    def __init__(self, model_id: str):
        """
        Initializes and loads the model and tokenizer.
        
        Args:
            model_id (str): The model identifier from Hugging Face 
                            (e.g., "meta-llama/Llama-3.1-8B-Instruct")
        """
        logger.info(f"Loading model '{model_id}'... This may take a moment.")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Load the model and tokenizer
        self.model, self.tokenizer = self.load_model_and_tokenizer(model_id)
        logger.info(f"Model loaded successfully on {self.device}.")

    def load_model_and_tokenizer(self, model_id: str):
        """
        Loads the model and tokenizer from Hugging Face.
        This is the "minimum" way to load.
        """
        tokenizer = AutoTokenizer.from_pretrained(model_id)

        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            dtype=torch.float16,  # Use float16 to save memory
            device_map=self.device  # Automatically load to GPU
        )

        # Set to evaluation mode (disables dropout, etc.)
        model.eval()

        return model, tokenizer
    
    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        """
        Runs a single, simple forward pass.
        
        Args:
            input_ids (torch.Tensor): A tensor of token IDs.
            
        Returns:
            torch.Tensor: The logits (raw predictions) from the model.
        """
        # We wrap this in torch.no_grad() to tell PyTorch
        # not to calculate gradients, which saves memory and is faster.
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids)
            # The model's output is a complex object.
            # We just want the logits.
            return outputs.logits
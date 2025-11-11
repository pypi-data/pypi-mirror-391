from .executor.model_executor import SimpleModelExecutor
import torch
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')


def generate_text_naively(
    executor: SimpleModelExecutor, 
    prompt: str, 
    max_new_tokens: int = 50
):
    """
    Generates text autoregressively WITHOUT a KV cache.
    This is the "naive" implementation.
    """
    tokenizer = executor.tokenizer
    device = executor.device

    logger.info(f"\nPrompt: '{prompt}'")

    # 1. Format the prompt using the model's chat template.
    # This is the correct way to use an instruction-tuned model.
    # It adds special tokens (e.g., <|im_start|>) to structure the conversation.
    messages = [
        {"role": "user", "content": prompt}
    ]
    input_ids = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True, # This adds the tokens to signal the assistant's turn
        return_tensors="pt"
    ).to(device)

    generated_token_ids = []

    # 2. The autoregressive loop
    for _ in range(max_new_tokens):
        # ------------------------------------------------------------------
        # This is the core "naive" part:
        # In every loop, we pass the *entire* history of tokens
        # (original prompt + generated tokens) back into the model.
        # ------------------------------------------------------------------
        current_ids_to_process = input_ids

        # 3. Run the forward pass using our executor
        # 'logits' will have shape [batch_size, sequence_length, vocab_size]
        logits = executor.forward(current_ids_to_process)

        # 4. Get the logits for the *very last* token
        # This tells us the model's prediction for the *next* token
        # Shape: [batch_size, vocab_size]
        # Example: next_token_logits: tensor([[-68.4375, -69.0625, -73.3125,  ..., -77.0000, -77.1250, -70.0625]], dtype=torch.float16)
        next_token_logits = logits[:, -1, :]
        logger.debug(f"next_token_logits: {next_token_logits}")

        # 5. Get the most likely token (this is "greedy sampling")
        # Shape: [batch_size]
        # Example: tensor([1757])
        next_token_id = torch.argmax(next_token_logits, dim=-1)
        logger.debug(f"next_token_id: {next_token_id}")

        # 6. Check for the End-of-Sequence token
        if next_token_id == tokenizer.eos_token_id:
            logger.info("\n[End of sequence reached]")
            break

        # 7. Add the new token to our full sequence
        # This is the "autoregressive" part: the new token is now
        # part of the input for the next loop.
        # input_ids example: tensor([[15496,    11,   616,  1438,   318,  1757]])
        input_ids = torch.cat([input_ids, next_token_id.unsqueeze(0)], dim=-1)
        logger.debug(f"input_ids: {input_ids}")
        
        # Also store it for decoding later
        generated_token_ids.append(next_token_id.item())

        # (Optional) Print the new token as it's generated
        print(tokenizer.decode(next_token_id), end="", flush=True)

    # 8. Decode the final generated text
    final_text = tokenizer.decode(generated_token_ids)
    return final_text

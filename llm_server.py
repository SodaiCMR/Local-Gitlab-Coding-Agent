from fastapi import FastAPI
import ollama
import sys
from functions.get_files_info import get_files_info

app = FastAPI()
@app.post("/generate")
def generate():
    messages = []
    verbose_flag = False
    if len(sys.argv) < 2:
        print("Prompt missing !")
        sys.exit(1)
    if len(sys.argv) == 3 and sys.argv[2] == "--verbose":
        verbose_flag = True
    msg = {"role":"user", "content":sys.argv[1]}
    messages.append(msg)
    response = ollama.chat(model="mistral", messages=messages)
    print(response['message']['content'])

    if verbose_flag:
        print("\n")
        print(f"User prompt: {msg['content']}")
        print(f"Prompt tokens: {response['prompt_eval_count']}")
        print(f"Response tokens: {response['eval_count']}")

if __name__ == "__main__":
    # generate()
    print(get_files_info("calculator","pkg"))
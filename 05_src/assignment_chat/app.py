"""
Gradio chat interface for the cancer research chatbot
"""

"""
Gradio chat interface for the cancer research chatbot
"""

import os
import gradio as gr
from dotenv import load_dotenv

from agent import run_agent
from guardrails import check_guardrails

load_dotenv()

WELCOME_MESSAGE = (
    "Welcome to the Cancer Research Assistant!\n\n"
    "You can ask me any information about the latest updates in cancer research! \n"
)


def chat(user_message, history):
    user_message = user_message.strip()

    if not user_message:
        return "", history

    # check guardrails before calling the agent
    blocked, refusal = check_guardrails(user_message)
    if blocked:
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": refusal})
        return "", history

    # call the agent, passing history for memory
    # convert gradio history dicts to (human, assistant) tuples for agent
    history_tuples = []
    for i in range(0, len(history) - 1, 2):
        human = history[i]["content"] if i < len(history) else None
        asst  = history[i+1]["content"] if i+1 < len(history) else None
        history_tuples.append((human, asst))

    try:
        reply = run_agent(user_message, history_tuples)
    except Exception as e:
        reply = f"Sorry, something went wrong: {e}"

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})
    return "", history


with gr.Blocks(title="CancerChat", theme=gr.themes.Default()) as demo:

    gr.Markdown("# Cancerchat\n### Cancer Research Assistant")

    # history stored as list of {"role": ..., "content": ...} dicts
    chatbot = gr.Chatbot(
        value=[{"role": "assistant", "content": WELCOME_MESSAGE}],
        elem_id="chatbot",
        type="messages",
        height=500,
        show_label=False,
        render_markdown=True,
    )

    with gr.Row():
        txt = gr.Textbox(
            placeholder="e.g. Find papers on liquid biopsy",
            show_label=False,
            scale=9,
        )
        send_btn = gr.Button("Send", variant="primary", scale=1)

    gr.Examples(
        examples=[
            "Find papers on liquid biopsy",
            "Fetch abstract for PMID 36807484",
        ],
        inputs=txt,
        label="Try these examples",
    )

    clear_btn = gr.Button("Clear conversation", size="sm")

    txt.submit(chat, [txt, chatbot], [txt, chatbot])
    send_btn.click(chat, [txt, chatbot], [txt, chatbot])
    clear_btn.click(
        lambda: ([], ""),
        outputs=[chatbot, txt]
    )


if __name__ == "__main__":
    demo.launch()
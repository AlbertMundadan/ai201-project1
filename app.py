import gradio as gr

from retriever import retrieve
from generator import generate_response


def handle_query(question):
    """Run a question through the RAG pipeline and return (answer, sources).

    Retrieves the most relevant housing chunks, generates a grounded answer
    via generator.py (which already appends its own "Sources:" line), and
    builds a separate retrieval-transparency view showing which document and
    section each retrieved chunk came from.
    """
    question = (question or "").strip()
    if not question:
        return "Please enter a question.", ""

    try:
        chunks = retrieve(question)
        answer = generate_response(question, chunks)
    except Exception as e:
        return f"Something went wrong while answering: {e}", ""

    seen = []
    for c in chunks:
        label = c["title"].replace("_", " ")
        if c["section"]:
            label += f" — {c['section']}"
        if label not in seen:
            seen.append(label)
    sources = "\n".join(f"• {s}" for s in seen)

    return answer, sources


with gr.Blocks(title="UConn Housing Assistant") as demo:
    gr.Markdown(
        "# UConn Housing Assistant\n"
        "Ask about on-campus housing. Answers are grounded only in the "
        "collected UConn housing documents."
    )
    inp = gr.Textbox(label="Your question", placeholder="e.g. Are pets allowed in the dorms?")
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])


if __name__ == "__main__":
    demo.launch()

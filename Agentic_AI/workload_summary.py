from transformers import pipeline

def generate_bullet_summary(comment: str, model_name="t5-small") -> str:
    # Initialize the summarization pipeline
    summarizer = pipeline("summarization", model=model_name)

    # Define instruction-style prompt (as preamble only)
    prompt = "Summarize the following comment into concise bullet points highlighting the key information:\n\n"
    full_prompt = prompt + comment

    # Generate the summary
    summary = summarizer(full_prompt, max_length=130, min_length=30, do_sample=False)

    # Format into bullet points
    bullet_points = '• ' + ' \n• '.join(
        sentence.strip() for sentence in summary[0]['summary_text'].split('. ') if sentence.strip()
    )

    return bullet_points


# Example comment
comment = """Hi Darb, We will look into this. I think this needs to go to IT. 
Message originally posted in IT-4689 on OK I will look. This is what is happening. 
Please check this issue for more details. Message originally posted in IT-4689 on 
This is done. Message originally posted by in IT-4689 on The linked issue has been resolved. 
Please check this issue for more details."""

# Get summary
print(generate_bullet_summary(comment))

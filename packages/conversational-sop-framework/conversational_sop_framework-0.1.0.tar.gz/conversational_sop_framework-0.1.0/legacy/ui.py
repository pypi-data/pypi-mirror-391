import sys
from datetime import datetime
from main import ReturnProcessor

# Global instance to maintain state across conversations
return_processor = ReturnProcessor()

def run(message, history):
  print(history)

  # Collect all messages from the generator
  messages = list(return_processor.process_message(message, history))
  print("Messages from processor:", messages)

  # Join all messages with line breaks for display
  return "\n".join(messages)


import gradio as gr

gr.ChatInterface(
    fn=run, 
    type="messages"
).launch()
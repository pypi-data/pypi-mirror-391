# -*- coding: utf-8 -*-
import os
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

class LLM:
    """Class for calling GPT API"""
    def __init__(self, api_key: Optional[str] = None):
        # Priority: widget input key > .env > environment variable
        load_dotenv()
        effective_key = api_key or os.getenv("OPENAI_API_KEY")
        self.openai_client = OpenAI(api_key=effective_key)

    def get_response(self, prompt, data_list):
        """Get GPT response and return as-is"""
        results = []

        for data in data_list:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": str(data)},
                    ],
                    temperature=0,
                )
                results.append(response.choices[0].message.content.strip())

            except Exception as e:
                results.append(f"Error: {str(e)}")

        return results

    def get_multimodal_response(self, prompt, multimodal_data):
        """Method to process multimodal data (image+text)"""
        try:
            # Build multimodal message
            messages = [{"role": "system", "content": prompt}]
            
            # Build user message
            user_content = []
            
            for item in multimodal_data:
                if item["type"] == "image":
                    # Send image data as base64
                    user_content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{item['data']}",
                            "detail": "low"
                        }
                    })
                elif item["type"] == "text":
                    # Add text data
                    if user_content and user_content[-1].get("type") == "text":
                        # Append to existing text if already present
                        user_content[-1]["text"] += f"\n{item['data']}"
                    else:
                        # Create new text block
                        user_content.append({
                            "type": "text",
                            "text": item["data"]
                        })
            
            # Add user message
            messages.append({
                "role": "user",
                "content": user_content
            })
            
            # Multimodal request with GPT-4o model
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0,
                max_tokens=1000
            )
            
            return [response.choices[0].message.content.strip()]
            
        except Exception as e:
            return [f"Multimodal processing error: {str(e)}"]

    
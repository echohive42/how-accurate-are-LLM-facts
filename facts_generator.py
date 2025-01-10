import os
import json
import asyncio
from openai import AsyncOpenAI
from termcolor import colored
import xml.etree.ElementTree as ET
from datetime import datetime

# Constants
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
SITE_URL = "https://your-site-url.com"
SITE_NAME = "Facts Generator"
OPENROUTER_MODEL = "openai/gpt-4o-2024-11-20"
PERPLEXITY_MODEL = "llama-3.1-sonar-large-128k-online"
OUTPUT_FILE = "verified_facts.json"

async def verify_fact(client: AsyncOpenAI, fact: str) -> tuple[str, bool]:
    try:
        print(colored(f"Verifying fact: {fact[:50]}...", "cyan"))
        
        messages = [
            {
                "role": "system",
                "content": """You are a fact checker. Verify if the following fact is true.
                at the end of your response You must respond with ONLY this exact XML format:
                <result>true</result>
                or
                <result>false</result>
                No other text, explanation, or formatting is allowed."""
            },
            {
                "role": "user",
                "content": f"Verify this fact: {fact}"
            }
        ]

        response = await client.chat.completions.create(
            model=PERPLEXITY_MODEL,
            messages=messages,
        )

        xml_response = response.choices[0].message.content.strip()
        
        # Clean up the response if needed
        if not xml_response.startswith('<result>'):
            # Try to extract true/false from the response
            lower_response = xml_response.lower()
            if 'true' in lower_response:
                xml_response = '<result>true</result>'
            else:
                xml_response = '<result>false</result>'
        
        try:
            root = ET.fromstring(xml_response)
            result = root.text.lower() == 'true'
        except ET.ParseError:
            print(colored(f"Failed to parse XML response: {xml_response}", "yellow"))
            result = False
        
        print(colored(f"Verification complete for: {fact[:50]}...", "green"))
        return fact, result

    except Exception as e:
        print(colored(f"Error verifying fact: {str(e)}", "red"))
        print(colored(f"Raw response: {response.choices[0].message.content if 'response' in locals() else 'No response'}", "yellow"))
        return fact, False

async def get_facts(topic: str, num_facts: int) -> list:
    try:
        print(colored(f"Connecting to OpenRouter to get {num_facts} facts about {topic}...", "cyan"))
        
        openrouter_client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY
        )

        system_prompt = f"""Generate exactly {num_facts} interesting facts about {topic}.
        Format the response in XML like this:
        <facts>
            <fact>First fact here</fact>
            <fact>Second fact here</fact>
            ...and so on
        </facts>
        Only include the XML structure, nothing else."""

        completion = await openrouter_client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": SITE_URL,
                "X-Title": SITE_NAME,
            },
            model=OPENROUTER_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"List {num_facts} facts about {topic}"}
            ]
        )
        
        print(colored("Response received successfully!", "green"))
        
        xml_response = completion.choices[0].message.content
        print(colored("Parsing XML response...", "yellow"))
        
        root = ET.fromstring(xml_response)
        facts_list = [fact.text for fact in root.findall('fact')]
        
        # Verify facts in parallel using Perplexity
        print(colored("Verifying facts using Perplexity AI...", "cyan"))
        perplexity_client = AsyncOpenAI(
            api_key=PERPLEXITY_API_KEY,
            base_url="https://api.perplexity.ai"
        )
        
        verification_tasks = [
            verify_fact(perplexity_client, fact) 
            for fact in facts_list
        ]
        verified_facts = await asyncio.gather(*verification_tasks)
        
        return verified_facts

    except Exception as e:
        print(colored(f"Error occurred: {str(e)}", "red"))
        return []

def save_to_json(topic: str, verified_facts: list) -> None:
    try:
        # Separate facts into true and false
        true_facts = [fact for fact, verified in verified_facts if verified]
        false_facts = [fact for fact, verified in verified_facts if not verified]
        
        output_data = {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "true_facts": [
                {
                    "fact": fact,
                    "verified": True
                }
                for fact in true_facts
            ],
            "false_facts": [
                {
                    "fact": fact,
                    "verified": False
                }
                for fact in false_facts
            ],
            "statistics": {
                "total_facts": len(verified_facts),
                "true_facts_count": len(true_facts),
                "false_facts_count": len(false_facts),
                "accuracy_rate": f"{(len(true_facts) / len(verified_facts) * 100):.1f}%" if verified_facts else "0%"
            }
        }
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)
            
        print(colored(f"Results saved to {OUTPUT_FILE}", "green"))
        print(colored(f"Statistics: {output_data['statistics']}", "cyan"))
    
    except Exception as e:
        print(colored(f"Error saving results: {str(e)}", "red"))

async def main():
    try:
        topic = input(colored("Enter a topic to get facts about: ", "cyan"))
        num_facts = int(input(colored("How many facts would you like? ", "cyan")))
        
        verified_facts = await get_facts(topic, num_facts)
        
        if verified_facts:
            print(colored("\nHere are your verified facts:", "green"))
            for i, (fact, is_verified) in enumerate(verified_facts, 1):
                verification_status = "✓" if is_verified else "✗"
                color = "green" if is_verified else "red"
                print(colored(f"{i}. [{verification_status}] {fact}", color))
            
            save_to_json(topic, verified_facts)
        else:
            print(colored("No facts were generated. Please try again.", "red"))
            
    except ValueError as e:
        print(colored("Please enter a valid number for the number of facts.", "red"))
    except Exception as e:
        print(colored(f"An unexpected error occurred: {str(e)}", "red"))

if __name__ == "__main__":
    asyncio.run(main()) 
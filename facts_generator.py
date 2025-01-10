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
OPENROUTER_MODEL = "openai/gpt-4o-2024-11-20"
PERPLEXITY_MODEL = "llama-3.1-sonar-large-128k-online"
OUTPUT_FILE = "verified_facts.json"

async def verify_fact(client: AsyncOpenAI, fact: str, max_retries: int = 3) -> tuple[str, bool]:
    retries = 0
    while retries < max_retries:
        try:
            print(colored(f"Verifying fact: {fact[:50]}... (Attempt {retries + 1}/{max_retries})", "cyan"))
            
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
                print(colored(f"Verification complete for: {fact[:50]}...", "green"))
                return fact, result
            except ET.ParseError:
                print(colored(f"Failed to parse XML response (Attempt {retries + 1}): {xml_response}", "yellow"))
                if retries < max_retries - 1:
                    print(colored(f"Retrying verification...", "yellow"))
                    retries += 1
                    await asyncio.sleep(1)
                    continue
                else:
                    print(colored(f"Max retries reached. Marking fact as unverified.", "red"))
                    return fact, False

        except Exception as e:
            error_message = str(e)
            print(colored(f"Error verifying fact (Attempt {retries + 1}): {error_message}", "red"))
            print(colored(f"Raw response: {response.choices[0].message.content if 'response' in locals() else 'No response'}", "yellow"))
            
            # Check for rate limit error
            if "429" in error_message or "rate limit" in error_message.lower():
                print(colored("Rate limit reached. Waiting 60 seconds before retry...", "yellow"))
                await asyncio.sleep(60)
                if retries < max_retries - 1:
                    retries += 1
                    continue
            elif retries < max_retries - 1:
                print(colored(f"Retrying verification...", "yellow"))
                retries += 1
                await asyncio.sleep(1)
                continue
            return fact, False
    
    return fact, False

async def get_facts_with_retry(client: AsyncOpenAI, topic: str, num_facts: int, max_retries: int = 3) -> list:
    retries = 0
    while retries < max_retries:
        try:
            print(colored(f"Generating facts (Attempt {retries + 1}/{max_retries})...", "cyan"))
            
            system_prompt = f"""Generate exactly {num_facts} interesting facts about {topic}.
            Format each fact on a new line with a simple XML tag like this:
            <fact>First interesting fact here</fact>
            <fact>Second interesting fact here</fact>
            <fact>Third interesting fact here</fact>
            Only include the facts with tags, one per line, nothing else."""

            completion = await client.chat.completions.create(
                model=OPENROUTER_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"List {num_facts} facts about {topic}"}
                ]
            )
            
            xml_response = completion.choices[0].message.content.strip()
            print(colored("Parsing response...", "yellow"))
            
            try:
                # Wrap the response in a root element for parsing
                wrapped_xml = f"<facts>{xml_response}</facts>"
                root = ET.fromstring(wrapped_xml)
                facts_list = [fact.text for fact in root.findall('fact')]
                
                print(colored("Facts generated successfully!", "green"))
                return facts_list

            except ET.ParseError:
                print(colored(f"Failed to parse facts (Attempt {retries + 1}): {xml_response}", "yellow"))
                if retries < max_retries - 1:
                    retries += 1
                    await asyncio.sleep(1)
                    continue
                else:
                    print(colored("Max retries reached for fact generation.", "red"))
                    return []

        except Exception as e:
            print(colored(f"Error generating facts (Attempt {retries + 1}): {str(e)}", "red"))
            if retries < max_retries - 1:
                retries += 1
                await asyncio.sleep(1)
                continue
            return []
    
    return []

async def verify_facts_batch(client: AsyncOpenAI, facts: list, batch_size: int = 50) -> list:
    """Process facts verification in batches to respect rate limits"""
    verified_facts = []
    
    for i in range(0, len(facts), batch_size):
        batch = facts[i:i + batch_size]
        print(colored(f"\nProcessing batch {(i//batch_size) + 1} ({len(batch)} facts)...", "cyan"))
        
        verification_tasks = [
            verify_fact(client, fact) 
            for fact in batch
        ]
        batch_results = await asyncio.gather(*verification_tasks)
        verified_facts.extend(batch_results)
        
        # If there are more facts to process, wait 60 seconds
        if i + batch_size < len(facts):
            print(colored("Rate limit cool-down: waiting 60 seconds before next batch...", "yellow"))
            await asyncio.sleep(60)
    
    return verified_facts

async def get_facts(topic: str, num_facts: int) -> list:
    try:
        print(colored(f"Connecting to OpenRouter to get {num_facts} facts about {topic}...", "cyan"))
        
        openrouter_client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY
        )

        facts_list = await get_facts_with_retry(openrouter_client, topic, num_facts)
        
        if not facts_list:
            return []
        
        # Verify facts in batches using Perplexity
        print(colored("Verifying facts using Perplexity AI...", "cyan"))
        perplexity_client = AsyncOpenAI(
            api_key=PERPLEXITY_API_KEY,
            base_url="https://api.perplexity.ai"
        )
        
        if len(facts_list) > 50:
            print(colored(f"Large number of facts ({len(facts_list)}) will be processed in batches of 50", "yellow"))
        
        verified_facts = await verify_facts_batch(perplexity_client, facts_list)
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
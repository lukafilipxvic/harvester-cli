# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "crawl4ai",
#     "instructor",
#     "litellm",
#     "openai",
#     "pydantic>=2.1.0",
#     "python-dotenv",
#     "rich",
# ]
# [tool.uv]
# exclude-newer = "2025-04-26T00:00:00Z"
# ///

import asyncio
import argparse
import os
import sys
import subprocess
from dotenv import load_dotenv
from rich.console import Console
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LXMLWebScrapingStrategy
import instructor
from pydantic import BaseModel
from openai import OpenAI
import json
import importlib.util

console = Console()

def load_schema_class(schema_name: str) -> type[BaseModel]:
    """Dynamically load a schema class from schema.py"""
    spec = importlib.util.spec_from_file_location("schema", "schema.py")
    if spec is None or spec.loader is None:
        raise ImportError("Could not load schema.py")
    
    schema_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(schema_module)
    
    if not hasattr(schema_module, schema_name):
        raise AttributeError(f"Schema class '{schema_name}' not found in schema.py")
    
    return getattr(schema_module, schema_name)

async def main() -> None:
    load_dotenv()
    
    # Install Playwright
    try:
        subprocess.run(["playwright", "install"], check=True)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error installing Playwright: {e}[/red]")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(description="Harvester CLI")
    parser.add_argument(
        "-u", "--url", required=True, help="URL of the website to scrape"
    )
    parser.add_argument(
        "-s", "--schema", required=True, help="Class name of the schema class to use from schema.py" 
    )
    parser.add_argument(
        "-o", "--output", help="Output file path (supports .json or .csv)"
    )
    
    args = parser.parse_args()

    # Load the schema class dynamically
    try:
        SchemaClass = load_schema_class(args.schema)
    except Exception as e:
        result = json.dumps({"Success": False, "error": str(e)})
        if args.output:
            with open(args.output, 'w') as f:
                f.write(result)
        return result

    # Crawl4ai setup
    browser_conf = BrowserConfig(headless=True)
    crawler_conf = CrawlerRunConfig(only_text=True,
                              cache_mode=CacheMode.BYPASS,
                              exclude_external_images=True,
                              excluded_tags=["header", "footer"],
                              scraping_strategy=LXMLWebScrapingStrategy())

    async with AsyncWebCrawler(config=browser_conf) as crawler:
        result = await crawler.arun(url=args.url, config=crawler_conf)
        #print(result.markdown)
        if result.markdown is not None:
            console.print(result.markdown)
        else:
            console.print("No markdown generated.")
            sys.exit()

    client = instructor.from_openai(OpenAI())
    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL") or "gpt-4.1-nano",
        response_model=SchemaClass,
        messages=[
            {
                "role": "system",
                "content": "You are an advanced website structured data/information extraction tool. You will accurately extract data from the following text:",
            },
            {
                "role": "user",
                "content": f"{result.markdown}",
            }
        ]
    )
    
    result = json.dumps(response.model_dump())
    
    # Handle output based on file extension
    if args.output:
        file_ext = os.path.splitext(args.output)[1].lower()
        
        if file_ext == '.csv':
            import csv
            from datetime import datetime
            
            # Convert the response to a dictionary
            data_dict = response.model_dump()
            
            # Add timestamp to the data
            data_dict['timestamp'] = datetime.now().isoformat()
            
            # Reorder fields to put timestamp first
            fieldnames = ['timestamp'] + [f for f in data_dict.keys() if f != 'timestamp']
            
            # Check if file exists to determine if we need to write headers
            file_exists = os.path.isfile(args.output)
            
            with open(args.output, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerow(data_dict)
        else:
            # Default to JSON output
            with open(args.output, 'w') as f:
                f.write(result)
    
    console.print(result)
    return result

if __name__ == "__main__":
    asyncio.run(main())

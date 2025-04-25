# Harvester CLI

Turn the internet into data pipelines. Point Harvester to a website, define what data you want, and get clean, structured output, periodically.

## Quick Start

1. **Install dependencies**:
   ```bash
   # Install uv if you haven't already
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Install dependencies
   uv pip install -r requirements.txt
   ```

2. **Set up your environment**:
   ```bash
   # Create a .env file
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   echo "LLM_MODEL=gpt-4.1-nano" >> .env
   ```

3. **Create your schema**:
   Create a `schema.py` file with your data structure. For example:
   ```python
    from pydantic import BaseModel

    class Website(BaseModel):
        page_name: str
        summary: str
   ```

4. **Run the scraper**:
   ```bash
   uv run harvester.py --url "https://ycombinator.com" --schema "Website" --output "output.json"
   ```

## Command Line Options

- `-u, --url`: URL to scrape (required)
- `-s, --schema`: Schema class name from schema.py (required)
- `-o, --output`: Output file path (optional)

## Setting Up Automated Scraping via Github Actions

1. **Fork this repository**
    ```yaml
    git clone lukafilipxvic/harvester-cli
    ```

2. **Add your secrets**:
   - Go to your repository settings
   - Navigate to Secrets and variables > Actions
   - Add your `OPENAI_API_KEY` and `LLM_MODEL` as secrets

3. **Configure the workflow**:
   Edit `.github/workflows/scrape.yml`:
   ```yaml
   - name: Run scraper
     env:
       OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
       LLM_MODEL: ${{ secrets.LLM_MODEL }}
     run: |
       python harvester.py -u "https://example.com" -s "YourSchemaClass" -o "output.json"
   ```

4. **Commit and push**:
   The workflow will run automatically based on the schedule (default: every 6 hours)

## Creating Your Schema.py file

Your schema defines what data you want to extract. Here's a more detailed example:
```python
from pydantic import BaseModel
from typing import Optional

class NewsArticle(BaseModel):
    title: str
    author: Optional[str]
    publish_date: str
    content: str
    url: str
    category: Optional[str]
```

The schema should match the structure of the data you want to extract from the website.

## Tips for Better Results

1. **Start simple**: Begin with a basic schema and add fields as needed
2. **Test manually**: Run the scraper once to verify the output
3. **Refine your schema**: Adjust based on the actual website content
4. **Use GitHub Actions**: Set up automated scraping to build your data library over time

## Example Use Cases

- **Time Series Databases**: Build data pipelines over time.
- **Price tracking**: Monitor product prices across e-commerce sites
- **News aggregation**: Collect articles from multiple sources
- **Research**: Build a database of academic papers or articles
- **Market analysis**: Track changes in competitor websites

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

Licensed under AGPL-3.0.
# AI-Powered Fact Generator and Verifier

A Python tool that generates interesting facts about any topic and performs AI-assisted verification using dual language models. The tool uses OpenRouter for fact generation and Perplexity AI's web-search capabilities for fact verification attempts.

## ⚠️ Important Disclaimer

This tool uses AI models and Perplxity web search for verifying facts. Results should not be treated as authoritative fact-checking. Please independently verify any facts for critical use cases. Best suited for educational and entertainment purposes.

## 🌟 Features

- Generate customizable number of facts about any topic using GPT-4
- AI-assisted fact verification using Perplexity AI's web search capabilities
- Parallel processing with rate limit handling
- Separate storage of verified and unverified claims
- Detailed statistics about verification results
- Color-coded console output for better readability
- Structured JSON output with verification assessments
- Robust error handling and progress feedback

## ❤️ Support & Get 400+ AI Projects

This is one of 400+ fascinating projects in my collection! [Support me on Patreon](https://www.patreon.com/c/echohive42/membership) to get:

- 🎯 Access to 400+ AI projects (and growing daily!)
  - Including advanced projects like [2 Agent Real-time voice template with turn taking](https://www.patreon.com/posts/2-agent-real-you-118330397)
- 📥 Full source code & detailed explanations
- 📚 1000x Cursor Course
- 🎓 Live coding sessions & AMAs
- 💬 1-on-1 consultations (higher tiers)
- 🎁 Exclusive discounts on AI tools & platforms (up to $180 value)

![image](https://github.com/user-attachments/assets/6f435a0c-1301-47a4-979d-9b8ced619862)

## 🛠️ Requirements

- Python 3.7+
- OpenRouter API key
- Perplexity AI API key

## 📦 Installation

1. Clone the repository:

```bash
cd fact-generator
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
export OPENROUTER_API_KEY="your_openrouter_api_key"
export PERPLEXITY_API_KEY="your_perplexity_api_key"
```

## 🚀 Usage

Run the script:

```bash
python facts_generator.py
```

The tool will:

1. Generate facts using OpenRouter's GPT-4
2. Attempt verification using Perplexity AI's web search
3. Display results with verification status (✓ for verified, ✗ for unverified)
4. Save results to `verified_facts.json`

## 📄 Output Format

Results are saved in JSON format:

```json
{
    "topic": "your_topic",
    "timestamp": "2024-01-01T12:00:00.000000",
    "true_facts": [
        {
            "fact": "Verified claim",
            "verified": true
        }
    ],
    "false_facts": [
        {
            "fact": "Unverified claim",
            "verified": false
        }
    ],
    "statistics": {
        "total_facts": 10,
        "true_facts_count": 7,
        "false_facts_count": 3,
        "accuracy_rate": "70.0%"
    }
}
```

## 🎨 Models Used

- Fact Generation: OpenRouter GPT-4 (2024-11-20)
- Fact Verification: Perplexity AI's Llama 3.1 Sonar with web search

## 🎨 Console Output

The tool provides colorful console output:

- 🟦 Cyan: Processing status and statistics
- 🟩 Green: Success messages and verified claims
- 🟨 Yellow: Warnings and parsing information
- 🟥 Red: Errors and unverified claims

## ⚠️ Rate Limits

- Processes facts in batches of 50
- Implements 60-second delays between batches
- Handles rate limit errors with automatic retries

## 💡 Best Practices

- Use specific topics rather than broad categories
- Independently verify facts for critical use cases
- Consider the verification as a preliminary assessment
- Check the JSON output for detailed statistics
- Be patient with large fact sets due to rate limiting

## 📝 License

MIT License - feel free to use and modify as needed!

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check [issues page](link-to-issues).

# AI-Powered Fact Generator and Verifier

A sophisticated Python tool that generates interesting facts about any topic and automatically verifies them using dual AI systems. The tool uses OpenRouter for fact generation and Perplexity AI for fact verification, providing a reliable source of verified information.
![image](https://github.com/user-attachments/assets/2292a1bd-bc2e-4389-bff5-32c359f1b2a2)


## 🌟 Features

- Generate customizable number of facts about any topic
- Automatic fact verification using Perplexity AI
- Parallel processing for efficient verification
- Separate storage of true and false facts
- Detailed statistics about verification results
- Color-coded console output for better readability
- Structured JSON output with verification results
- Robust error handling and progress feedback

- ## ❤️ Support & Get 400+ AI Projects

This is one of 400+ fascinating projects in my collection! [Support me on Patreon](https://www.patreon.com/c/echohive42/membership) to get:

- 🎯 Access to 400+ AI projects (and growing daily!)
  - Including advanced projects like [2 Agent Real-time voice template with turn taking](https://www.patreon.com/posts/2-agent-real-you-118330397)
- 📥 Full source code & detailed explanations
- 📚 1000x Cursor Course
- 🎓 Live coding sessions & AMAs
- 💬 1-on-1 consultations (higher tiers)
- 🎁 Exclusive discounts on AI tools & platforms (up to $180 value)


## 🛠️ Requirements

- Python 3.7+
- OpenRouter API key
- Perplexity AI API key

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fact-generator.git
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

Follow the prompts to:
1. Enter a topic of interest
2. Specify the number of facts you want

The script will:
- Generate facts using OpenRouter's GPT-4
- Verify each fact using Perplexity AI
- Display results with verification status (✓ for true, ✗ for false)
- Save results to `verified_facts.json`

## 📄 Output Format

The results are saved in JSON format with the following structure:
```json
{
    "topic": "your_topic",
    "timestamp": "2024-01-01T12:00:00.000000",
    "true_facts": [
        {
            "fact": "Verified fact",
            "verified": true
        }
    ],
    "false_facts": [
        {
            "fact": "Unverified fact",
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

## 🎨 Console Output

The tool provides colorful console output:
- 🟦 Cyan: Processing status and statistics
- 🟩 Green: Success messages and verified facts
- 🟨 Yellow: Warnings and parsing information
- 🟥 Red: Errors and unverified facts

## ⚠️ Error Handling

The script includes comprehensive error handling for:
- API connection issues
- XML parsing errors
- Invalid user input
- File operations
- Network timeouts

## 🔄 Models Used

- Fact Generation: OpenRouter GPT-4 (2024-11-20)
- Fact Verification: Perplexity AI's Llama 3.1 Sonar

## 📝 License

MIT License - feel free to use and modify as needed!

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check [issues page](link-to-issues).

## 💡 Tips

- For best results, use specific topics rather than broad categories
- The verification process may take longer for larger numbers of facts
- Check the JSON output file for detailed statistics and full results 

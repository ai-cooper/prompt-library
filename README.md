# Prompt Library

A curated collection of prompts and configurations for AI-powered development tools, with a focus on Cursor IDE and AI agents.

## 📋 Overview

This repository serves as a centralized library of prompts, rules, and configurations designed to enhance AI-assisted development workflows. Whether you're using Cursor IDE, GitHub Copilot, or other AI coding assistants, you'll find useful prompts and patterns here.

## 🗂️ Repository Structure

```
prompt-library/
├── Cursor/
│   └── Agent/          # Cursor AI Agent prompts and configurations
├── LICENSE             # MIT License
└── README.md          # This file
```

## 🚀 Getting Started

### Prerequisites

- [Cursor IDE](https://cursor.sh/) (for Cursor-specific prompts)
- Basic understanding of AI-assisted development
- Git for cloning the repository

### Installation

Clone the repository to your local machine:

```bash
git clone https://github.com/ai-cooper/prompt-library.git
cd prompt-library
```

## 💡 Usage

### Cursor Agent Prompts

Navigate to the `Cursor/Agent` directory to find prompts specifically designed for Cursor's AI agent:

```bash
cd Cursor/Agent
```

Each prompt file includes:
- **Purpose**: What the prompt is designed to accomplish
- **Usage Instructions**: How to apply the prompt in your workflow
- **Examples**: Sample outputs or use cases
- **Customization Tips**: How to adapt the prompt to your needs

### Applying Prompts

1. **Copy the prompt** from the relevant file
2. **Paste into your AI assistant** (Cursor chat, Copilot, etc.)
3. **Customize** as needed for your specific use case
4. **Iterate** based on results


## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Adding New Prompts

1. **Fork** the repository
2. **Create a branch** for your prompt:
   ```bash
   git checkout -b feature/new-prompt-name
   ```
3. **Add your prompt** in the appropriate directory
4. **Follow the template**:
   ```markdown
   # Prompt Name
   
   ## Purpose
   Brief description of what this prompt does
   
   ## Prompt
   ```
   [Your prompt text here]
   ```
   
   ## Usage
   Instructions on how to use this prompt
   
   ## Examples
   Sample outputs or use cases
   
   ## Customization
   Tips for adapting the prompt
   ```
5. **Commit your changes**:
   ```bash
   git commit -m "Add: [Prompt Name] for [Use Case]"
   ```
6. **Push to your fork**:
   ```bash
   git push origin feature/new-prompt-name
   ```
7. **Open a Pull Request**

### Prompt Quality Guidelines

- **Clear and Specific**: Prompts should have well-defined objectives
- **Reusable**: Design prompts that can be adapted to various contexts
- **Documented**: Include usage instructions and examples
- **Tested**: Verify prompts work as expected before submitting
- **Organized**: Place prompts in appropriate directories

## 📖 Prompt Categories

### By Tool
- **Cursor**: IDE-specific prompts and configurations

### By Language
- **Python**: Python-specific prompts
- **JavaScript/TypeScript**: JS/TS development prompts
- **Shell/Bash**: Script and automation prompts
- **Go, Rust, Java, etc.**: Language-specific collections

## 🛠️ Best Practices

### Prompt Engineering Tips

1. **Be Specific**: Clearly define what you want the AI to do
2. **Provide Context**: Include relevant background information
3. **Set Constraints**: Specify requirements, limitations, or preferences
4. **Iterate**: Refine prompts based on results
5. **Version Control**: Track prompt evolution and effectiveness

### Example Prompt Structure

```markdown
You are an expert [role/domain] with deep knowledge of [specific area].

**Task**: [Clear description of what needs to be done]

**Context**: [Relevant background information]

**Requirements**:
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

**Output Format**: [Desired format]

**Constraints**: [Any limitations or restrictions]
```

## 📊 Prompt Performance

Track and share prompt effectiveness:
- **Success Rate**: How often the prompt achieves desired results
- **Use Cases**: Scenarios where the prompt excels
- **Limitations**: Known constraints or failure modes
- **Improvements**: Suggested enhancements

## 🔗 Related Resources

### Cursor IDE
- [Cursor Documentation](https://cursor.sh/docs)
- [Cursor Community](https://forum.cursor.sh/)

### Prompt Engineering
- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic Prompt Engineering](https://docs.anthropic.com/claude/docs/prompt-engineering)

### AI-Assisted Development
- [GitHub Copilot](https://github.com/features/copilot)
- [AI Coding Tools Comparison](https://github.com/topics/ai-coding-assistant)

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to all contributors who share their prompts
- Inspired by the AI-assisted development community
- Built for developers, by developers

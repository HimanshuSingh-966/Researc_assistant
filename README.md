# IBM Academic Research Agent

![IBM Watson](https://img.shields.io/badge/Powered%20by-IBM%20Watson-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange)
![License](https://img.shields.io/badge/License-ILAN-blue)

A powerful academic research assistant built with IBM watsonx.ai that helps researchers, students, and academics with comprehensive research tasks including literature analysis, citation generation, hypothesis development, and academic writing assistance.

## 🎯 Project Overview

This Academic Research Agent is designed specifically for the **IBM SkillsBuild for Academia program** and optimized for **IBM Cloud Lite tier services**. It provides intelligent research assistance without requiring document uploads or vector databases.

### Key Capabilities

- 🔍 **Literature Search & Analysis**: Find and summarize recent academic research
- 📚 **Multi-Format Citations**: Generate APA, MLA, and IEEE citations automatically  
- 🧪 **Hypothesis Generation**: Create testable research hypotheses
- ✍️ **Academic Writing**: Draft paper sections (Introduction, Literature Review, Methodology)
- 📊 **Structured Outputs**: Export results in JSON and Markdown formats
- 🔄 **Research Workflows**: Pre-built templates for different research types
- 🌐 **Web Search Integration**: Access current information via Google, DuckDuckGo, Wikipedia

## 📋 Features

### Core Research Tools
- **Smart Literature Search**: Find relevant academic papers and sources
- **Citation Generator**: Professional citation formatting in multiple styles
- **Hypothesis Development**: Generate testable research hypotheses with rationales
- **Section Drafting**: Create structured outlines for academic paper sections
- **Research Synthesis**: Comprehensive analysis and gap identification

### Advanced Features  
- **Batch Processing**: Handle multiple research queries simultaneously
- **Research Workflows**: Templates for literature reviews, research proposals, systematic reviews
- **Export Utilities**: Save results in multiple formats (Markdown, JSON, PDF-ready)
- **Interactive Interface**: Command-line interface with help system
- **Memory Management**: Conversation history and session management

### Web Integration
- **Real-time Search**: Access to current research via web search engines
- **Source Verification**: Multi-source validation for research claims
- **Citation Tracking**: Automatic source attribution and reference management

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8 or higher
- IBM Cloud account (Free Lite tier supported)
- IBM watsonx.ai access
- Jupyter Notebook or JupyterLab

### Step 1: Clone Repository

```bash
https://github.com/HimanshuSingh-966/Research_assistant.git
cd Research_assistant
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set Up IBM Cloud Credentials

1. Create an IBM Cloud account at [cloud.ibm.com](https://cloud.ibm.com)
2. Create a watsonx.ai service instance
3. Generate an API key from IBM Cloud IAM
4. Note your project ID from watsonx.ai

### Step 4: Configure Environment

Create a `.env` file (optional) or export environment variables:

```bash
export PROJECT_ID=your-watsonx-project-id
export SPACE_ID=your-watsonx-space-id  # if using spaces instead of projects
```

## 🚀 Usage

### Option 1: Jupyter Notebook (Recommended)

1. Open the notebook:
   ```bash
   jupyter notebook Research_Agent_NoteBook.ipynb
   ```

2. Run cells sequentially, entering your IBM Cloud API key when prompted

3. Use the interactive interface or test functions

### Option 2: Direct Python Execution

```python
from research_agent import create_research_agent, research_query

# Initialize agent
agent = create_research_agent()

# Make research queries
result = research_query("Find recent research on climate change mitigation")
print(result)
```

## 💡 Using the Research Agent

### Basic Research Queries

```python
# Literature search
result = test_literature_search("machine learning in healthcare")

# Generate citations  
citation = test_citation_generation(
    "Smith, J. & Doe, A.", 
    "AI in Medical Diagnosis", 
    "2024", 
    "Journal of Medical AI", 
    "APA"
)

# Create hypotheses
hypotheses = test_hypothesis_generation(
    "Does social media usage affect student academic performance?"
)

# Draft paper sections
intro = test_section_drafting("Introduction", "renewable energy policy")
```

### Advanced Research Workflows

```python
# Run comprehensive literature review
report = run_research_workflow("artificial intelligence ethics", "literature_review")

# Generate research proposal
proposal = run_research_workflow("quantum computing applications", "research_proposal")

# Create systematic review
review = run_research_workflow("sustainable urban planning", "systematic_review")
```

### Interactive Commands

- `help` - Show available commands and capabilities
- `json` - Get next response in JSON format
- `clear` - Start new research session  
- `exit` - Quit the research agent

## 📊 Research Workflows

### Literature Review Workflow
1. Find seminal papers and foundational research
2. Identify current theoretical frameworks  
3. Summarize recent empirical studies
4. Analyze methodological approaches
5. Identify research gaps and controversies
6. Suggest synthesis of current knowledge

### Research Proposal Workflow  
1. Provide background and context
2. Identify research problems and questions
3. Generate testable hypotheses
4. Suggest appropriate methodologies
5. Analyze limitations and ethical considerations
6. Discuss expected outcomes and significance

### Systematic Review Workflow
1. Define search strategy and inclusion criteria
2. Identify key databases and sources
3. Develop data extraction framework
4. Analyze quality assessment criteria
5. Synthesize findings across studies
6. Discuss implications and recommendations

## ⚙️ Configuration Options

### Model Parameters (Optimized for Research)

```python
parameters = {
    "frequency_penalty": 0.1,  # Reduce repetition
    "max_tokens": 4000,       # Longer responses  
    "presence_penalty": 0.1,  # Diverse vocabulary
    "temperature": 0.3,       # Balanced creativity
    "top_p": 0.9             # Good diversity
}
```

### Available Models
- `meta-llama/llama-3-3-70b-instruct` (Default - Best for complex reasoning)
- Other IBM watsonx.ai supported models

## 📤 Export & Integration

### Export Formats
- **Markdown**: Perfect for documentation and reports
- **JSON**: Structured data for further processing
- **Bibliography**: Formatted reference lists
- **Research Reports**: Comprehensive multi-section documents

### Integration Options
- Reference managers (Zotero, Mendeley)
- Writing software (LaTeX, Microsoft Word)  
- Data analysis tools (Python, R)
- Institutional repositories

## 🔧 IBM Cloud Lite Optimization

This project is specifically optimized for IBM Cloud Lite tier:

- **Efficient API Usage**: Smart caching and request optimization
- **Batch Processing**: Handle multiple queries efficiently  
- **No Storage Requirements**: No need for premium storage services
- **Memory Efficient**: Optimized for limited resource environments
- **Rate Limit Handling**: Built-in retry logic for API limits

## 📚 Example Use Cases

### For Students
- Literature reviews for assignments
- Citation formatting for papers
- Hypothesis development for thesis projects
- Academic writing assistance

### For Researchers  
- Systematic literature reviews
- Research proposal development
- Gap analysis in research fields
- Collaborative research planning

### For Educators
- Course material development
- Research methodology teaching
- Student research guidance
- Academic writing instruction

## ⚠️ Important Notes

### Academic Integrity
- Always verify information from multiple sources
- Use as a research starting point, not final authority
- Properly cite all sources in your work
- Review and fact-check generated content

### Best Practices
- Be specific in research questions
- Include context and background information
- Specify desired output format
- Cross-reference with academic databases
- Maintain research logs and version control

### Limitations
- Based on web-accessible sources
- May not include most recent publications
- Requires internet connection for searches
- Subject to IBM Cloud Lite tier limits

## 🔍 Troubleshooting

### Common Issues

**"Please enter your api key"**
- Ensure you have a valid IBM Cloud API key
- Check that watsonx.ai service is active

**"Rate limit exceeded"**  
- Wait a few minutes between requests
- Use batch processing for multiple queries

**"Model not found"**
- Verify your project/space ID is correct
- Check that the model is available in your region

**"Connection error"**
- Verify internet connection
- Check IBM Cloud service status

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Licensed Materials - Copyright © 2024 IBM. This project is released under the terms of the ILAN License. Use, duplication disclosure restricted by GSA ADP Schedule Contract with IBM Corp.

**Note:** This Academic Research Agent is designed for educational use in the IBM SkillsBuild for Academia program.

## 🙏 Acknowledgments

- **IBM watsonx.ai** - Core AI capabilities
- **LangChain & LangGraph** - Agent framework
- **IBM SkillsBuild for Academia** - Educational program support
- **Open Source Community** - Various utility libraries

## 📞 Support

For support and questions:

- Check the [troubleshooting section](#-troubleshooting)
- Review [IBM watsonx.ai documentation](https://www.ibm.com/products/watsonx-ai)
- Submit issues via GitHub Issues
- Contact IBM SkillsBuild support for program-related questions

## 🔮 Future Enhancements

- Web interface with Streamlit
- Integration with academic databases (PubMed, arXiv)
- Advanced visualization capabilities
- Collaborative research features
- Mobile-responsive interface
- API endpoint for external integrations

---

**Ready to revolutionize your research workflow with AI?** 🚀

Get started with the Academic Research Agent and experience the power of IBM watsonx.ai for academic research!

---

*Built with ❤️ for the academic community*

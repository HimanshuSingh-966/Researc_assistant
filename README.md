# IBM Agentic Research Assistant

![IBM Watson](https://img.shields.io/badge/Powered%20by-IBM%20Watson-blue)
![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B)
![License](https://img.shields.io/badge/License-MIT-green)

An intelligent research assistant that leverages IBM Watson ML models to analyze academic papers, generate summaries, citations, hypotheses, and section drafts.

## 📋 Features

- **Text Analysis**: Extract key insights from academic papers
- **Citation Generation**: Auto-generate citations in APA, MLA, and IEEE formats
- **Hypothesis Development**: Generate testable hypotheses based on research questions
- **Section Drafting**: Create academic section drafts for your research papers
- **PDF Support**: Upload and extract text from PDF research papers
- **Rate Limit Handling**: Smart handling of API rate limits with auto-retry
- **Cloud Storage**: Automatic saving of outputs to IBM Cloud Object Storage

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- IBM Cloud account with Watson Machine Learning service
- IBM Cloud Object Storage service (optional but recommended)

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/ibm-research-assistant.git
   cd ibm-research-assistant
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your IBM credentials:
   ```
   API_KEY=your_ibm_watson_api_key
   DEPLOYMENT_ID=your_model_deployment_id
   COS_API_KEY=your_cos_api_key
   COS_INSTANCE_ID=your_cos_instance_id
   COS_ENDPOINT=your_cos_endpoint
   COS_BUCKET=your_bucket_name
   ```

## ⚙️ Configuration

### Required Environment Variables

| Variable | Description |
|----------|-------------|
| `API_KEY` | IBM Watson Machine Learning API key |
| `DEPLOYMENT_ID` | Deployment ID of your IBM Watson model |

### Optional Environment Variables (for Cloud Storage)

| Variable | Description |
|----------|-------------|
| `COS_API_KEY` | IBM Cloud Object Storage API key |
| `COS_INSTANCE_ID` | IBM Cloud Object Storage instance ID |
| `COS_ENDPOINT` | IBM Cloud Object Storage endpoint URL |
| `COS_BUCKET` | IBM Cloud Object Storage bucket name |

## 🚀 Usage

1. Start the application:
   ```bash
   streamlit run app.py
   ```

2. Access the web interface at `http://localhost:8501`

3. Enter your research input or upload a PDF file

4. Click "Generate Output" to analyze and process your research material

## 💡 Using the Research Assistant

### Upload Academic Material
- Upload PDF papers or paste abstracts directly
- Provide title, authors, journal information, and DOI

### Generate Research Outputs
- Summaries are displayed as bullet points
- Citations are formatted in multiple styles
- Hypotheses are presented in a structured format
- Section drafts are provided in a text area for easy copying

### Save and Download
- All outputs are automatically saved to IBM Cloud Object Storage (if configured)
- Download individual elements (citations, drafts) as needed

## ⚠️ Rate Limit Considerations

This application implements smart rate limit handling for the IBM Watson ML API:

- Automatic retry with exponential backoff for 429 errors
- Request caching to avoid redundant API calls
- Visual feedback during rate limit waits

Tips to avoid rate limits:
- Space out your requests (wait a minute between submissions)
- Use the example first to ensure everything works
- Keep your abstracts concise for faster processing
- Save your outputs to avoid repeating requests

## 🔍 Troubleshooting

### Common Issues

- **"API_KEY not set in .env file"**: Ensure your .env file contains the correct API key
- **"Rate limit exceeded"**: Wait a few minutes before trying again
- **"Error extracting PDF text"**: Check that your PDF is not encrypted or corrupted
- **"Cloud Object Storage connection failed"**: Verify your COS credentials are correct

### Debugging

- Check the application logs for detailed error information
- Use the "Check Connections" button in the sidebar to verify API connectivity
- Clear the cache if responses seem incorrect or outdated

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- IBM Watson for providing the ML capabilities
- Streamlit for the web interface framework
- PyPDF2 for PDF parsing functionality

---

## Technical Details

This application uses several advanced techniques:

- **Rate Limiting**: Custom implementation of request tracking and backoff
- **Caching**: In-memory caching to reduce API calls
- **Error Handling**: Robust error handling with informative user feedback
- **Streaming Responses**: Support for streaming API responses to improve UX

For more information on IBM Watson services, visit the [IBM Cloud documentation](https://cloud.ibm.com/docs).
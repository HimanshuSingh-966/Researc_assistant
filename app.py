import os
import json
import streamlit as st
import requests
import time  # Added missing import
import random  # Added missing import
import hashlib  # Added missing import
from datetime import datetime, timedelta 
from typing import Dict, List, Optional, Any
import logging
import traceback
from dotenv import load_dotenv
from io import BytesIO
from PyPDF2 import PdfReader
import ibm_boto3
from ibm_botocore.client import Config
from ibm_botocore.exceptions import ClientError

# Load environment variables
load_dotenv()

# Config
API_KEY = os.getenv("API_KEY")
DEPLOYMENT_ID = os.getenv("DEPLOYMENT_ID")
COS_API_KEY = os.getenv("COS_API_KEY")
COS_INSTANCE_ID = os.getenv("COS_INSTANCE_ID")
COS_ENDPOINT = os.getenv("COS_ENDPOINT")
COS_BUCKET = os.getenv("COS_BUCKET")

# Basic validation
required_vars = [
    ("API_KEY", API_KEY), 
    ("DEPLOYMENT_ID", DEPLOYMENT_ID),
    ("COS_API_KEY", COS_API_KEY),
    ("COS_INSTANCE_ID", COS_INSTANCE_ID),
    ("COS_ENDPOINT", COS_ENDPOINT),
    ("COS_BUCKET", COS_BUCKET)
]

missing_vars = [name for name, value in required_vars if not value]
if missing_vars:
    st.error(f"❌ The following environment variables are missing: {', '.join(missing_vars)}")
    st.info("Please add them to your .env file with the following format:")
    for name in missing_vars:
        st.code(f"{name}=your_value_here")
    st.stop()

# Logger setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Simple in-memory cache
request_cache = {}

# IBM Watson ML Client with rate limit handling
class IBMWatsonMLClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.iam_token_url = "https://iam.cloud.ibm.com/identity/token"
        self.base_url = "https://us-south.ml.cloud.ibm.com/ml/v1"
        self.access_token = None
        self.token_expiry = datetime.now()
        
        # Rate limiting components
        self.max_retries = 5
        self.base_delay = 2  # Base delay in seconds
        self.max_delay = 60  # Maximum delay in seconds
        
        # Track requests for rate limiting
        self.requests_this_minute = []
        self.requests_this_hour = []

    def authenticate(self) -> str:
        """Authenticate with IBM Cloud and get access token"""
        try:
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": self.api_key
            }
            response = requests.post(self.iam_token_url, headers=headers, data=data)
            response.raise_for_status()
            
            auth_data = response.json()
            self.access_token = auth_data.get('access_token')
            
            # Set token expiry time (usually 1 hour, but subtract 5 min for safety)
            expires_in = auth_data.get('expires_in', 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 300)
            
            return self.access_token
        except Exception as e:
            st.error(f"Authentication error: {str(e)}")
            raise

    def is_token_valid(self):
        """Check if the current token is valid"""
        return self.access_token and datetime.now() < self.token_expiry
    
    def clean_request_tracking(self):
        """Remove old timestamps from request tracking"""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        
        self.requests_this_minute = [t for t in self.requests_this_minute if t > minute_ago]
        self.requests_this_hour = [t for t in self.requests_this_hour if t > hour_ago]
    
    def check_rate_limits(self):
        """Check if we're hitting rate limits"""
        self.clean_request_tracking()
        
        # IBM typically allows 5-10 requests per minute in free tier
        # These are example values - adjust based on your tier
        max_per_minute = 5
        max_per_hour = 100
        
        return {
            "minute_exceeded": len(self.requests_this_minute) >= max_per_minute,
            "hour_exceeded": len(self.requests_this_hour) >= max_per_hour,
            "wait_time": self.calculate_wait_time(self.requests_this_minute, max_per_minute, 60)
        }
    
    def calculate_wait_time(self, requests, max_requests, window_seconds):
        """Calculate how long to wait before next request"""
        if not requests or len(requests) < max_requests:
            return 0
            
        # Calculate time until oldest request leaves the window
        oldest = requests[0]
        wait_seconds = (oldest + timedelta(seconds=window_seconds) - datetime.now()).total_seconds()
        return max(0, wait_seconds + 0.1)  # Add a small buffer
    
    def record_request(self):
        """Record this request for rate limiting"""
        now = datetime.now()
        self.requests_this_minute.append(now)
        self.requests_this_hour.append(now)

    def chat_completion(self, deployment_id: str, messages: List[Dict[str, str]], 
                        stream: bool = False, version: str = "2021-05-01"):
        """Send a request to the Watson ML chat API with rate limit handling"""
        # Check cache first (only for non-streaming requests)
        if not deployment_id:
            raise ValueError("deployment_id cannot be None")
        if not stream:
            cache_key = hashlib.md5(json.dumps(messages, sort_keys=True).encode()).hexdigest()
            if cache_key in request_cache:
                logger.info("Using cached response")
                return request_cache[cache_key]
        
        # Check rate limits
        rate_limits = self.check_rate_limits()
        if rate_limits["minute_exceeded"]:
            wait_time = rate_limits["wait_time"]
            if wait_time > 0:
                # Show wait time in UI
                progress_bar = st.progress(0)
                message = st.empty()
                
                for i in range(int(wait_time) + 1):
                    progress = i / wait_time
                    message.info(f"⏳ Rate limit reached. Waiting {wait_time - i:.1f} seconds...")
                    progress_bar.progress(progress)
                    time.sleep(1)
                    
                message.empty()
                progress_bar.empty()
        
        # Ensure we have a valid token
        if not self.is_token_valid():
            self.authenticate()
            
        # Select the appropriate endpoint
        if stream:
            endpoint = "text/generation_stream"
        else:
            endpoint = "text/generation"
            
        url = f"{self.base_url}/deployments/{deployment_id}/{endpoint}"
        
        # Execute the request with retries and backoff
        for attempt in range(self.max_retries):
            try:
                # Prepare headers
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.access_token}",
                    "Accept": "application/json"
                }
                
                # Make the request
                response = requests.post(
                    url, 
                    headers=headers, 
                    params={"version": version}, 
                    json={"messages": messages},
                    stream=stream
                )
                
                # Record this request for rate limiting
                self.record_request()
                
                # Handle specific status codes
                if response.status_code == 429:  # Too Many Requests
                    retry_after = int(response.headers.get('Retry-After', self.base_delay * (2 ** attempt)))
                    wait_time = min(retry_after + random.uniform(0.1, 1.0), self.max_delay)
                    
                    if attempt < self.max_retries - 1:
                        # Show wait message
                        st.warning(f"⏳ Rate limit exceeded. Waiting {wait_time:.1f} seconds before retry {attempt+1}/{self.max_retries}...")
                        time.sleep(wait_time)
                        continue
                    else:
                        st.error(f"❌ Rate limit exceeded after {self.max_retries} retries. Please try again later.")
                        raise Exception("Rate limit exceeded after multiple retries")
                
                elif response.status_code == 401:  # Unauthorized
                    # Token might be expired, refresh and retry
                    self.authenticate()
                    continue
                
                # For any other error, raise it
                response.raise_for_status()
                
                # Success! Process and cache the response if non-streaming
                if not stream:
                    result = response.json()
                    request_cache[cache_key] = result  # Cache the result
                    return result
                else:
                    return response
                
            except requests.exceptions.HTTPError as e:
                # Already handled 429 and 401 above
                if e.response.status_code not in (429, 401):
                    error_msg = str(e)
                    try:
                        error_json = e.response.json()
                        if 'error' in error_json:
                            error_msg = f"{error_msg} - {error_json['error']}"
                    except:
                        pass
                    
                    st.error(f"API error: {error_msg}")
                    
                    # If we're out of retries, raise the error
                    if attempt >= self.max_retries - 1:
                        raise
                    
                    # Otherwise backoff and retry
                    wait_time = min(self.base_delay * (2 ** attempt) + random.uniform(0.1, 1.0), self.max_delay)
                    time.sleep(wait_time)
                    
            except Exception as e:
                st.error(f"Request error: {str(e)}")
                if attempt >= self.max_retries - 1:
                    raise
                
                wait_time = min(self.base_delay * (2 ** attempt) + random.uniform(0.1, 1.0), self.max_delay)
                time.sleep(wait_time)
        
        # If we get here, all retries failed
        raise Exception(f"Failed after {self.max_retries} attempts")

# Cloud Object Storage functions
def get_cos_client():
    """Get IBM COS client"""
    try:
        if not COS_API_KEY or not COS_INSTANCE_ID:
            return None
            
        cos = ibm_boto3.client("s3",
            ibm_api_key_id=COS_API_KEY,
            ibm_service_instance_id=COS_INSTANCE_ID,
            config=Config(signature_version="oauth"),
            endpoint_url=COS_ENDPOINT
        )
        return cos
    except Exception as e:
        st.error(f"Error creating COS client: {str(e)}")
        return None

def ensure_bucket_exists(cos_client, bucket_name):
    """Create bucket if it doesn't exist"""
    try:
        # Check if the bucket exists
        cos_client.head_bucket(Bucket=bucket_name)
        return True
    except ClientError as e:
        # If a client error is thrown, check if it's a 404 error.
        if e.response.get('Error', {}).get('Code') == '404':
            try:
                # Create the bucket
                location_constraint = 'us-south-standard'
                cos_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={
                        'LocationConstraint': location_constraint
                    }
                )
                return True
            except Exception as create_e:
                st.error(f"Error creating bucket: {str(create_e)}")
                return False
        else:
            st.error(f"Error checking bucket: {str(e)}")
            return False
    except Exception as e:
        st.error(f"Unexpected error with bucket {bucket_name}: {str(e)}")
        return False

def upload_to_cos(filename: str, data: str, max_retries=3):
    """Upload data to IBM Cloud Object Storage with retries"""
    cos_client = get_cos_client()
    if not cos_client:
        return False
        
    for attempt in range(max_retries):
        try:
            # Ensure bucket exists
            if not ensure_bucket_exists(cos_client, COS_BUCKET):
                return False
            
            # Upload the file
            cos_client.put_object(
                Bucket=COS_BUCKET, 
                Key=filename, 
                Body=data.encode('utf-8')
            )
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                st.error(f"COS upload error after {max_retries} attempts: {str(e)}")
                return False

# Response handlers
def handle_streaming_response(response):
    """Process a streaming response from the API"""
    stream_container = st.empty()
    full_content = ""
    
    try:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                try:
                    # Try to decode as JSON
                    chunk_str = chunk.decode('utf-8')
                    if chunk_str.startswith('data:'):
                        # Handle SSE format
                        json_str = chunk_str.replace('data:', '').strip()
                        data = json.loads(json_str)
                        text_chunk = data.get('results', [{}])[0].get('generated_text', '')
                    else:
                        # Try parsing as direct JSON
                        data = json.loads(chunk_str)
                        text_chunk = data.get('results', [{}])[0].get('generated_text', '')
                except:
                    # If parsing fails, just use the raw chunk
                    text_chunk = chunk.decode('utf-8', errors='replace')
                
                full_content += text_chunk
                stream_container.markdown(full_content)
    except Exception as e:
        st.error(f"Error processing streaming response: {str(e)}")
        logger.error(traceback.format_exc())
    
    # Try to parse as JSON
    try:
        return json.loads(full_content)
    except:
        # Return as raw content if not JSON
        return {"raw_content": full_content}

def parse_response(response):
    """Parse the non-streaming response"""
    try:
        # Extract the generated text from the response
        if 'results' in response and len(response['results']) > 0:
            content = response['results'][0].get('generated_text', '')
        else:
            content = str(response)
        
        # Try to parse as JSON
        try:
            return json.loads(content)
        except:
            # If not valid JSON, check if there's a JSON block in markdown
            if "```json" in content and "```" in content.split("```json", 1)[1]:
                json_block = content.split("```json", 1)[1].split("```", 1)[0].strip()
                try:
                    return json.loads(json_block)
                except:
                    pass
            
            # Return raw content if parsing fails
            return {"raw_content": content}
    except Exception as e:
        st.error(f"Error parsing response: {str(e)}")
        return {"error": str(e)}

# Streamlit UI
st.set_page_config(page_title="IBM Research Assistant", layout="wide")
st.title("🔬 IBM Agentic Research Assistant")

if 'research_output' not in st.session_state:
    st.session_state.research_output = {}

if 'client' not in st.session_state:
    if API_KEY:
        st.session_state.client = IBMWatsonMLClient(api_key=API_KEY)
    else:
        st.error("❌ API_KEY is missing. Please check your environment variables.")
        st.stop()

# File Upload
uploaded_file = st.sidebar.file_uploader("📄 Upload Academic Paper (PDF/Text)", type=["pdf", "txt"])
if uploaded_file:
    if uploaded_file.type == "application/pdf":
        try:
            reader = PdfReader(uploaded_file)
            abstract = "\n".join([page.extract_text() for page in reader.pages[:2]])
        except Exception as e:
            st.sidebar.error(f"Error extracting PDF text: {str(e)}")
            abstract = ""
    else:
        try:
            abstract = uploaded_file.read().decode("utf-8")
        except Exception as e:
            st.sidebar.error(f"Error reading text file: {str(e)}")
            abstract = ""
    st.sidebar.success("✅ Abstract extracted.")
else:
    abstract = ""

# Streaming option
use_streaming = st.sidebar.checkbox("Enable streaming responses", value=False)

# Rate limit information
with st.sidebar.expander("ℹ️ Rate Limit Information"):
    st.info("""
    IBM Watson ML APIs have rate limits that vary by service tier:
    - Free tier: ~5 requests per minute
    - Paid tiers: Higher limits based on plan
    
    If you encounter "Too Many Requests" errors, this application will:
    1. Automatically wait and retry
    2. Use caching to avoid repeat requests
    3. Show a progress indicator during wait periods
    
    For best results, space out your requests and avoid rapid submissions.
    """)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📚 Research Prompt", "📄 Summary", "📌 Hypotheses", "🧾 Section Draft"])

with tab1:
    st.subheader("Enter Research Input")
    st.markdown("*Use 'Try Example' to auto-fill sample data*")

    if st.button("🎯 Try Example"):
        abstract = "This paper explores the use of machine learning in predicting climate change impacts on agriculture."
        st.session_state.update({
            'title': "ML for Climate Change",
            'authors': "J. Smith, A. Doe",
            'journal': "AI for Earth",
            'year': 2024,
            'doi': "https://doi.org/10.1234/example",
            'research_q': "How can ML be used to predict agricultural output under climate change?",
            'section_type': "Introduction",
            'section_topic': "Machine Learning Applications in Agriculture"
        })

    abstract = st.text_area("Academic Text or Abstract", value=abstract, height=150)
    title = st.text_input("Title", value=st.session_state.get('title', ''))
    authors = st.text_input("Author(s)", value=st.session_state.get('authors', ''))
    journal = st.text_input("Journal/Source", value=st.session_state.get('journal', ''))
    year = st.number_input("Year", min_value=1900, max_value=datetime.now().year, value=st.session_state.get('year', 2023))
    doi = st.text_input("DOI/URL", value=st.session_state.get('doi', ''))
    research_q = st.text_area("Research Question", value=st.session_state.get('research_q', ''))
    section_type = st.selectbox("Section", ["Introduction", "Related Work", "Methodology"], index=["Introduction", "Related Work", "Methodology"].index(st.session_state.get('section_type', "Introduction")))
    section_topic = st.text_input("Topic for Section Draft", value=st.session_state.get('section_topic', ''))

    # Add these status indicators for request monitoring
    with st.expander("🔄 API Status"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Rate Limit Status", "Normal", delta="Available")
        with col2:
            if 'client' in st.session_state:
                client = st.session_state.client
                client.clean_request_tracking()
                st.metric("Requests (Last Minute)", len(client.requests_this_minute), delta=f"{5-len(client.requests_this_minute)} remaining")

    if st.button("🧠 Generate Output"):
        # Prepare the payload for the model - exactly as your template expects
        payload = {
            "text": abstract,
            "metadata": {
                "title": title,
                "authors": authors,
                "journal": journal,
                "year": year,
                "doi": doi
            },
            "research_question": research_q,
            "section": {
                "type": section_type,
                "topic": section_topic
            }
        }
        
        # Send as a user message - your prompt template is already deployed
        messages = [{"role": "user", "content": json.dumps(payload)}]

        try:
            with st.spinner("Generating research insights..."):
                # Use the enhanced client with rate limit handling
                if use_streaming:
                    # Use streaming API
                    try:
                        if not DEPLOYMENT_ID:
                            st.error("Deployment ID is missing. Please check your environment variables.")
                            st.stop()

                        response = st.session_state.client.chat_completion(
                            deployment_id=str(DEPLOYMENT_ID),
                            messages=messages,
                            stream=True
                        )
                        content = handle_streaming_response(response)
                    except Exception as e:
                        st.error(f"Streaming API failed: {str(e)}. Falling back to regular API.")
                        use_streaming = False

                        if not DEPLOYMENT_ID:
                            st.error("Deployment ID is missing. Please check your environment variables.")
                            st.stop()
                        # Fallback to non-streaming
                        response = st.session_state.client.chat_completion(
                            deployment_id=str(DEPLOYMENT_ID),
                            messages=messages,
                            stream=False
                        )
                        content = parse_response(response)
                else:
                    # Use regular API
                    if not DEPLOYMENT_ID:
                        st.error("Deployment ID is missing. Please check your environment variables.")
                        st.stop()
                    response = st.session_state.client.chat_completion(
                        deployment_id=str(DEPLOYMENT_ID),
                        messages=messages,
                        stream=False
                    )
                    content = parse_response(response)
                
                # Store the result
                st.session_state.research_output = content
                
                # Save to Cloud Object Storage
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_{title.replace(' ', '_')[:30]}.json"
                
                success = upload_to_cos(filename, json.dumps(content, indent=2))
                
                if success:
                    st.success(f"✅ Research output generated and saved to Cloud Object Storage as '{filename}'.")
                else:
                    st.warning("✅ Research output generated but could not be saved to Cloud Object Storage.")
                
        except Exception as e:
            error_msg = str(e)
            
            if "429" in error_msg or "Too Many Requests" in error_msg:
                st.error("❌ Rate limit exceeded. The system will automatically retry after waiting.")
                st.info("Tips to avoid rate limits: space out your requests, use smaller inputs, or try again later.")
            else:
                st.error(f"❌ Error: {error_msg}")
                st.error(traceback.format_exc())

with tab2:
    st.subheader("Summary & Citations")
    if st.session_state.research_output:
        if "raw_content" in st.session_state.research_output:
            st.text_area("Raw Response", st.session_state.research_output["raw_content"], height=400)
        else:
            st.markdown("### 📌 Summary")
            for point in st.session_state.research_output.get("summary", []):
                st.markdown(f"- {point}")

            st.markdown("### 📚 Citations")
            citations = st.session_state.research_output.get("citations", {})
            if isinstance(citations, dict):
                for style, citation in citations.items():
                    st.markdown(f"**{style}:** {citation}")
            elif isinstance(citations, str):
                st.markdown(citations)
            else:
                st.markdown("No citations available")


            st.download_button("⬇️ Download Citations JSON", 
                              json.dumps(st.session_state.research_output.get("citations", {}), indent=2), 
                              file_name="citations.json")
    else:
        st.info("Generate research output first.")

with tab3:
    st.subheader("Hypotheses")
    if st.session_state.research_output:
        if "raw_content" in st.session_state.research_output:
            st.info("Please check the Summary tab for the raw response.")
        else:
            st.markdown(st.session_state.research_output.get("hypotheses", "No hypotheses found."))
    else:
        st.info("Generate research output first.")

with tab4:
    st.subheader("Section Draft")
    if st.session_state.research_output:
        if "raw_content" in st.session_state.research_output:
            st.info("Please check the Summary tab for the raw response.")
        else:
            draft = st.session_state.research_output.get("section_draft", "")
            st.text_area("Generated Draft", draft, height=300)
            st.download_button("⬇️ Download Draft", draft, file_name="section_draft.txt")
    else:
        st.info("Generate research output first.")

# Add cache control in the sidebar
st.sidebar.markdown("---")
if st.sidebar.button("🗑️ Clear Cache"):
    request_cache.clear()
    st.sidebar.success("✅ Cache cleared successfully!")
    
# Display cache status
if request_cache:
    st.sidebar.info(f"📊 Cache contains {len(request_cache)} previous requests")

# Add footer with tips
st.markdown("---")
st.markdown("""
**💡 Tips to avoid rate limits:**
- Space out your requests (wait a minute between submissions)
- Use the example first to ensure everything works
- Keep your abstracts concise for faster processing
- Save your outputs to avoid repeating requests
""")
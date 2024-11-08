# GenAI-based Voice-Enabled Data Analyst (VEDA) Tool
Based on Text or Voice prompt, this GenAI Data Analyst tool invokes LLM to generate matplotlib code to facilitate creation of bar charts and graphs for your private data. It enhances the prompt with additional context (RAG) about dataset related meta info, expected response format etc. This uses OpenAI and PineconeDB for LLM and vectorDB respectively.

## Features.
1. Takes voice prompt or text prompt from the user.
2. Augments this user prompt (RAG) with additional context including meta-data info about the user-selected dataset.
3. Sends this context + user prompt to the LLM for code generation.
4. Parses the LLM response using simple XML parser. Response should contain Pandas and Matplotlib code.
5. Edits relevant sections of the Pandas code to create Dataframe(s) using private data.
6. Newly created dataframes with private data are used by Matplotlib to generate Bar Chart/Pie Charts etc.
7. Complete Streamlit App code is generated into file which is then launched to display charts/graphs etc.
8. Tool also seeks human feedback for the quality of charts/graphs based on the prompt.

## Libraries/Technolgies Used
1. App: Streamlit
2. Language: Python
3. Charts/Graphs: Pandas, Matplotlib
4. Model/LLM: OpenAI gpt-4o-mini
5. Framework: LangChain
6. VectorDB: Pinecone DB  (TBD)
7. Embedding Model: text-embedding-ada-002 (Langchain's default OpenAI embedding model)
8. Speech to Text: Speech Recognition module from Google
9. Logger: Loguru
10. Image display: Pillow

## Tool Diagram
![Diagram for Voice-Enabled Data Analyst Tool](docs/diagram-voice-enabled-data-analyst.png)

# Setup Instructions
## If you want to enable Speech2Text functionality (Optional)
    1. Install portaudio
        On Linux (as sudo):
           $ sudo apt-get install portaudio19-dev python-all-dev
        Mac:
           $ brew install portaudio

    2. Then install PyAudio python library
        $ pip install pyaudio

## Install Python libraries
    $ cd <your_folder>/genai-data-analyst
    $ pip install -r requirements.txt

## Setup OpenAI API Key
    a) Create login for OpenAI, and Get **OpenAI API Key**.
    b) This is needed to use OpenAI API to converse with GPT-4o LLM.
        https://platform.openai.com/settings/organization/api-keys

    $ export OPENAI_API_KEY="<OpenAI API Key goes here in double-quotes>"

## Setup Pinecone API Key
    a) Create login for **PineconeDB** (Vector DB), and Get it's API Key.
    b) This is needed to use Pinecone API for updating and querying vector DB to match prompt with the correct dataset.
        https://app.pinecone.io/organizations

    $ export PINECONE_API_KEY="<Pinecone API Key goes here in double-quotes>"

    c) Create Index (aka DB name), and Namespace in PineconeDB with correct dimensions size of the embeddings.
        Index = ik-capstone
        Namespace = meta_ds
        Dimension = 1536             <<< This matches with the default OpenAI Embedding model we use.

        Note: If you want to use different names for Index or Namespace, you need to update src/app_config.py accordingly.

    d) Now you need to initialize VectorDB with dataset related Metadata.
        $ cd <your_folder>/genai-data-analyst
        $ bash ./load_VectorDB.sh

        Note: You should be able check Pinecone's ik-capstone Index to verify if this is initialized.        

## Run the App
    $ cd <your_folder>/genai-data-analyst
    $ bash ./run_app.sh

    Note 1: You can use 'Sales' or 'World_Top_Companies' dataset. Select one of them in the App.
    Note 2: You can provide textual prompt. For example:
            Dataset = Sales
            Prompt = Generate bar-chart for top 5 agents by sales.
    Note 3: After you submit your prompt, you would see a new browser page for the Results showing bar-charts etc.
    Note 4: This behavior of using a new browser page for results is because Streamlit Apps are event-driven, and
        any change causes the entire App to run from start to finish.

# NovelWriter

An AI-powered fiction novel writing assistant that helps authors write, continue, and manage their stories using large language models. NovelWriter provides intelligent story continuation, entity extraction, and knowledge base management for maintaining consistency across your narrative.

## Features

- **AI Story Continuation**: Generate story continuations using LLM-powered completion chains
- **Entity Mining**: Automatically extract and profile entities (characters, locations, events, objects, organizations) from your story text
- **Vector Search**: Find similar entities using ChromaDB vector embeddings
- **Story Management**: Store and load stories from S3
- **Knowledge Base**: Maintain a searchable knowledge base of story entities with detailed profiles
- **Prompt Template Management**: Store and retrieve customizable prompt templates for different novel contexts

## Architecture

NovelWriter is built as a full-stack application with the following components:

### Frontend
- **React 19** with **Vite** for fast development and builds
- **Tailwind CSS** for styling
- **shadcn/ui** components for a modern UI
- Real-time story editing with word count tracking

### Backend
- **FastAPI** webserver providing REST API endpoints
- **AWS Bedrock** integration for LLM inference (DeepSeek v3)
- **ChromaDB** for vector storage and similarity search
- **AWS S3** for story storage
- **DynamoDB** for prompt template management

### Entity Miner (Lambda Function)
- **AWS Lambda** function for asynchronous entity extraction
- Processes story text to extract:
  - Genre determination
  - Entity extraction and classification
  - Detailed entity profiling (Person, Location, Event, Object, Organization)
  - Relationship extraction
- **OpenTelemetry** instrumentation for observability

### Infrastructure
- **Terraform** for infrastructure as code
- **AWS** services:
  - VPC with public and private subnets
  - EC2 instances for hosting services
  - ECR for Docker image storage
  - S3 for story storage
  - DynamoDB for metadata
  - Lambda for serverless processing
  - Application Load Balancer for routing

## Project Structure

```
novelwriter/
├── frontend/              # React frontend application
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── api.js         # API client
│   │   └── App.jsx        # Main application
│   └── package.json
├── backend/
│   ├── webserver/         # FastAPI backend
│   │   ├── main.py        # API endpoints
│   │   └── utils.py       # Utility functions
│   └── lambda/            # Entity miner Lambda function
│       ├── entity_miner.py
│       └── pydantic_models.py
└── infra/
    └── terraform/        # Infrastructure definitions
        ├── main.tf
        ├── networks.tf
        ├── compute.tf
        └── ...
```

## Prerequisites

- **Python 3.12**
- **Node.js** (for frontend development)
- **AWS Account** with appropriate permissions
- **Terraform** (for infrastructure deployment)
- **Docker** (for containerized deployments)
- **AWS CLI** configured with credentials

## Installation

### Backend Setup

1. Create a virtual environment:
```bash
python3.12 -m venv nw_env
source nw_env/bin/activate  
```

2. Install backend dependencies:
```bash
cd backend/webserver
pip install -e .
cd ../lambda
pip install -e .
```

3. Configure AWS credentials and create `config.json` files:
   - `backend/webserver/config.json`
   - `backend/lambda/config.json`

Example config structure:
```json
{
  "aws": {
    "region": "ap-south-1",
    "dynamodb_table": "your-table-name",
    "entity_miner_model_id": "deepseek.v3-v1:0"
  },
  "chroma": {
    "remote": {
      "host": "your-chroma-host",
      "port": 8000
    },
    "default_collection": "novelwriter-entities"
  }
}
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure API endpoint in `src/api.js` to point to your backend.

### Infrastructure Deployment

1. Navigate to the Terraform directory:
```bash
cd infra/terraform
```

2. Configure variables in `terraform.tfvars`:
```hcl
aws-region = "ap-south-1"
aws_access_key = "your-access-key"
aws_secret_key = "your-secret-key"
LOCAL_PUBLIC_IP = "your-public-ip"
```

3. Initialize and apply Terraform:
```bash
terraform init
terraform plan
terraform apply
```

## Usage

### Running Locally

**Backend (FastAPI)**:
```bash
cd backend/webserver
uvicorn main:app --host 0.0.0.0 --port 7000
```

**Frontend (Development)**:
```bash
cd frontend
npm run dev
```

## API Endpoints

### Story Management
- `GET /api/story` - Retrieve a story from S3
- `POST /api/story` - Upload a story to S3

### Entity Management
- `POST /api/entity` - Add an entity manually to ChromaDB
- `GET /api/similar_entities` - Search for similar entities using vector search
- `POST /api/mine_entities` - Extract entities from story text (invokes Lambda)

### Story Generation
- `GET /api/generate` - Generate story continuation using LLM chains

### Templates
- `GET /api/templates` - Retrieve prompt templates from DynamoDB

## Entity Mining Workflow

The entity mining process follows this workflow:

1. **Genre Determination**: Identifies the fiction genre
2. **Entity Extraction**: Extracts named entities and classifies them
3. **Entity Profiling**: Creates detailed profiles for:
   - Persons (with personality, history, motivations, etc.)
   - Locations (with description, history, atmosphere)
   - Events (with causality, sequence, impact)
   - Objects (with physical details, function, provenance)
   - Organizations (with structure, goals, members)
4. **Storage**: Saves profiled entities to ChromaDB for vector search

See `backend/lambda/entity_mining_plan.md` for detailed workflow documentation.

## Configuration

### Environment Variables

- `OTEL_EXPORTER_OTLP_ENDPOINT`: OpenTelemetry collector endpoint (for Lambda)
- AWS credentials via AWS CLI or environment variables

### Config Files

Both `backend/webserver/config.json` and `backend/lambda/config.json` should contain:
- AWS region and service configurations
- ChromaDB connection details
- DynamoDB table names
- Model IDs for LLM inference

## Development

### Code Style

- Python: Uses `ruff` for linting and formatting (configured in `pyproject.toml`)
- JavaScript: Uses ESLint (configured in `frontend/eslint.config.js`)

### Testing

Run linting:
```bash
# Python
ruff check backend/

# JavaScript
cd frontend && npm run lint
```

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please ensure your code follows the project's style guidelines and includes appropriate tests.

## Author

**boundlesslightbringer** (kunae47@gmail.com)

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Uses [LangChain](https://www.langchain.com/) for LLM orchestration
- Vector storage powered by [ChromaDB](https://www.trychroma.com/)
- UI components from [shadcn/ui](https://ui.shadcn.com/)


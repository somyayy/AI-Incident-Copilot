# AI Incident Co-Pilot – Intelligent Incident Response Assistant

AI Incident Co-Pilot is a Generative AI-powered platform that assists Site Reliability Engineers (SREs) and DevOps teams in diagnosing, analysing, and resolving production incidents. By combining Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), and historical incident knowledge, the platform provides root cause analysis, troubleshooting guidance, and automated remediation suggestions in real time.

---

## 🚀 Features

* 🤖 AI-powered incident analysis
* 🔍 Root Cause Analysis (RCA) generation
* 📚 Retrieval-Augmented Generation (RAG) for context-aware responses
* 📑 Similar incident search from historical records
* 💡 Automated troubleshooting recommendations
* 📊 Incident severity classification
* 📝 AI-generated postmortem summaries
* ⚡ REST APIs for incident management
* 📂 Persistent incident history storage
* 🐳 Dockerized deployment

---

## 🛠 Tech Stack

**Backend:** Python, FastAPI
**Generative AI:** LangChain, OpenAI GPT-4 / GPT-4o-mini, Prompt Engineering, Embedding Models
**Database:** PostgreSQL
**Vector Store:** FAISS
**Cache:** Redis
**DevOps:** Docker, GitHub Actions
**Tools:** Git, Postman, PyTest

---

## 📂 Project Structure

```text
AI-Incident-CoPilot/
│
├── app/
│   ├── api/            # FastAPI route handlers
│   ├── services/        # Business logic orchestration
│   ├── rag/              # Embeddings + FAISS retriever
│   ├── llm/               # LangChain LLM client + prompts
│   ├── database/       # SQLAlchemy engine/session
│   ├── models/           # ORM models
│   ├── schemas/         # Pydantic request/response schemas
│   ├── utils/             # Logging etc.
│   └── main.py
│
├── data/
│   ├── incidents/
│   └── knowledge_base/
│
├── embeddings/            # Persisted FAISS index
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
└── README.md
```

---

## ⚙️ System Architecture

```text
                    User
                      │
                      ▼
               FastAPI Backend
                      │
      ┌───────────────┴───────────────┐
      ▼                               ▼
 Prompt Processing              Incident APIs
      │                               │
      ▼                               ▼
Embedding Generation          PostgreSQL Database
      │
      ▼
 FAISS Vector Store
      │
      ▼
Relevant Incident Retrieval
      │
      ▼
 Large Language Model
      │
      ▼
 AI Incident Analysis & RCA
```

---

## 📋 Core Functionalities

**Incident Analysis** — analyse incidents, identify root causes, generate summaries, suggest remediation.
**Knowledge Retrieval** — retrieve similar historical incidents via FAISS similarity search.
**AI Assistance** — explain errors, generate postmortems, answer incident queries.
**Incident Management** — store, categorise by severity, track status, search history.

---

## 🧪 Running the Project

### Option A: Docker (recommended)

```bash
git clone https://github.com/yourusername/AI-Incident-CoPilot.git
cd AI-Incident-CoPilot
cp .env.example .env   # then fill in OPENAI_API_KEY
docker-compose up --build
```

Visit `http://localhost:8000/docs` for interactive API docs.

### Option B: Local virtualenv

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in OPENAI_API_KEY and a local DATABASE_URL
uvicorn app.main:app --reload
```

### Testing

```bash
pytest
```

---

## 📡 API Endpoints

| Method | Endpoint                          | Description                              |
|--------|------------------------------------|-------------------------------------------|
| POST   | `/incidents`                       | Create a new incident                     |
| GET    | `/incidents`                       | List incidents                            |
| GET    | `/incidents/{id}`                  | Get a single incident                     |
| POST   | `/incidents/{id}/analyze`          | Run RAG + LLM root cause analysis         |
| POST   | `/incidents/{id}/postmortem`       | Generate an AI postmortem summary         |

---

## 📈 Example Workflow

```text
Engineer Reports Incident → Incident Stored → Retrieve Similar Cases
    → LLM Generates RCA → Suggest Resolution → Generate Postmortem
```

---

## 🚀 Future Enhancements

* Multi-agent AI collaboration
* Kubernetes log integration
* Grafana and Prometheus integration
* Slack and Microsoft Teams notifications
* Real-time anomaly detection
* Automated runbook execution
* Fine-tuned domain-specific LLM
* Voice-based incident assistant

---

## 👨‍💻 Author

**Somya Das**
Computer Science & Business Systems, BMS College of Engineering

## 📄 License

This project is intended for educational and portfolio purposes.

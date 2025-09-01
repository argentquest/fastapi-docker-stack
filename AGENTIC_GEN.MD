# **Project Specification: Agentic Content Generation Workflow**

## **1\. Project Overview & Goal**

This document outlines the specifications for a project to build and evaluate two implementations of a multi-step, AI-powered blog content generation workflow.

The primary goal is to compare two distinct technical approaches for building agentic AI systems:

* **Approach A: LangGraph** \- Utilizing a stateful graph framework to manage the agent's logic and flow.  
* **Approach B: Google ADK** \- Using Google's Agent Development Kit for enhanced agent orchestration and workflow management.

By building these two versions, we aim to evaluate the developer experience, robustness, and maintainability of each approach.

## **Technical Integration Requirements**

* **Integration**: Both services integrate into existing FastAPI app on port 8001
* **Architecture**: Follow established patterns from existing services in `app/services/`
* **Storage**: Follow comprehensive AI test pattern - database logging, MinIO file storage, Redis caching
* **Frontend**: Update Frontend Claude with new agentic workflow testing interface
* **API Client**: Extend existing API client with new agentic endpoints
* **Comparison**: Side-by-side testing interface to compare both approaches
* **Automation**: Fully automated workflow (AI generates clarifying question answers)

## **2\. Request for LangGraph Developer**

**Project Title:** Agentic Blog Content Generation Workflow

Project Goal:  
To build a multi-step, agentic workflow using LangGraph that guides a user from a vague topic idea to a fully generated, well-structured blog post.  
**Project Setup:**

* **Language:** Python integration with existing FastAPI codebase
* **Service Location:** `app/services/agentic_langgraph_service.py`
* **Routes**: Add endpoints to `app/routes/ai.py` following existing patterns
* **Frontend**: Add new tab to Frontend Claude AI Testing page
* **API Client**: Extend `frontendclaude/utils/api_client.py` with new methods

Core Concept:  
The workflow will function like a specialized content team. We are creating a "Content Creation Agent" composed of three distinct specialist nodes:

1. A **Content Strategist** to clarify intent.  
2. A **Content Architect** to structure the post and identify keywords.  
3. A **Copywriter** to draft the final content based on the architect's blueprint.

Workflow Specification (Nodes):  
You will create a graph with the following three core nodes:  
**1\. Node 1: clarify\_topic**

* **Purpose:** Takes a broad topic from the user and generates clarifying questions.  
* **Process:** Calls the LLM using the following system prompt:  
  You are an expert Content Strategist AI. Your goal is to help users refine a broad blog topic into a specific, actionable idea. Given the user's topic, your task is to generate 3-4 clarifying questions. These questions must help determine the target audience (e.g., beginners, experts), the specific angle or focus (e.g., tools, trends, ethics), and the desired tone (e.g., casual, professional, technical). Do not write the blog post; only provide the clarifying questions.

**2\. Node 2: generate\_outline**

* **Purpose:** Creates a detailed blueprint and SEO strategy for the blog post.  
* **Process:** Calls the LLM using the following system prompt:  
  You are an expert Content Architect and SEO Specialist. Your task is to create a detailed blueprint for a blog post based on the user's refined requirements. Use the provided details to generate a structured outline and a list of SEO keywords. 

  Your output MUST be a single, valid JSON object and nothing else. 

  The JSON object must have two top-level keys: "keywords" (a list of 5-7 relevant SEO keyword strings) and "outline" (an object containing keys for "title", "introduction", "section\_1", "section\_2", "section\_3", and "conclusion").

**3\. Node 3: write\_post**

* **Purpose:** Writes the final, long-form blog content.  
* **Process:** Calls the LLM using the following system prompt:  
  You are a skilled blog writer. Your task is to write a complete, engaging, and well-formatted blog post based on the provided JSON blueprint. Adhere strictly to the "title" and "outline" provided. Write in the specified tone for the target audience. Seamlessly and naturally integrate the provided "keywords" into the text. The final post should be approximately 500-700 words.

**API Endpoints in app/routes/ai.py:**

```python
@router.post("/agentic/langgraph/generate-blog")
async def agentic_langgraph_blog(request: TopicRequest):
    """LangGraph-based blog generation workflow"""
    # Calls agentic_langgraph_service.generate_blog()
    # Follows comprehensive test pattern: database logging, MinIO storage, Redis caching

@router.post("/agentic/comparison/generate-blog") 
async def agentic_comparison_blog(request: TopicRequest):
    """Side-by-side comparison of both approaches"""
    # Calls both services and returns comparison results
```

## **3\. Request for Google ADK Developer**

**Project Title:** Multi-Step Blog Content Generation Workflow

Project Goal:  
To build an agentic workflow using Google's Agent Development Kit (ADK) that orchestrates a sequence of three agent operations to guide from a vague topic to a fully generated blog post.

**Project Setup:**

* **Language:** Python integration with existing FastAPI codebase
* **Service Location:** `app/services/agentic_googleadk_service.py`
* **Routes**: Add endpoints to `app/routes/ai.py` following existing patterns
* **Frontend**: Add to existing Frontend Claude AI Testing page
* **API Client**: Extend `frontendclaude/utils/api_client.py` with new methods

Core Concept:  
The script will function like a specialized content team, with each step handled by a dedicated function. We are creating a "Content Creation Agent" composed of three specialist functions:

1. A **Content Strategist** to clarify intent.  
2. A **Content Architect** to structure the post and identify keywords.  
3. A **Copywriter** to draft the final content based on the architect's blueprint.

Workflow Specification (Functions):  
You will create a primary script that calls the following three functions in order:  
**1\. Function 1: get\_topic\_clarifications(topic: str)**

* **Purpose:** Takes a broad topic from the user and generates clarifying questions.  
* **Process:** Makes an API call to the Gemini model using the following system prompt:  
  You are an expert Content Strategist AI. Your goal is to help users refine a broad blog topic into a specific, actionable idea. Given the user's topic, your task is to generate 3-4 clarifying questions. These questions must help determine the target audience (e.g., beginners, experts), the specific angle or focus (e.g., tools, trends, ethics), and the desired tone (e.g., casual, professional, technical). Do not write the blog post; only provide the clarifying questions.

**2\. Function 2: generate\_post\_outline(user\_answers: dict)**

* **Purpose:** Creates a detailed blueprint and SEO strategy for the blog post.  
* **Process:** Makes a second API call to the Gemini model using the following system prompt. Ensure you enable JSON mode in the API call.  
  You are an expert Content Architect and SEO Specialist. Your task is to create a detailed blueprint for a blog post based on the user's refined requirements. Use the provided details to generate a structured outline and a list of SEO keywords. 

  Your output MUST be a single, valid JSON object and nothing else. 

  The JSON object must have two top-level keys: "keywords" (a list of 5-7 relevant SEO keyword strings) and "outline" (an object containing keys for "title", "introduction", "section\_1", "section\_2", "section\_3", and "conclusion").

**3\. Function 3: write\_final\_post(outline\_json: dict)**

* **Purpose:** Writes the final, long-form blog content.  
* **Process:** Makes a third API call to the Gemini model using the following system prompt:  
  You are a skilled blog writer. Your task is to write a complete, engaging, and well-formatted blog post based on the provided JSON blueprint. Adhere strictly to the "title" and "outline" provided. Write in the specified tone for the target audience. Seamlessly and naturally integrate the provided "keywords" into the text. The final post should be approximately 500-700 words.

**API Endpoints in app/routes/ai.py:**

```python
@router.post("/agentic/googleadk/generate-blog")
async def agentic_googleadk_blog(request: TopicRequest):
    """Google ADK-based blog generation workflow"""
    # Calls agentic_googleadk_service.generate_blog()
    # Follows comprehensive test pattern: database logging, MinIO storage, Redis caching
```

**Frontend Integration:**
- New "Agentic Workflows" tab in Frontend Claude AI Testing page
- Side-by-side comparison interface with LangGraph and Google ADK columns
- Real-time workflow progress display showing each step
- Performance metrics comparison (time, tokens, cost)
- Output comparison (clarifications, outline, final blog post)

## **Implementation Plan**

**Goal:** Build and compare two agentic blog generation workflows side-by-side

### Phase 1: Core Services
1. **Create prompt files in `prompts/` folder**
   - `prompts/content_strategist.txt` - Clarifying questions system prompt
   - `prompts/content_architect.txt` - Outline generation system prompt  
   - `prompts/copywriter.txt` - Final blog writing system prompt
   - `prompts/clarification_answers.txt` - Auto-answer generation prompt

2. **Create `agentic_langgraph_service.py`**
   - 3-node LangGraph workflow: clarify_topic → generate_outline → write_post
   - Load all prompts from prompts/ folder
   - Automated AI-generated answers to clarifying questions
   - State management via LangGraph's built-in state system

3. **Create `agentic_googleadk_service.py`** 
   - 3-step Google ADK agent workflow using same prompts from prompts/ folder
   - Sequential function calls with manual state passing
   - Leverage existing Google ADK agent framework

### Phase 2: API Integration
4. **Add endpoints to `app/routes/ai.py`**
   - `/agentic/langgraph/generate-blog` - LangGraph workflow
   - `/agentic/googleadk/generate-blog` - Google ADK workflow  
   - `/agentic/comparison/generate-blog` - Side-by-side comparison
   - Follow comprehensive test pattern: database + MinIO + Redis

### Phase 3: Frontend Integration
5. **Update Frontend Claude** 
   - New "Agentic Workflows" tab in AI Testing page
   - Side-by-side comparison interface
   - Real-time progress display for each workflow step
   - Performance metrics and output comparison

6. **Extend API client** - Add methods for all new agentic endpoints

**Architecture Pattern:**
- **All system prompts** stored in separate `.txt` files in `prompts/` folder
- Services load prompts at startup for consistent prompt management
- Both LangGraph and Google ADK workflows use identical prompts for fair comparison

**Deliverable:** Working comparison interface to evaluate LangGraph vs Google ADK approaches for multi-step content generation workflows.  

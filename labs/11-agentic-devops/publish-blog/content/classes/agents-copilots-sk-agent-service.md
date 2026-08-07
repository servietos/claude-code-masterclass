---
title: "Implementing Agents and Copilots using Semantic Kernel and Azure AI Agent Service"
date: '2025-05-01T12:00:00+02:00'
lastmod: '2025-05-09T10:15:00+02:00'
showLastmod: true
tags: ['Copilots', 'Agents', 'Semantic Kernel']
---

This in-depth course that takes developers from foundational concepts to advanced multi-agent orchestration using Microsoft's AI ecosystem. The course begins with Azure AI Foundry essentials, covering hubs, projects, and resources while establishing expertise in prompt engineering, GitHub Models, and the Agent-to-Agent (A2A) protocol fundamentals. Students dive deep into Semantic Kernel development, mastering chat completion, multi-modal capabilities, and advanced prompt templating using YAML, Handlebar, and Liquid formats.

The curriculum provides extensive coverage of Semantic Kernel's plugin architecture, including native functions, OpenAPI integrations, and MCP server implementations, alongside Kernel Memory and vector store connectors for RAG solutions. Participants will master both the Semantic Kernel Agent and Process Frameworks, learning to build multi-step task agents with personas while choosing between Orleans and Dapr runtimes. The course emphasizes Azure AI Foundry's multi-agent solutions, teaching students to leverage the Azure AI Agent Service with action tools (code interpreters, function calling) and knowledge tools (file search, Azure AI Search, Bing Grounding).

Advanced topics include orchestrating complex multi-agent solutions, implementing human-in-the-loop patterns, and integrating .NET Aspire for scalable deployments. The final module ensures production readiness through security, monitoring, and evaluation strategies including agent guardrails, risk monitoring, and Azure AI Foundry's governance and observability features. By completion, students will architect and deploy secure, monitored multi-agent systems leveraging the full power of Azure AI Foundry's orchestration capabilities.

Throughout all modules, you'll work with hands-on code samples in both Python and C#, giving you practical experience building production-ready AI agent solutions.

## Module 1: Copilot, Agents & Azure AI Foundry Essentials

### Introduction to Azure AI Foundry

- Overview Copilots and Agent Frameworks in the Microsoft Ecosystem
- Azure AI Foundry: Hubs, Projects and Resources
- Deploy and use Large Language Models (LLM) in Azure AI Foundry
- Introduction to Azure AI Foundry SDK
- Deploy AI Apps using Azure Developer CLI

### Agent Essentials

- Introduction Effective Prompt Engineering
- Introduction to GitHub Models
- Comparing and Prototyping Prompts using GitHub Models
- Retrieval Augmented Generation (RAG) & Agentic Retrieval in Azure AI Search
- Function Calling, Model Context Protocol (MCP)
- Agent2Agent (A2A) Protocol Basics
- Installing Windows AI Foundry
- Windows local MCP support

## Module 2: Develop AI Agents using Azure OpenAI and Semantic Kernel

### Semantic Kernel Basics & Concepts

- Understand the purpose of Semantic Kernel
- Semantic Kernel Components
- Chat History & AI Services Integration
- ChatCompletion and Multi-modal capabilities

### Optimizing Prompts

- Prompt Engineering with Semantic Kernel
- YAML Prompt Templates and Template Formats
- Handlebar Prompt Templates
- Liquid Prompt Templates
- Using Prompty Visual Studio Code Extension

### Implement Plugins for Semantic Kernel

- Understand the purpose of Semantic Kernel plugins
- Learn how to use pre-made plugins
- Planners, Function Calling and Choice Behaviors
- Implement Native Functions using Prompts
- Integrate existing API's using OpenApi Plugins
- Using MCP Servers in Semantic Kernel
- Invocation-, Prompt Render & Invocation Filters

### Kernel Memory & Vector Store Connectors

- Understand the purpose of Kernel Memory
- Semantic Kernel Memory: In-process & Out-of-the-box-Connectors
- Data Model And Embedding Generation
- Kernel Memory & Retrieval Augmented Generation (RAG)

## Semantic Kernel Agent Framework

- Agents Overview
- Completing multi-step tasks with Agents
- Using Personas with Agents
- Implementing Multi Agent Solutions
- Sematic Kernel A2A Integration
- Using .NET Aspire in multi-agent scenarios

## Semantic Kernel Process Framework

- Process Framework Overview
- Core Components and Patterns
- Runtimes: Orleans vs Dapr
- Implementing Human in the Loop

## Module 4: Develop Agents using Azure AI Agent Service

- Introduction to Azure AI Agent Service
- Using Action Tools: Code Interpreter, Function Calling, Azure Functions and OpenAPI Tools
- Using Knowledge Tools: File Search, Azure AI Search and Bing Grounding
- Orchestrate Multi-Agent-Solutions using Semantic Kernel
- Using Agent to Agent (A2A) Protocol
- Azure Agent AI Service & .NET Aspire

## Module 5: Securing, Monitoring and Evaluating Agents

- Agent Guardrails and Data Controls
- Ensuring App Behavior using Evaluations
- Monitoring Risk and Alerts
- Azure AI Foundry Agent Governance and Observability

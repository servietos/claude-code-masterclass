---
title: "Designing & Implementing Cloud Native Applications using Microsoft Azure"
date: '2023-06-01T12:00:00+02:00'
lastmod: '2024-02-15T09:45:00+02:00'
showLastmod: true
tags: ['Azure', 'Cloud Native', '.NET Aspire', 'Dapr']
---

This five days comprehensive workshop guides you through the journey of designing and implementing cloud-native applications using Microsoft Azure's powerful ecosystem.

Learn how to evolve from monolithic architectures to scalable microservices, master containerization with Azure Container Apps, leverage .NET Aspire and Dapr for distributed application development, implement event-driven architectures, and optimize application performance and security.

You'll gain hands-on experience with modern cloud patterns, Azure services integration, and best practices for building resilient, scalable applications in the cloud.

### Introduction to Cloud Native Applications & Cloud Maturity Model

- What are Cloud Native Applications
- Cloud Maturity Model: Monolith vs Microservices Architecture
- Introduction to .NET Aspire: Orchestration, Components, Tooling
- Microservices Communication Patterns
- Container Hosting & DevOps
- Provisioning of Azure Resources using Azure Developer CLI (AZD) & Bicep
- Introduction to Azure Cost Management

### Deploy cloud-native apps using Azure Container Apps (ACA)

- Get started with cloud native apps and containerized deployments
- Configure Azure Container Registry for container app deployments
- Configure a container app in Azure Container Apps
- Configure continuous deployment for container apps
- Secrets, Managed Identities & Service Connectors
- Using Azure App Configuration in Azure Container Apps
- Task Automation using Jobs
- Scale and manage deployed container apps using KEDA (Kubernetes Event Driven Auto-Scaling)
- Stateful Apps using Volume Mounts & Persistent Storage
- Health Probes, Monitoring, Logging & Observability

### Build distributed apps with .NET Aspire

- Introduction to .NET Aspire & Creating Projects
- Use telemetry & service discovery in a .NET Aspire project
- Use databases in .NET Aspire (SQL Server, Cosmos DB, MongoDB, ...)
- Improve performance with a cache in a .NET Aspire project
- Send messages with RabbitMQ / Service Bus in a .NET Aspire project
- Deploy a .NET Aspire solution to Azure Container Apps / Kubernetes

### Stateful Microservices using Azure Functions

- OData, Open API Support and Dependency Injection
- Hosting: Serverless vs Containers
- Environment Variables, Key Vault, and App Configuration
- Using Managed Identities and Service Connector to access Azure Resources
- Durable Functions - Orchestrate Long Running Processes
- Azure Durable Entities, Aggregation & Virtual Actors
- Publishing Azure Functions to Azure Container Apps
- Distributed Tracing in Azure Functions

### NoSQL Data & Event storage using Cosmos DB

- From Relational to NoSQL: Do's and Don’ts
- Partitioning Strategies & Performance Optimization
- Domain Driven Design (DDD) Basics & Bounded Context Pattern
- Using SDKs and Data Api Builder to expose Cosmos DB
-
- Implementing an Event Store using Event Sourcing
- Creating Materialized Views using Materialized Views Builder
- Optimizing Read/Write Performance with Change Feed & CQRS

### Designing and Implementing Message- & Event Driven Apps

- Introduction to Messaging
- Message Types and Channels
- Introduction to Event Driven Architecture (EDA)
- Event Types: Domain-, Integration-, Cloud Events
- Publishing & Subscribing Events using an Event Bus
- Distributed Transactions
- Saga: Orchestration, Choreography
- Common Message Brokers in Azure

### Using Distributed Application Runtime - Dapr

- Introduction to Dapr
- Understanding Dapr Architecture & Building Blocks
- Developer Environment Setup, Debugging & State Management
- Using Dapr Components in Azure Container Apps
- Service Invocation & Bindings
- Pub/Sub Messaging
- Secrets and Configuration
- Azure Functions & Dapr Bindings
- Dapr Actors & Saga
- Observability and Distributed Tracing
- Dapr & .NET Aspire Integration

### Optimizing and Securing Access using Api Management & Application Gateway

- API Management (APIM) Recap
- API Versions and Revisions using Azure Container Apps
- Authenticating to Backend Services
- Understanding Gateway Pattern and Backends for Frontend Pattern (BFF)
- Implement BFF using APIM and GraphQL

### Connecting Real Time Micro Frontends using Event Grid

- Micro Frontends: Introduction & Benefits
- Publish the Shop Micro Frontend to Azure Container Apps
- Event Grid Basics
- Partner Events
- Real-time connected Micro Frontend using Azure Event Grid and SignalR
- Connect the Real Time Kitchen Dashboard
- Connect the Order Status Micro Frontend

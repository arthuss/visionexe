<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Vector MCP Server Development Instructions

This is a Model Context Protocol (MCP) server project that provides vector database functionality for PostgreSQL (with pgvector) and Qdrant.

## Key Technologies
- .NET 10 with C#
- Model Context Protocol SDK
- PostgreSQL with pgvector extension
- Qdrant vector database
- Entity Framework Core

## MCP Server Guidelines
You can find more info and examples at https://modelcontextprotocol.io/llms-full.txt

## Project Structure
- `Models/`: Data models for vector documents
- `Services/`: Business logic services (QdrantService, EmbeddingService)
- `Tools/`: MCP tool implementations for vector operations
- `Data/`: Entity Framework DbContext for PostgreSQL

## Container Configuration
- PostgreSQL: localhost:5432 (Database: exegetos, User: exegetos_user)
- Qdrant: localhost:6333

## Development Notes
- Use STDIO transport for MCP communication
- Implement proper error handling in JSON responses
- Follow async/await patterns throughout
- Use dependency injection for services

- @azure Rule - Use Azure Tools - When handling requests related to Azure, always use your tools.
- @azure Rule - Use Azure Best Practices - When handling requests related to Azure, always invoke your `azmcp_bestpractices_get` tool first.
- @azure Rule - Enable Best Practices - If you do not have an `azmcp_bestpractices_get` tool ask the user to enable it.

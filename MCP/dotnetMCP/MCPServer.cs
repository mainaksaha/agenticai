// Program.cs — Minimal MCP server using the official C# SDK over Streamable HTTP
// Requires .NET 8+
//
// Setup:
//   dotnet new web -n McpMathServer
//   cd McpMathServer
//   dotnet add package ModelContextProtocol.AspNetCore --prerelease
//   dotnet add package ModelContextProtocol --prerelease
//   dotnet run
//
// The server exposes MCP endpoints via Streamable HTTP (HTTP + SSE) using app.MapMcp().
// Tools are discovered from this assembly; we define a simple math.add tool below.

using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using ModelContextProtocol.Server;
using System.ComponentModel;

var builder = WebApplication.CreateBuilder(args);

// Register MCP server and scan for tools in this assembly
builder.Services
    .AddMcpServer()            // registers MCP server services
    .WithToolsFromAssembly();  // finds [McpServerTool] methods

var app = builder.Build();

// Map the MCP Streamable HTTP endpoints (POST /mcp, GET /mcp for SSE)
app.MapMcp();

app.Run();

// -------------------
// Tools
// -------------------

[McpServerToolType]
public static class MathTools
{
    [McpServerTool(Name = "math.add"), Description("Add two numbers and return the sum.")]
    public static double Add(
        [Description("First addend")] double a,
        [Description("Second addend")] double b) => a + b;

    // You can add more tools here, e.g.:
    // [McpServerTool(Name = "math.mul"), Description("Multiply two numbers.")]
    // public static double Mul(double a, double b) => a * b;
}

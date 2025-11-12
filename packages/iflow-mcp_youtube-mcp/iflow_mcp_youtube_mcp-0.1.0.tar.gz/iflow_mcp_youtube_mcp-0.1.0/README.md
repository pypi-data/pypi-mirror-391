# YouTube MCP
[![smithery badge](https://smithery.ai/badge/@Prajwal-ak-0/youtube-mcp)](https://smithery.ai/server/@Prajwal-ak-0/youtube-mcp)

A Model Context Protocol (MCP) server for YouTube video analysis, providing tools to get transcripts, summarize content, and query videos using Gemini AI.

## Features

- 📝 **Transcript Extraction**: Get detailed transcripts from YouTube videos
- 📊 **Video Summarization**: Generate concise summaries using Gemini AI
- ❓ **Natural Language Queries**: Ask questions about video content
- 🔍 **YouTube Search**: Find videos matching specific queries
- 💬 **Comment Analysis**: Retrieve and analyze video comments

## Requirements

- Python 3.9+
- Google Gemini API key
- YouTube Data API key

## Running Locally

### Installing via Smithery

To install youtube-mcp for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@Prajwal-ak-0/youtube-mcp):

```bash
npx -y @smithery/cli install @Prajwal-ak-0/youtube-mcp --client claude
```

### Option 1: Install directly from smithery

[![smithery badge](https://smithery.ai/badge/@Prajwal-ak-0/youtube-mcp)](https://smithery.ai/server/@Prajwal-ak-0/youtube-mcp)

### Option 2: Local setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Prajwal-ak-0/youtube-mcp
   cd youtube-mcp
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e .
   ```

3. Create a `.env` file with your API keys:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   YOUTUBE_API_KEY=your_youtube_api_key
   ```
   
4. Run MCP Server
   ```bash
   mcp dev main.py
   ```
   Navigate to [Stdio](http://localhost:5173)

   OR

6. Go cursor or windsurf configure with this json content:
   ```json
   {
     "youtube": {
       "command": "uv",
       "args": [
         "--directory",
         "/absolute/path/to/youtube-mcp",
         "run",
         "main.py",
         "--transport",
         "stdio",
         "--debug"
       ]
     }
   }
   ```

## Available Tools

- `youtube/get-transcript`: Get video transcript
- `youtube/summarize`: Generate a video summary
- `youtube/query`: Answer questions about a video
- `youtube/search`: Search for YouTube videos
- `youtube/get-comments`: Retrieve video comments
- `youtube/get-likes`: Get video like count

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

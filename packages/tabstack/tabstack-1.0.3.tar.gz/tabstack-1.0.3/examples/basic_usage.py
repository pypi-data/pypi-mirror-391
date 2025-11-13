"""Example usage of TABStack AI SDK."""

import asyncio
import os

from tabstack import TABStack


async def main():
    """Run all examples."""
    # Initialize the client with connection pooling
    async with TABStack(
        api_key=os.getenv("TABSTACK_API_KEY", "your-api-key-here"),
        max_connections=50,
        max_keepalive_connections=10,
    ) as tabs:
        # Example 1: Extract markdown from a URL
        print("Example 1: Extract Markdown")
        print("-" * 50)
        try:
            result = await tabs.extract.markdown(
                url="https://example.com/blog/article", metadata=True
            )
            print(f"URL: {result.url}")
            print(f"Title: {result.metadata.title if result.metadata else 'N/A'}")
            print(f"Content preview: {result.content[:100]}...")
        except Exception as e:
            print(f"Error: {e}")

        print("\n")

        # Example 2: Generate schema from URL
        print("Example 2: Generate Schema")
        print("-" * 50)
        try:
            result = await tabs.extract.schema(
                url="https://news.ycombinator.com",
                instructions="extract top stories with title, points, and author",
            )
            # result.schema is a JSON Schema dict that can be used directly
            print(f"Generated schema: {result.schema}")
            # You can now use this schema directly with extract.json()
            # data = await tabs.extract.json(
            #     url="https://news.ycombinator.com", schema=result.schema
            # )
        except Exception as e:
            print(f"Error: {e}")

        print("\n")

        # Example 3: Extract structured JSON data
        print("Example 3: Extract Structured JSON")
        print("-" * 50)
        try:
            schema = {
                "type": "object",
                "properties": {
                    "stories": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "points": {"type": "number"},
                                "author": {"type": "string"},
                            },
                        },
                    }
                },
            }

            result = await tabs.extract.json(url="https://news.ycombinator.com", schema=schema)
            print(f"Extracted data: {result.data}")
        except Exception as e:
            print(f"Error: {e}")

        print("\n")

        # Example 4: Generate transformed content with AI
        print("Example 4: Generate Transformed Content")
        print("-" * 50)
        try:
            summary_schema = {
                "type": "object",
                "properties": {
                    "summaries": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "category": {"type": "string"},
                                "summary": {"type": "string"},
                            },
                        },
                    }
                },
            }

            result = await tabs.generate.json(
                url="https://news.ycombinator.com",
                schema=summary_schema,
                instructions="For each story, categorize it (tech/business/science/other) "
                "and write a one-sentence summary",
            )
            print(f"Generated summaries: {result.data}")
        except Exception as e:
            print(f"Error: {e}")

        print("\n")

        # Example 5: Automate web tasks (streaming)
        print("Example 5: Web Automation (Streaming)")
        print("-" * 50)
        try:
            async for event in tabs.automate.execute(
                task="Find the top 3 trending repositories and extract their details",
                url="https://github.com/trending",
                guardrails="browse and extract only, don't interact with repositories",
                max_iterations=20,
            ):
                if event.type == "task:completed":
                    print(f"✓ Task completed: {event.data.get('finalAnswer', 'N/A')}")
                elif event.type == "agent:extracted":
                    print(f"→ Extracted data: {event.data.get('extractedData', 'N/A')}")
                elif event.type == "agent:status":
                    print(f"→ Status: {event.data.get('message', 'N/A')}")
                elif event.type == "error":
                    print(f"✗ Error: {event.data.get('error', 'N/A')}")
                elif event.type == "done":
                    print("✓ Stream completed")
                    break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())

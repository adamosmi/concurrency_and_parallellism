# Concurrency and Parallelism

## Overview

This project, Concurrency and Parallelism, showcases different approaches to concurrency and parallelism in Python, focusing on synchronous vs. asynchronous execution, thread-based parallelism, and process-based parallelism. The project includes a startup script to set up a tmux session for an efficient development workflow, highlighting tools and practices for managing Python environments and running/debugging code in a structured manner.

## Directory Structure

- `README.md` - This file.
- `config/`
  - `startup.sh` - A script to set up a tmux session for development, including windows for a Python IDE, REPL, and Git workflow.
- `src/`
  - `async_queue.py` - Demonstrates asynchronous queue management with asyncio.
  - `sleep_4_ways.py` - Compares different methods of implementing sleep to showcase synchronous, threading, multiprocessing, and asyncio approaches.
  - `sync_vs_async_requests.py` - Compares synchronous and asynchronous HTTP requests.

## Getting Started

### Prerequisites

- Python 3.8+
- tmux
- Requests library for Python
- aiohttp library for Python

To install the required Python libraries, run:

```bash
pip install requests aiohttp
```

### Setup

Clone the repository to your local machine:

```bash
git clone <repository-url>
cd <repository-path>
```

### Running the Startup Script

Before running the `startup.sh` script, make sure you have tmux installed on your system. To start the development environment, navigate to the project's root directory and execute:

```bash
./config/startup.sh
```

This script initializes a tmux session with predefined windows for code editing, a REPL for interactive Python sessions, and a window for Git operations. If the session named "cp" already exists, it attempts to attach to it; otherwise, it creates a new session according to the script's configuration.

### Script Details

- **Python IDE Window**: Opens Neovim with the `sync_vs_async_requests.py` file loaded.
- **REPL Window**: Sets up a Python REPL for interactive testing.
- **Git Workflow Window**: Configures `lazygit` with the specified GitHub username for efficient Git operations.

### Exploring the Source Code

- `async_queue.py`: Explore how asyncio can be used to manage a queue asynchronously, showcasing producer and consumer patterns.
- `sleep_4_ways.py`: This script illustrates four ways to implement sleep in Python: synchronously, using asyncio, threading, and multiprocessing. It serves as a practical comparison of concurrency and parallelism techniques.
- `sync_vs_async_requests.py`: Demonstrates the performance difference between synchronous and asynchronous HTTP requests by fetching URLs in both modes.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues to discuss potential improvements or features.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

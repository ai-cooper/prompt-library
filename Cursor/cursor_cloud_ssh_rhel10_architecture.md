# Cursor on Mac + SSH to RHEL10 (ASCII)

```
                                       +----------------------------------------------+
                                       |      LLM Providers (Inference Backends)      |
                                       |  Fireworks / Anthropic / OpenAI / Google     |
                                       +---------------------+------------------------+
                                                             ^
                                                             |
                                            (3) AI requests/responses to/from LLM providers
                                                             |
                                                             v
+------------------------------------------------------------------------------------------------+
|                                  Cursor Cloud (AWS Infrastructure)                             |
|                                                                                                |
|  - Builds prompts (context assembly)                                                           |
|  - Receives code snippets, viewed files, chat history                                          |
|  - Runs custom models on Fireworks                                                             |
|  - Handles ALL AI routing				                                         |
|                                                                                                |
|  +---------------------------+      +--------------------------------------------------------+ |
|  | Prompt Builder            | ---> |  AI Router / Load Balancer                             | |
|  +---------------------------+      +--------------------------------------------------------+ |
|               ^                                                                                |
|               | (2) Code, context, files,       			                         |
|               |     conversation history                                                       |
+---------------+--------------------------------------------------------------------------------+
                ^
                | (1) Cursor Client sends keystrokes, chat prompts, file context
                | (4) AI Responses from Cursor Cloud
                v
+------------------------------------------------------------------------------------------------+
|                                     My Mac (Cursor Client)                                   |
|                                                                                                |
|   +--------------------------------+        +-----------------------------------------------+  |
|   | Cursor Editor / Chat / UI      |        | SSH Extension (Remote Terminal to RHEL10)     |  |
|   | - Sends AI requests on         |        +-------------------------+---------------------+  |
|   |   every keystroke              |                                  ^                        |
|   | - Sends recently viewed files  |                                  | (7) Command output     |
|   | - Sends conversation history   |                                  |   from RHEL10          |
|   +--------------------------------+                                  |                        |
|                                                                       v                        |
+---------------------+-----------------------------------------------+-------------------------+
                      ^
                      | (5) Encrypted SSH Connection with commands
                      v
        +---------------------------------------------------------------+
        |                         RHEL10 Linux Server                   |
        |                                                               |
        |   +--------------------+      +-----------------------------+ |
        |   |  sshd (daemon)     | ---> | Shell / bash                | |
        |   +---------+----------+      +--------------+--------------+ |
        |             |                                                 |
        |             | (6) Execute AI-generated                        |
        |             |     commands                                    |
        |             |                                                 |
        |     +-------+-------------+                                   |
        |     | Linux Tools:        |                                   |
        |     | - eBPF / BCC        |                                   |
        |     | - bpftrace / perf   |                                   |
        |     +---------------------+                                   |
        |                                                               |
        |                       (7) Command output back                 |
        +---------------------+------------------------+----------------+

```

# House Hunt

## Description

This is an application that allows users to chat with an Artificial Intelligence (AI), powered by OpenAI's GPT-4o-mini model, to help them find properties to rent or buy in Finland. The AI can help users find properties based on their preferences, such as location, price range, built year, and more. Based on the user's input, the AI will generate a list of properties that match the user's criteria and provide additional information about each property. The user can then, for example, provide personal information to the chat and let the AI recommend the best properties for them.

## Demo

- **Chat with the AI:**

https://github.com/user-attachments/assets/49847c1e-44de-491c-8d77-49db3912e308

## Features

- **Chat application**
  - [x] User interface for chatting with the AI.
  - [x] Properties search based on user preference (e.g., location, price range, living area, building type, building year)
  - [x] Stored chat sessions.
  - [ ] Caching search results.
  - [ ] User authentication.
  - [ ] Load chat sessions.
  - [ ] Monitoring AI performance and usage.
- **Data**
  - [x] Crawling of property data from online sources.
  - [ ] Automatic updating property data.
  - [ ] Fully translated property data.

## Tech Stack

- Client: Python, Streamlit
- Server: Python, FastAPI, OpenAI, Langchain
- Database: DynamoDB
- Crawling: Scrapy, Redis

## Getting Started

### Requirements:

- Python version management tool: [pyenv](https://github.com/pyenv/pyenv)

- Python CLI application installer: [pipx](https://github.com/pypa/pipx)

- Python dependency management tool: [poetry](https://python-poetry.org/)

- Justfile: [just](https://github.com/casey/just)

### Installation:

1. Install `just`:

   ```bash
   brew install just
   ```

2. Install `pyenv` and Python 3.10.14 version:

   ```bash
   brew install pyenv
   pyenv install 3.10.14
   pyenv local 3.10.14
   ```

3. Install `pipx`:

   ```bash
   brew install pipx
   ```

4. Install `poetry` and project dependencies:

   ```bash
   pipx install poetry
   poetry env use 3.10.14
   poetry install --no-root
   ```

5. Copy the `.env.example` files in the following directories and rename them to `.env`:

   - `backend/.env.example`
   - `platform/dynamodb/.env.example`
   - `platform/redis/.env.example`

Then add the OpenAI API key to the `OPENAI_API_KEY` variable in the `backend/.env` file.

### Running the application:

> **Note:**
>
> - To run both the backend and the frontend in development, you need to have two terminal windows/tabs and run them each in a separate terminal.

**Run the backend in development:**

```bash
just dev-backend
```

**Run the frontend in development:**

```bash
just dev-frontend
```

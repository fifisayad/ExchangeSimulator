# Exchange Simulator

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Exchange Simulator is an advanced simulation platform designed to model core functionalities of a financial exchange. It includes a matching engine and portfolio management components, making it a valuable tool for quantitative researchers, algorithmic traders, and developers interested in exchange infrastructure.

---

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [PostgreSQL Setup](#postgresql-setup)
  - [Docker Compose Usage](#docker-compose-usage)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- 🚀 **Matching Engine** — Simulates real-time order matching for efficient trade execution.
- 📊 **Portfolio Management** — Tracks and manages simulated user portfolios based on executed trades.
- 🔄 **Exchange Data Integration** — Utilizes realistic or synthetic exchange data for accurate testing.
- 🧩 **Modular Design** — Easily extend or integrate new components for custom workflows.
- 🧪 **Research & Testing Friendly** — Suitable for development, backtesting, and academic research.
- 🛢️ **PostgreSQL Support** — Store exchange and portfolio data persistently using PostgreSQL.

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- PostgreSQL 13 or higher _(local or via Docker)_
- (Optional) [pipenv](https://pipenv.pypa.io/en/latest/) or `venv` for virtual environments
- (Optional) [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) for containerized deployment

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/fifisayad/ExchangeSimulator.git
   cd ExchangeSimulator
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   The following dependencies are required to connect to and use PostgreSQL:

   ```text
   psycopg2-binary
   sqlalchemy
   ```

   These should be listed in your `requirements.txt`. If not, add them:

   ```bash
   pip install psycopg2-binary sqlalchemy
   ```

---

### PostgreSQL Setup

1. **Local PostgreSQL installation:**  
   Install PostgreSQL by following the [official instructions](https://www.postgresql.org/download/), create a database (e.g., `exchange_simulator`), and update your project’s configuration to include:
   - `DB_HOST`
   - `DB_PORT`
   - `DB_USER`
   - `DB_PASSWORD`
   - `DB_NAME`

2. **Or, use Docker Compose as described below.**

---

## Usage

1. **Configure simulation parameters and database connection** in your config files or environment.
2. **Run the main simulation script** (locally):

   ```bash
   python main.py
   ```

   Or inside Docker Compose:

   ```bash
   docker-compose up
   ```

3. **Review the simulation outputs** for exchange activities and portfolio analytics.

_For detailed usage guides and tutorial notebooks, see the [Documentation](#documentation) section below._

---

## Project Structure

```
ExchangeSimulator/
├── data/               # Exchange data samples and synthetic generators
├── engine/             # Core matching engine code
├── portfolio/          # Portfolio management logic
├── tests/              # Unit tests and simulation scenarios
├── utils/              # Utility functions and helpers
├── requirements.txt    # Python dependencies (includes psycopg2-binary, sqlalchemy)
├── Dockerfile          # Container build definition (if present)
├── docker-compose.yml  # Sample compose file for Dockerized workflow
└── main.py             # Entry point for the simulator
```

---

## Documentation

Comprehensive documentation including architecture details, component walkthroughs, and setup instructions can be found here:

👉 **[Exchange Simulator — Full Documentation (Notion)](https://cream-scarf-445.notion.site/Exchange-Simulator-23dd87f6fe3d8052884ac6df06df45e4)**

Please consult this for design rationale, API reference, and advanced usage.

---

## Contributing

Contributions are welcome! Please open issues or submit pull requests for feature requests, bug fixes, or improvements.

1. Fork this repo
2. Create your feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -am 'Add awesome feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## License

Distributed under the MIT License. See `LICENSE` for more information.

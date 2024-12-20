# METL (Metadata Embedding and Tracking Ledger)

METL is a robust and versatile experimental tool for embedding, encrypting, signing, and verifying metadata within various file formats. By leveraging sidecar files, cryptographic security, and Role-Based Access Control (RBAC), METL ensures the integrity, authenticity, and confidentiality of your metadata.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Embedding Metadata](#embedding-metadata)
  - [Verifying Metadata](#verifying-metadata)
- [User Tokens and RBAC](#user-tokens-and-rbac)
- [Security Features](#security-features)
- [Testing](#testing)
- [Benchmarking](#benchmarking)
- [License](#license)

## Features

- **Metadata Embedding:** Embed metadata into files using sidecar JSON files.
- **Encryption:** Protect sensitive metadata with AES-256-GCM.
- **Digital Signing:** Ensure metadata authenticity via Ed25519 signatures.
- **RBAC:** Manage permissions with role-based user tokens.
- **Auditability:** Maintain a ledger of all metadata operations.
- **Multi-Format Support:** Adapters for PDF, DOCX, JPEG, PNG, and more.
- **CLI & GUI:** Use METL from the command line or a graphical interface.
- **CI/CD:** Automated pipelines for testing and deployment.
- **Extensibility:** Easily integrate new file formats and systems.

## Prerequisites

- **Operating System:** Linux, macOS, or Windows
- **Python:** 3.8 or higher
- **Pip:** Python package installer
- **Git:** Optional, recommended

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/metl.git
   cd metl
   ```

2. **Set Up a Virtual Environment (recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Install METL in Editable Mode**
   ```bash
   pip install -e .
   ```

## Configuration

1. **Encryption Configuration**
   - Use `configs/encryption.example.yml` as a template and rename it to `encryption.yml`.
   - Store sensitive keys and secrets in environment variables, then reference them in the YAML.

2. **RBAC Configuration**
   - Edit `src/utils/auth.py` to manage user tokens and roles.

## Usage

### Embedding Metadata
```bash
metl embed <file_path> --policy <policy_name> --token <user_token>
```
Example:
```bash
metl embed examples/sample_files/test.jpg --policy gdpr --token carol-token
```

### Verifying Metadata
```bash
metl verify <file_path> --token <user_token>
```
Example:
```bash
metl verify examples/sample_files/test.jpg --token bob-token
```

## User Tokens and RBAC

User tokens control access rights. Edit `USER_DATABASE` in `src/utils/auth.py` to add new users.

## Security Features

- **Encryption (AES-256-GCM)**
- **Digital Signing (Ed25519)**
- **RBAC**
- **Audit Ledger**
- **Key Management via KMS (mock or integrate with real providers)**

## Testing

Run tests with coverage:
```bash
pytest --cov=src --cov-report=term-missing
```

## Benchmarking

Run benchmarking scripts:
```bash
python3 benchmark.py
```

## License

This project is licensed under the MIT License.

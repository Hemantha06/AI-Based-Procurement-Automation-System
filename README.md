# AI-Based-Procurement-Automation-System

This project implements a **multi-agent AI system** using [Agno AI](https://github.com/agnos-ai/agnos) and OpenAI’s GPT-4 to automate the procurement process for enterprise buyers. Each agent in the system is responsible for a specific part of the procurement workflow, and they collaborate as a **Procurement Team**.

---

## Features

- Modular agent design using `Agno AI`
- Four specialized agents:
  - Requirement Fetcher
  - Item Fetcher
  - Quotation Fetcher
  - Vendor Evaluator
- SQL Server database integration
- Intelligent vendor evaluation using OpenAI GPT-4
- Dynamic, sequential task execution with inter-agent coordination

---

## Agent Responsibilities

```
| Agent Name           | Responsibility                                                   | Tool Used                  |
|----------------------|------------------------------------------------------------------|----------------------------|
| Requirement Fetcher  | Fetches procurement terms from the `requirementdetails` table    | `get_requirement_details` |
| Item Fetcher         | Fetches product specifications from the `requirementitems` table | `get_items`               |
| Quotation Fetcher    | Retrieves vendor quotations from the `quotations` table          | `get_quotations`          |
| Vendor Evaluator     | Evaluates and ranks vendors based on buyer requirements          | `evaluate_vendors`        |
```

---

## Example Usage

You can run the system using:
```
python team.py
```

## How it works

- The system **monitors the database** and waits for a new procurement requirement to be added to the `requirementdetails` table.
- Once a new `REQ_ID` is detected, the system **automatically triggers** the multi-agent evaluation pipeline.
- Vendors are scored and accepted/rejected based on dynamic criteria retrieved from the database.

---

## Project Structure

```
.
├── README.md
├── requirements.txt
├── team.py
└── tools
    ├── config.py
    ├── database.py
    ├── evaluate_ai.py
    ├── get_items.py
    ├── get_quotations.py
    └── get_requirement_details.py
```

---

## Configuration

Edit config.py to match your SQL Server setup:
```
SQL_SERVER_CONFIG = {
    "server": "localhost",
    "database": "ProcurementDB",
    "username": "sa",
    "password": "YourStrongPassword",
    "driver": "ODBC Driver 17 for SQL Server"
}
```

---

## Output Format

```
[
  {
    "vendor_id": "VENDOR001",
    "score": 88.5,
    "status": "accepted",
    "reason": "Meets all delivery and pricing requirements"
  },
  {
    "vendor_id": "VENDOR002",
    "score": 64.3,
    "status": "rejected",
    "reason": "Delivery time exceeds the acceptable limit"
  }
]
```








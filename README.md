# State of the Union Web Scraper — Project Report

## Executive Summary

This project is a Python-based web scraping system designed to systematically collect, process, and archive presidential State of the Union addresses from historical records. The scraper extracts speeches dating back to 1790, storing them in both a Microsoft SQL Server database and local text files for analysis and preservation.

---

## 1. What — Project Overview

The State of the Union Web Scraper is a Python application that automates the collection of presidential State of the Union addresses. The system extracts three key data points from each address:

- **President's name** — The delivering president
- **Speech date** — When the address was given
- **Full speech text** — Complete transcript of the address

The scraped data is stored in two formats: a structured Microsoft SQL Server database for querying and analysis, and individual text files for archival and natural language processing tasks.

---

## 2. Why — Project Purpose

- **Historical Archive**: Creates a structured, queryable repository of State of the Union addresses
- **Data Analysis**: Enables statistical analysis of presidential rhetoric over time
- **NLP Research**: Provides clean, structured text data for natural language processing experiments
- **Educational Resource**: Offers accessible historical content for academic study
- **API Foundation**: Serves as a potential backend for applications requiring historical speech data

---

## 3. Who — Stakeholders

**Developer**: Yoga Sundaram Rama Swamy

**Potential Users**:
- Data scientists studying political communication
- Historians analyzing presidential rhetoric
- Students and educators requiring primary source materials
- NLP practitioners seeking high-quality text datasets

---

## 4. When — Temporal Context

- **Data Coverage**: State of the Union addresses from 1790 to present
- **Execution**: On-demand or scheduled periodically to capture new addresses
- **Relevance**: Constitutionally mandated annual reports — valuable for longitudinal studies spanning multiple centuries

---

## 5. Where — Data Sources and Destinations

### Source
- **Website**: https://www.infoplease.com
- **Content**: HTML pages containing transcribed speeches

### Destinations
- **SQL Server**: Database `STATE_UNION_ADDRESSES`, table `ADDRESS_TABLE` with structured columns for president name, date, link, filename, and speech text
- **Local Files**: Individual text files per speech + a combined archive file

---

## 6. Which — Technologies and Tools

| Component | Technology |
|-----------|-----------|
| Language | Python 3.x |
| Database | Microsoft SQL Server |
| HTTP Client | `requests` |
| HTML Parsing | `lxml` (XPath) |
| DB Connector | `pyodbc` |
| URL Handling | `urllib.parse` |
| Date Processing | `datetime` |
| Version Control | Git / GitHub |

---

## 7. How — System Architecture and Workflow

### Flow

1. **Initialization** — Load DB config from environment variables, connect to SQL Server, create database/table if not exists (non-destructive)
2. **Scraping** — Fetch pages with 30s timeout, parse HTML via XPath, extract names/dates/text, 1s rate limiting between requests
3. **Processing** — Clean and normalize text, validate completeness, track broken links
4. **Storage** — Parameterized INSERT queries to SQL Server, write individual + combined text files
5. **Reporting** — Log broken links, print success summary

### Security Features

- **Parameterized SQL queries** — Prevents SQL injection
- **Environment variable config** — Keeps credentials out of source code
- **Request timeouts** — Prevents indefinite hanging
- **Non-destructive DB operations** — `IF NOT EXISTS` prevents accidental data loss
- **Rate limiting** — Respects server resources

---

## Getting Started

### Prerequisites
- Python 3.x
- Microsoft SQL Server instance
- Network access to source website

### Installation

```bash
pip install -r requirements.txt
```

### Configuration (Optional)

Set environment variables to override default database settings:

```bash
export SQL_SERVER='YOUR_SERVER'
export SQL_DATABASE='YOUR_DATABASE'
```

### Usage

```bash
python main.py
```

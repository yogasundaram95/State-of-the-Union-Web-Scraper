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

---

## Demo (No SQL Server Required)

Want to see the scraper in action without setting up SQL Server? Run the standalone demo script:

```bash
python demo.py
```

The demo scrapes 3 historical speeches from [The American Presidency Project (UCSB)](https://www.presidency.ucsb.edu) and saves them to the `sample_output/` directory:

- **George Washington** — January 8, 1790 (First Annual Address)
- **Abraham Lincoln** — December 1, 1862 (Second Annual Message)
- **John F. Kennedy** — January 11, 1962 (State of the Union Address)

### Example Terminal Output

```
$ python demo.py
2026-02-08 02:00:31 [INFO] State of the Union Web Scraper — Demo Mode
2026-02-08 02:00:31 [INFO] Scraping 3 speeches (no SQL Server needed)

2026-02-08 02:00:31 [INFO] Scraping: George Washington (January 8, 1790)
2026-02-08 02:00:33 [INFO] Saved to sample_output/George_Washington_(January_8_1790).txt
2026-02-08 02:00:33 [INFO] Scraping: Abraham Lincoln (December 1, 1862)
2026-02-08 02:00:35 [INFO] Saved to sample_output/Abraham_Lincoln_(December_1_1862).txt
2026-02-08 02:00:35 [INFO] Scraping: John F. Kennedy (January 11, 1962)
2026-02-08 02:00:37 [INFO] Saved to sample_output/John_F._Kennedy_(January_11_1962).txt

======================================================================
DEMO RESULTS SUMMARY
======================================================================

President:  George Washington
Date:       January 8, 1790
Length:     6,670 characters
Saved to:   George_Washington_(January_8_1790).txt
Preview:    Fellow-Citizens of the Senate and House of Representatives...
----------------------------------------------------------------------

President:  Abraham Lincoln
Date:       December 1, 1862
Length:     49,447 characters
Saved to:   Abraham_Lincoln_(December_1_1862).txt
Preview:    Fellow-Citizens of the Senate and House of Representatives...
----------------------------------------------------------------------

President:  John F. Kennedy
Date:       January 11, 1962
Length:     39,351 characters
Saved to:   John_F._Kennedy_(January_11_1962).txt
Preview:    [As delivered in person before a joint session]...
----------------------------------------------------------------------

Total speeches scraped: 3
```

Pre-generated sample files are available in [`sample_output/`](sample_output/).

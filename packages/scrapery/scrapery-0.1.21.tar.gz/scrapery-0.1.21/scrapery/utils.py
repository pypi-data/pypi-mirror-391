# utils.py
import csv
import re
import os
import chardet
import mmap
import ujson as json
import ijson
from chardet import detect
from typing import Any, Optional, Union, Generator, List, Tuple
from urllib.parse import urlparse
import tldextract
from ftfy import fix_text
import sqlite3
import logging
from logging.handlers import RotatingFileHandler
# for mail
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path


import pandas as pd
from .exceptions import FileError, EncodingError, ValidationError


# -------------------------------
# Folder
# -------------------------------

def create_directory(directory_name: str) -> None:
    """
    Creates a directory if it doesn't already exist.

    Args:
    - directory_name (str): The name of the directory to create.

    Returns:
    - None
    """
    try:
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)
    except OSError as error:
        # print(f"Error: {error}")
        pass

# -------------------------------
# String manipulation
# -------------------------------

def standardized_string(string: Optional[str] = None) -> str:
    """
    Standardizes a string by:
    - Replacing `\n`, `\t`, and `\r` with spaces.
    - Removing HTML tags.
    - Replacing multiple spaces with a single space.
    - Stripping leading/trailing spaces.

    Args:
    - string (str, optional): The string to be standardized. Defaults to None.

    Returns:
    - str: The standardized string, or an empty string if input is None.
    """
    old_string = string
    if string is None:
        return ""
    if not isinstance(string, str):
        string = str(string)

    # Fix encoding issues (mojibake)
    try:
        try:
            string = fix_text(string)
        except:
            pass

        string = string.replace("\\n", " ").replace("\\t", " ").replace("\\r", " ")
        string = re.sub(r"<.*?>", " ", string)  # Remove HTML tags
        string = re.sub(r"\s+", " ", string)  # Collapse multiple spaces into one
        string = string.strip()  # Strip leading/trailing spaces
        return string
    except:
        return old_string

def _replace_in_string(text, old, new, count, ignore_case, position):
    """Helper function to replace text safely, with optional position occurrence."""
    if ignore_case:
        pattern = re.compile(re.escape(old), re.IGNORECASE)
    else:
        pattern = re.compile(re.escape(old))

    # Replace only position occurrence
    if position is not None:
        matches = list(pattern.finditer(text))
        if len(matches) < position:
            return text  # position occurrence doesn't exist
        start, end = matches[position - 1].span()
        return text[:start] + new + text[end:]

    # Replace first 'count' occurrences (or all if count=None)
    if count is None:
        return pattern.sub(new, text)
    else:
        return pattern.sub(new, text, count)

def replace_content(content, old="", new="", count=None, ignore_case=False, position=None):
    """
    Safely replace content in a string or file.

    Parameters:
        content     : str or path to a file
        old         : substring to replace (default: "")
        new         : replacement string (default: "")
        count       : max number of occurrences to replace (like str.replace)
        ignore_case : bool - whether to ignore case
        position         : int - replace only the position occurrence (1-based). If None, replace all/count

    Returns:
        str : replaced text (or original content if replacement fails)
    """
    try:
        if old == "":
            print("Warning: 'old' is empty — no replacement performed.")
            return content

        # Read file if content is a path to a file
        if isinstance(content, str) and content.endswith(('.txt', '.md', '.log')):
            with open(content, 'r', encoding='utf-8') as f:
                text = f.read()
            text = _replace_in_string(text, old, new, count, ignore_case, position)
            with open(content, 'w', encoding='utf-8') as f:
                f.write(text)
            return text

        # String content
        elif isinstance(content, str):
            return _replace_in_string(content, old, new, count, ignore_case, position)

        # Convert other types to string
        else:
            text = str(content)
            return _replace_in_string(text, old, new, count, ignore_case, position)

    except Exception as e:
        print(f"Error replacing content: {type(e).__name__} - {e}")
        return content

# -------------------------------
# Input Validation
# -------------------------------

def validate_input(data: Any, data_type: Optional[type] = None) -> None:
    """Validate input data with type checking."""
    if data is None:
        raise ValidationError("Input data cannot be None")
    if isinstance(data, str) and not data.strip():
        raise ValidationError("Input data cannot be empty string")
    if data_type and not isinstance(data, data_type):
        raise ValidationError(f"Input data must be of type {data_type.__name__}")


# -------------------------------
# HTML Normalization
# -------------------------------

_normalize_comments_re = re.compile(r'<!--.*?-->', re.DOTALL)

def normalize_html(html_content: str) -> str:
    """Normalize HTML for faster parsing."""
    html_content = re.sub(r'>\s+<', '><', html_content)
    html_content = html_content.replace('&nbsp;', ' ')
    html_content = _normalize_comments_re.sub('', html_content)
    return html_content


def detect_encoding(data: Union[str, bytes]) -> str:
    """Detect encoding of data efficiently."""
    if isinstance(data, str):
        return 'utf-8'
    result = chardet.detect(data)
    encoding = result.get('encoding') or 'utf-8'
    try:
        data.decode(encoding)
        return encoding
    except (UnicodeDecodeError, LookupError):
        return 'utf-8'

# -------------------------------
# Xpath detection
# -------------------------------

def _detect_selector_method(selector: str) -> str:
    """
    Detect whether the selector is XPath or CSS with more robust rules.
    """
    selector = selector.strip()

    # Strong XPath patterns
    xpath_patterns = [
        r"(^//|^\.//)",         # Starts with '//' or './/'
        r"@",                   # Attribute access
        r"\bcontains\(",        # XPath function
        r"\bstarts-with\(",     # XPath function
        r"text\(\)",            # XPath text node
        r"::",                  # Axis specifier
    ]

    if any(re.search(pattern, selector) for pattern in xpath_patterns):
        return "xpath"

    # Default fallback → CSS
    return "css"
        

def get_base_domain(url: str) -> Optional[str]:
    """
    Extracts the registered base domain from a given URL using tldextract.

    Args:
        url (str): The full URL or hostname.

    Returns:
        Optional[str]: The base domain (e.g., 'example.com', 'example.co.uk'),
                       or None if it cannot be extracted.

    Examples:
        >>> get_base_domain("https://sub.example.co.uk/path")
        'example.co.uk'

        >>> get_base_domain("example.com")
        'example.com'

        >>> get_base_domain("invalid_url")
        None
    """
    if not isinstance(url, str) or not url.strip():
        print("Invalid input: URL must be a non-empty string.")
        return None

    try:
        # Normalize the URL
        parsed_url = urlparse(url.strip())
        netloc = parsed_url.netloc or parsed_url.path  # handle URLs without scheme

        extracted = tldextract.extract(netloc)
        if extracted.domain and extracted.suffix:
            return f"{extracted.domain}.{extracted.suffix}"
        else:
            print(f"Could not extract base domain from: {url}")
            return None
    except Exception as e:
        print(f"Error extracting base domain from URL '{url}': {e}")
        return None


# -------------------------------
# CSV & Excel
# -------------------------------

def read_csv(csv_file_path: str, get_value_by_col_name: Optional[str] = None, filter_col_name: Optional[str] = None,
             inculde_filter_col_values: Optional[List[str]] = None,
             exclude_filter_col_values: Optional[List[str]] = None, sep: str = ",") -> Union[List[str], pd.DataFrame]:
    """
    Reads a CSV file and returns values from a specific column based on various filters.

    Args:
    - csv_file_path (str): Path to the CSV file.
    - get_value_by_col_name (Optional[str]): The column name from which to fetch values.
    - filter_col_name (Optional[str]): The column name to apply filters.
    - inculde_filter_col_values (Optional[List[str]]): List of values to include in the filter.
    - exclude_filter_col_values (Optional[List[str]]): List of values to exclude from the filter.
    - sep (str, optional): The delimiter used in the CSV file. Defaults to "," (comma).

    Returns:
    - Union[List[str], pd.DataFrame]: A list of values if filtering, or the full DataFrame if no filtering.
    """

    if not os.path.exists(csv_file_path):
        print("read_csv: csv_file_path does not exist.")
        return []

    urls = []

    try:
        # Try to read CSV with error handling and the specified separator
        df = pd.read_csv(csv_file_path, header=0, sep=sep, encoding='utf-8', on_bad_lines='skip', dtype=object).fillna(
            "")

        if get_value_by_col_name and filter_col_name:
            # If we are filtering by include values
            if inculde_filter_col_values:
                for value in inculde_filter_col_values:
                    filtered_df = df[df[filter_col_name] == str(value)]
                    urls.extend(filtered_df[get_value_by_col_name].tolist())

            # If we are filtering by exclude values
            elif exclude_filter_col_values:
                for value in exclude_filter_col_values:
                    filtered_df = df[df[filter_col_name] != str(value)]
                    urls.extend(filtered_df[get_value_by_col_name].tolist())

        elif get_value_by_col_name and not filter_col_name:
            # If just getting values from a single column without filters
            urls.extend(df[get_value_by_col_name].tolist())

        elif not get_value_by_col_name and not filter_col_name:
            # If no filters or specific column is provided, return the entire DataFrame
            return df

        else:
            print("========= Arguments are not proper =========")
            return []

    except Exception as e:
        print(f"Error reading CSV: {str(e)}")
        return []

    # Return unique values (set removes duplicates) as a list
    return list(set(urls))


def save_to_csv(data_list: Optional[List[list]] = None, headers: Optional[List[str]] = None,
                output_file_path: Optional[str] = None, sep: str = ",") -> None:
    """
    Saves data to a CSV file. If the file exists, it appends the data; otherwise, it creates a new file.

    Args:
    - data_list (Optional[List[list]], optional): The data to be saved in the CSV file. Defaults to None.
    - headers (Optional[List[str]], optional): The column headers for the CSV file. Defaults to None.
    - output_file_path (Optional[str], optional): The path to the output CSV file. Defaults to None.
    - sep (str, optional): The delimiter used in the CSV file. Defaults to "," (comma).

    Returns:
    - None: This function doesn't return anything. It performs a side effect (writing to a file).
    """
    
    # Get the directory name from the full file path
    dir_name = get_dir_by_path(file_path=output_file_path)
    # Create the directory if it doesn't exist
    create_directory(directory_name=dir_name)

    if data_list and headers and output_file_path:
        try:
            # Check if the file exists
            if os.path.exists(output_file_path):
                # Append data to the file if it exists
                pd.DataFrame(data_list, columns=headers).to_csv(output_file_path, index=False, header=False,
                                                                           sep=sep, encoding="utf-8",
                                                                           quoting=csv.QUOTE_ALL, quotechar='"',
                                                                           mode="a")
            else:
                # Create a new file and write data
                pd.DataFrame(data_list, columns=headers).to_csv(output_file_path, index=False, header=True,
                                                                           sep=sep, encoding="utf-8",
                                                                           quoting=csv.QUOTE_ALL, quotechar='"',
                                                                           mode="w")
        except Exception as e:
            print(f"save_to_csv: {e.__class__} - {str(e)}")
    else:
        missing_args = []
        if data_list is None:
            missing_args.append('data_list')
        if headers is None:
            missing_args.append('headers')
        if output_file_path is None:
            missing_args.append('output_file_path')

        print(f"Data not saved due to missing arguments: {', '.join(missing_args)}")


def save_to_xls(data_list: Optional[List[list]] = None, headers: Optional[List[str]] = None,
                output_file_path: Optional[str] = None) -> None:
    """
    Saves data to an Excel (.xls) file. If the file exists, it appends the data; otherwise, it creates a new file.

    Args:
    - data_list (Optional[List[list]], optional): The data to be saved in the Excel file. Defaults to None.
    - headers (Optional[List[str]], optional): The column headers for the Excel file. Defaults to None.
    - output_file_path (Optional[str], optional): The path to the output Excel file. Defaults to None.

    Returns:
    - None: This function doesn't return anything. It performs a side effect (writing to a file).
    """
    
    # Get the directory name from the full file path
    dir_name = get_dir_by_path(file_path=output_file_path)
    # Create the directory if it doesn't exist
    create_directory(directory_name=dir_name)

    if data_list and headers and output_file_path:
        try:
            # Check if the file exists
            if os.path.exists(output_file_path):
                # If the file exists, load the existing content and append new data
                with pd.ExcelWriter(output_file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                    df = pd.DataFrame(data_list, columns=headers)
                    df.to_excel(writer, index=False, header=False, sheet_name='Sheet1', startrow=writer.sheets['Sheet1'].max_row)
            else:
                # Create a new Excel file and write data
                with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
                    df = pd.DataFrame(data_list, columns=headers)
                    df.to_excel(writer, index=False, header=True, sheet_name='Sheet1')
        except Exception as e:
            print(f"save_to_xls: {e.__class__} - {str(e)}")
    else:
        missing_args = []
        if data_list is None:
            missing_args.append('data_list')
        if headers is None:
            missing_args.append('headers')
        if output_file_path is None:
            missing_args.append('output_file_path')

        print(f"Data not saved due to missing arguments: {', '.join(missing_args)}")


def save_to_db(data_list: Optional[List[list]] = None, headers: Optional[List[str]] = None, output_file_path: str = "data.sqlite", table_name: str = "data", auto_data_type: bool = False) -> None:
    """
    Saves data to an SQLite database. If the table exists, it appends the data; otherwise, it creates a new table.
    Handles type detection, smart appending, automatically adds missing columns with default empty string values.

    Args:
    - data_list (Optional[List[list]]): The data to be saved in the database.
    - headers (Optional[List[str]]): The column headers for the table.
    - output_file_path (str, optional): The path to the SQLite database file. Defaults to "data.sqlite".
    - table_name (str, optional): The name of the table to save data. Defaults to "data".
    - auto_data_type (bool, optional): If True, detect column types automatically. Defaults to False.

    Returns:
    - None
    """
    if data_list is None or headers is None:
        missing_args = []
        if data_list is None:
            missing_args.append('data_list')
        if headers is None:
            missing_args.append('headers')
        print(f"Data not saved due to missing arguments: {', '.join(missing_args)}")
        return

    try:
        # Ensure the directory for the database exists
        dir_name = get_dir_by_path(file_path=output_file_path)
        create_directory(directory_name=dir_name)

        conn = sqlite3.connect(output_file_path)
        cursor = conn.cursor()

        def detect_type(value):
            if isinstance(value, int):
                return "INTEGER"
            elif isinstance(value, float):
                return "REAL"
            else:
                return "TEXT"

        # Check if table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
        table_exists = cursor.fetchone() is not None

        if table_exists:
            # Get existing columns and types
            cursor.execute(f"PRAGMA table_info({table_name})")
            existing_cols_info = cursor.fetchall()  # [(cid, name, type, notnull, dflt_value, pk), ...]
            existing_cols = {col[1]: col[2].upper() for col in existing_cols_info}

            # Automatically add missing columns with default empty string
            missing_cols = [col for col in headers if col not in existing_cols]
            if missing_cols:
                first_row = data_list[0]
                for col in missing_cols:
                    index = headers.index(col)
                    col_type = detect_type(first_row[index]) if auto_data_type else "TEXT"
                    cursor.execute(
                        f'ALTER TABLE {table_name} ADD COLUMN "{col}" {col_type} DEFAULT ""'
                    )
                    existing_cols[col] = col_type

            # Coerce data to match existing types
            if auto_data_type:
                coerced_data = []
                for row in data_list:
                    new_row = []
                    for val, col in zip(row, headers):
                        col_type = existing_cols.get(col, "TEXT")
                        if col_type == "INTEGER":
                            new_row.append(int(val))
                        elif col_type == "REAL":
                            new_row.append(float(val))
                        else:
                            new_row.append(str(val))
                    coerced_data.append(new_row)
                data_list = coerced_data
        else:
            # Create table if it doesn't exist
            first_row = data_list[0]
            if auto_data_type:
                columns_def = ", ".join([f'"{col}" {detect_type(val)} DEFAULT ""' for col, val in zip(headers, first_row)])
            else:
                columns_def = ", ".join([f'"{col}" TEXT DEFAULT ""' for col in headers])
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})")

        # Insert rows
        placeholders = ", ".join(["?" for _ in headers])
        cursor.executemany(f"INSERT INTO {table_name} ({', '.join(headers)}) VALUES ({placeholders})", data_list)

        conn.commit()
        conn.close()
        # print(f"Saved {len(data_list)} rows to '{table_name}' in '{output_file_path}'.")

    except Exception as e:
        print(f"save_to_db: {e.__class__} - {str(e)}")

# -------------------------------
# File handling
# -------------------------------

def list_files(directory: str, extension: Optional[str] = None) -> List[str]:
    """
    List files in a given directory, optionally filtering by file extension.

    :param directory: Path to the directory.
    :param extension: File extension to filter by (e.g., 'pdf'). Default is None (returns all files).
    :return: List of matching file names.
    """
    if extension:
        return [f for f in os.listdir(directory) if f.endswith(f'.{extension.strip(".")}') and os.path.isfile(os.path.join(directory, f))]
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

def get_dir_by_path(file_path: str = None) -> Any:
    directory_path = os.path.dirname(file_path)  # Get the directory path
    return directory_path


def get_file_name_by_path(file_path: str = None) -> Any:
    file_name = os.path.basename(file_path)  # Get the file name
    return file_name

def stream_json_items(file_path: str, key: str = 'item') -> Generator[dict, None, None]:
    with open(file_path, 'rb') as f:
        yield from ijson.items(f, key)


def read_file_content(
    path_to_file: str,
    stream_json: Optional[bool] = None
) -> Union[str, dict, Generator[dict, None, None]]:
    """
    Reads file content with performance optimizations.

    Parameters:
        path_to_file (str): Path to file.
        stream_json (Optional[bool]): Force streaming JSON if True,
                                      force full load if False,
                                      auto-decide if None (default).

    Returns:
        Union[str, dict, Generator]: File content or streamed JSON items.
    """
    large_file_threshold_bytes = 50 * 1024 * 1024  # 50 MB

    if not os.path.isfile(path_to_file):
        raise FileNotFoundError(f"File not found: {path_to_file}")

    file_size = os.path.getsize(path_to_file)
    is_large = file_size >= large_file_threshold_bytes

    # JSON files
    if path_to_file.endswith('.json'):
        # Decide streaming behavior
        do_stream = stream_json if stream_json is not None else is_large

        if do_stream:
            return stream_json_items(path_to_file)
        else:
            with open(path_to_file, 'r', encoding='utf-8') as f:
                return json.load(f)

    # Large text files: mmap
    if is_large:
        with open(path_to_file, 'r+b') as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                return mm.read().decode('utf-8', errors='replace')

    # Small text files: detect encoding and decode
    with open(path_to_file, 'rb') as f:
        file_bytes = f.read()

    encoding = detect_encoding(file_bytes)

    try:
        return file_bytes.decode(encoding)
    except UnicodeDecodeError:
        return file_bytes.decode('utf-8', errors='replace')


# Function to save content to a specified file path
def save_file_content(output_file_path: str = None, content: Any = "", encoding: str = "utf-8", mode: str = "w") -> None:
    if output_file_path is None:
        return

    try:
        # Get the directory name from the full file path
        dir_name = get_dir_by_path(file_path=output_file_path)

        # Get the file name from the full file path
        file_name = get_file_name_by_path(file_path=output_file_path)

        # Create the directory if it doesn't exist
        create_directory(directory_name=dir_name)

        # Rebuild the full output file path (in case the directory was created)
        output_file_path = os.path.join(dir_name, file_name)

        # Open the file in the specified mode and encoding, and save the content
        with open(output_file_path, mode, encoding=encoding) as file:
            if file_name.endswith(".json"):
                if content is None:
                    content = {}
                json.dump(content, file, indent=4)  # Format JSON with an indent of 4 spaces
                print(f"JSON content successfully written to {output_file_path}")
            else:
                if not isinstance(content, str):
                    content = str(content)
                file.write(content)  # Write the provided content to the file
                print(f"Content successfully written to {output_file_path}")

    except Exception as e:
        print(e)

def get_logger(
    name: str,
    log_file: str = "logs/app.log",
    level: int = logging.DEBUG,
    max_bytes: int = 5 * 1024 * 1024,  # 5 MB
    backup_count: int = 5,
    enable_console: bool = True
) -> logging.Logger:
    """Create and return a configured logger."""
    
    # Ensure log directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # Avoid double logging if root logger is configured

    # Check if logger already has handlers to avoid duplicates
    if not logger.handlers:
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # File handler with rotation
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Optional console handler
        if enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

    return logger


def send_email(smtp_server: str, sender_email: str, sender_passwd: str, to_addrs: List[str], subject: str = "No Subject", smtp_port: int = 465, text_body: Optional[str] = "Test Mail", html_body: Optional[str] = None, cc_addrs: Optional[List[str]] = None, bcc_addrs: Optional[List[str]] = None, attachments: Optional[List[Union[str, Path]]] = None ) -> Tuple[bool, str]:
    """
    Send an email securely using SMTP over SSL with To, CC, BCC, and file attachments.
    Supports custom plain text and HTML body.
    Handles errors gracefully and logs them.
    """
    cc_addrs = cc_addrs or []
    bcc_addrs = bcc_addrs or []
    attachments = attachments or []
    messages = []

    # Check if there are any recipients
    if not (to_addrs or cc_addrs or bcc_addrs):
        return False, "No recipients specified. Email not sent."

    # Create the email
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = ", ".join(to_addrs)
    if cc_addrs:
        msg["Cc"] = ", ".join(cc_addrs)

    # Add body (text + HTML)
    alt_part = MIMEMultipart("alternative")
    if text_body:
        alt_part.attach(MIMEText(text_body, "plain"))
    if html_body:
        alt_part.attach(MIMEText(html_body, "html"))
    if not text_body and not html_body:
        alt_part.attach(MIMEText("No content provided.", "plain"))

    msg.attach(alt_part)

    # Attach files
    for file_path in attachments:
        try:
            file_path = Path(file_path)
            if not file_path.is_file():
                messages.append(f"Attachment not found: {file_path}")
                continue

            with open(file_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{file_path.name}"',
            )
            msg.attach(part)
        except Exception as e:
            messages.append(f"Error attaching file {file_path}: {e}")

    # Combine all recipients
    all_recipients = to_addrs + cc_addrs + bcc_addrs

    # Send email securely
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            try:
                server.login(sender_email, sender_passwd)
            except smtplib.SMTPAuthenticationError:
                return False, "Authentication failed. Check your email/password."
            except smtplib.SMTPException as e:
                return False, f"SMTP login failed: {e}"
            try:
                server.sendmail(sender_email, all_recipients, msg.as_string())
                messages.append("Email sent successfully.")
                return True, " | ".join(messages)
            except smtplib.SMTPRecipientsRefused as e:
                messages.append(f"All recipients were refused: {e.recipients}")
                return False, " | ".join(messages)
            except smtplib.SMTPException as e:
                messages.append(f"Failed to send email: {e}")
                return False, " | ".join(messages)

    except smtplib.SMTPConnectError as e:
        messages.append(f"SMTP connection failed: {e}")
        return False, " | ".join(messages)
    except ssl.SSLError as e:
        messages.append(f"SSL error: {e}")
        return False, " | ".join(messages)
    except Exception as e:
        messages.append(f"Unexpected error: {e}")
        return False, " | ".join(messages)    


__all__ = [
    "create_directory",
    "standardized_string",
    "replace_content",
    "get_base_domain",
    "read_csv",
    "save_to_csv",
    "save_to_xls",
    "save_to_db",
    "list_files",
    "get_dir_by_path",
    "get_file_name_by_path",
    "stream_json_items",
    "read_file_content",
    "save_file_content",
    "get_logger",
]

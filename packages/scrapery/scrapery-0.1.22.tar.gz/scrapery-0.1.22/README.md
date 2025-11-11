# 🕷️ scrapery


[![PyPI Version](https://img.shields.io/pypi/v/scrapery)](https://pypi.org/project/scrapery/)
[![Python Versions](https://img.shields.io/pypi/pyversions/scrapery)](https://pypi.org/project/scrapery/)
[![Downloads](https://img.shields.io/pypi/dm/scrapery)](https://pypi.org/project/scrapery/)
![License](https://img.shields.io/badge/License-Free-brightgreen)
[![Documentation Status](https://readthedocs.org/projects/scrapery/badge/?version=latest)](https://scrapery.readthedocs.io/en/latest/?badge=latest)

A blazing fast, lightweight, and modern parsing library for **HTML, XML, and JSON**, designed for **web scraping** and **data extraction**.  
It supports both **XPath** and **CSS** selectors, along with seamless **DOM navigation**, making parsing and extracting data straightforward and intuitive.

📘 **Full Documentation**: [https://scrapery.readthedocs.io](https://scrapery.readthedocs.io)

---

## ✨ Features

- ⚡ **Blazing Fast Performance** – Optimized for high-speed HTML, XML, and JSON parsing  
- 🎯 **Dual Selector Support** – Use **XPath** or **CSS selectors** for flexible extraction  
- 🛡 **Comprehensive Error Handling** – Detailed exceptions for different error scenarios
- 🧩 **Robust Parsing** – Encoding detection and content normalization for reliable results  
- 🧑‍💻 **Function-Based API** – Clean and intuitive interface for ease of use  
- 📦 **Multi-Format Support** – Parse **HTML, XML, and JSON** in a single library
- ⚙️ **Versatile File Management** – Create directories, list files, and handle paths effortlessly
- 📝 **Smart String Normalization** – Clean text by fixing encodings, removing HTML tags, and standardizing whitespace
- 🔍 **Flexible CSV, Excel & Database Handling** – Read, filter, save, and append data
- 🔄 **Efficient JSON Streaming & Reading** – Stream large JSON files or load fully with encoding detection
- 💾 **Robust File Reading & Writing** – Auto-detect encoding, support large files with mmap, and save JSON or plain text cleanly
- 🌐 **URL & Domain Utilities** – Extract base domains accurately using industry-standard parsing
- 🛡 **Input Validation & Error Handling** – Custom validations to ensure reliable data processing



### ⚡ Performance Comparison

The following benchmarks were run on sample HTML and JSON data to compare **scrapery** with other popular Python libraries.


| Library                 | HTML Parse Time | JSON Parse Time |
|-------------------------|----------------|----------------|
| **scrapery**            | 12 ms          | 8 ms           |
| **Other library**       | 120 ms         | N/A            |

> ⚠️ Actual performance may vary depending on your environment. These results are meant for **illustrative purposes** only. No library is endorsed or affiliated with scrapery.


---

## 📦 Installation

```bash
pip install scrapery

# -------------------------------
# HTML Example
# -------------------------------
import scrapery import *

html_content = """
<html>
    <body>
        <h1>Welcome</h1>
        <p>Hello<br>World</p>
        <a href="/about">About Us</a>
        <img src="/images/logo.png">
        <table>
            <tr><th>Name</th><th>Age</th></tr>
            <tr><td>John</td><td>30</td></tr>
            <tr><td>Jane</td><td>25</td></tr>
        </table>
    </body>
</html>
"""

# Parse HTML content
html_doc = parse_html(html_content)

# Pretty print XML
print(prettify(html_doc))

# Get all table rows
rows = select_all(html_doc, "table tr")
print("All table rows:")
for row in rows:
    print(selector_content(row))

# Output
    All table rows:
    NameAge
    John30
    Jane25

# Get first paragraph
paragraph = select_one(html_doc, "p")
print("First paragraph text:", selector_content(paragraph))
# ➜ First paragraph text: HelloWorld

# CSS selector: First <h1>
print(selector_content(html_doc, selector="h1"))  
# ➜ Welcome

# XPath: First <h1>
print(selector_content(html_doc, selector="//h1"))  
# ➜ Welcome

# CSS selector: <a href> attribute
print(selector_content(html_doc, selector="a", attr="href"))  
# ➜ /about

# XPath: <a> element href
print(selector_content(html_doc, selector="//a", attr="href"))  
# ➜ /about

# CSS: First <td> in table (John)
print(selector_content(html_doc, selector="td"))  
# ➜ John

# XPath: Second <td> (//td[2] = 30)
print(selector_content(html_doc, selector="//td[2]"))  
# ➜ 30

# XPath: Jane's age (//tr[3]/td[2])
print(selector_content(html_doc, selector="//tr[3]/td[2]"))  
# ➜ 25

# No css selector or XPath: full text
print(selector_content(html_doc))  
# ➜ Welcome HelloWorld About Us Name Age John 30 Jane 25

# Root attribute (lang, if it existed)
print(selector_content(html_doc, attr="lang"))  
# ➜ None

#-------------------------
# Embedded Data
#-------------------------

html_content = """
<html>
<head>
  <script>
    window.__INITIAL_STATE__ = {
      "user": {"id": 1, "name": "Alice"},
      "isLoggedIn": true
    };
  </script>
</head>
<body></body>
</html>
"""

json_data = embedded_json(page_source=html_content, start_keyword="window.__INITIAL_STATE__ =")
print(json_data)

# Output

{
  "user": {"id": 1, "name": "Alice"},
  "isLoggedIn": True
}


html_with_ldjson = """
<html>
  <head>
    <script type="application/ld+json">
      {
        "@context": "http://schema.org",
        "@type": "Person",
        "name": "Alice"
      }
    </script>
  </head>
</html>
"""

ld_json = embedded_json(page_source=html_with_ldjson, selector = "[type*='application/ld+json']")
print(ld_json)

# Output

[{
  "@context": "http://schema.org",
  "@type": "Person",
  "name": "Alice"
}]

#-------------------------
# DOM navigation
#-------------------------
# Example 1: parent, children, siblings
p_elem = select_one(html_doc,"p")
print("Parent tag of <p>:", parent(p_elem).tag)
print("Children of <p>:", [c.tag for c in children(p_elem)])
print("Siblings of <p>:", [s.tag for s in siblings(p_elem)])

# Example 2: next_sibling, prev_sibling
print("Next sibling of <p>:", next_sibling(p_elem).tag)
h1_elem = select_one(html_doc,"h1")
print("Previous sibling of <p>:", next_sibling(h1_elem))

# Example 3: ancestors and descendants
ancs = ancestors(p_elem)
print("Ancestor tags of <p>:", [a.tag for a in ancs])
desc = descendants(select_one(html_doc,"table"))
print("Descendant tags of <table>:", [d.tag for d in desc])

# Example 4: class utilities
div_html = '<div class="card primary"></div>'
div_elem = parse_html(div_html)
print("Has class 'card'? ->", has_class(div_elem, "card"))
print("Classes:", get_classes(div_elem))

# -------------------------------
# Resolve relative URLs
# -------------------------------
base = "https://example.com"

# Get <a> links
print(absolute_url(html_doc, "a", base_url=base))
# → 'https://example.com/about'

# Get <img> sources
print(absolute_url(html_doc, "img", base_url=base, attr="src"))
# → 'https://example.com/images/logo.png'

# -------------------------------
# XML Example
# -------------------------------

# Parsing XML from a string
xml_content = """<root>
                    <child>Test</child>
                </root>
            """

xml_doc = parse_xml(xml_content)
print(xml_doc)

# Pretty print XML
print(prettify(xml_doc))

# Select all child elements using CSS selector
all_elements = select_all(xml_doc, "child")
print(all_elements)

# Select one child element using XPath selector
child = select_one(xml_doc, "//child")
print(child)

# Extract content from an element
content = selector_content(xml_doc, "child")
print(content)

# Get the parent element of a child
parent_element = parent(child)
print(parent_element)

# Get all children of the root element
children = children(xml_doc)
print(children)

# Find the first child element with a specific tag
child = xml_find(xml_doc, "child")
print(child)

# Find all child elements with a specific tag
children = xml_find_all(xml_doc, "child")
print(children)

# Execute XPath expression
result = xml_xpath(xml_doc, "//child")
print(result)

# Apply XSLT transformation
xslt = """<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:template match="/">
        <html>
            <body>
                <xsl:value-of select="/root/child"/>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>"""

transformed = xml_transform(xml_doc, xslt)
print(prettify(transformed))

# Validate XML against XSD schema
is_valid = xml_validate_xsd(xml_doc, Path("schema.xsd"))
print(is_valid)

# Create a new element and add it to the root
new_element = xml_create_element("newTag", text="This is new", id="123")
xml_add_child(xml_doc, new_element)
print(prettify(xml_doc))

# Set an attribute on an element
xml_set_attr(new_element, "id", "456")
print(prettify(new_element))

# -------------------------------
# JSON Example
# -------------------------------

json_str = '{"user": {"profile": {"name": "Alice"}}}'
data = parse_json(json_str)

# Get first key match
print(json_content(json_str, keys=["name"], position="first"))
# ➜ {'name': 'Alice'}

# Follow nested path
print(json_content(json_str, keys=["user", "profile", "name"], position="last"))
# ➜ Alice

# -------------------------------
# Utility Example
# -------------------------------

1. Create a Directory

from scrapery import create_directory
# Creates a directory if it doesn't already exist.


# Example 1: Creating a new directory
create_directory("new_folder")

# Example 2: Creating nested directories
create_directory("parent_folder/sub_folder")

# ================================================================
2. Standardize a String

from scrapery import standardized_string
# This function standardizes the input string by removing escape sequences like \n, \t, and \r, removing HTML tags, collapsing multiple spaces, and trimming leading/trailing spaces.

# Example 1: Standardize a string with newlines, tabs, and HTML tags
input_string_1 = "<html><body>  Hello \nWorld!  \tThis is a test.  </body></html>"
print("Standardized String 1:", standardized_string(input_string_1))

# Example 2: Input string with multiple spaces and line breaks
input_string_2 = "  This   is   a  \n\n   string   with  spaces and \t tabs.  "
print("Standardized String 2:", standardized_string(input_string_2))

# Example 3: Pass an empty string
input_string_3 = ""
print("Standardized String 3:", standardized_string(input_string_3))

# Example 4: Pass None (invalid input)
input_string_4 = None
print("Standardized String 4:", standardized_string(input_string_4))

================================================================
3. Replace a String

from scrapery import replace_content

text = "posting posting posting"

# Example 1: Replace all occurrences
result = replace_content(text, "posting", "UPDATED")
print(result)
# Output: "UPDATED UPDATED UPDATED"

# Example 2: Replace only the 2nd occurrence (position)
result = replace_content(text, "posting", "UPDATED", position=2)
print(result)
# Output: "posting UPDATED posting"

# Example 3: Case-insensitive replacement
text = "Posting POSTING posting"
result = replace_content(text, "posting", "edited", ignore_case=True, position=2)
print(result)
# Output: "Posting edited posting"

# Example 4: Limit number of replacements (count)
text = "apple apple apple"
result = replace_content(text, "apple", "orange", count=2)
print(result)
# Output: "orange orange apple"

# Example 5: Replace in a file

# example.txt contains: "error error error"
replace_content("example.txt", "error", "warning", ignore_case=True)
# The file now contains: "warning warning warning"

================================================================
4. Read CSV

from scrapery import read_csv

csv_file_path = 'data.csv'
get_value_by_col_name = 'URL'
filter_col_name = 'Category'
include_filter_col_values = ['Tech']

result = read_csv(csv_file_path, get_value_by_col_name, filter_col_name, include_filter_col_values)
print(result)

Sample CSV

Category,URL
Tech,https://tech1.com
Tech,https://tech2.com
Science,https://science1.com

Result

['https://tech1.com', 'https://tech2.com']

================================================================
5. Save to CSV

from scrapery import save_to_csv

list_data = [[1, 'Alice', 23], [2, 'Bob', 30], [3, 'Charlie', 25]]
headers = ['ID', 'Name', 'Age']
output_file_path = 'output_data.csv'

# Default separator (comma)
save_to_csv(data_list, headers, output_file_path)

# Tab separator
save_to_csv(data_list, headers, output_file_path, sep="\t")

# Semicolon separator
save_to_csv(data_list, headers, output_file_path, sep=";")

Output (default, sep=","):
ID,Name,Age
1,Alice,23
2,Bob,30
3,Charlie,25

Output (sep="\t"):
ID  Name    Age
1   Alice   23
2   Bob 30
3   Charlie 25

================================================================
6. Save to Excel file 

from scrapery import save_to_xls

save_to_xls(data_list, headers, output_file_path)

================================================================
7. Save to sqlite Database

from scrapery import save_to_db

#Creates a SQLite database file named data.sqlite in the current folder and adds a table called data.
save_to_db(data_list, headers)

#Creates a SQLite database file named mydb.sqlite in the given folder (report) and adds a table called User.
save_to_db(data_list, headers, auto_data_type=False, output_file_path="report/mydb.sqlite", table_name="User")

================================================================
8. List files in a directory

from scrapery import list_files

files = list_files(directory=output_dir, extension="csv")
print("CSV files in output directory:", files)

================================================================
9. Read back file content

from scrapery import read_file_content

# Example 1: Read small JSON file fully
file_path_small_json = 'small_data.json'
content = read_file_content(file_path_small_json, stream_json=False)
print("Small JSON file content (fully loaded):")
print(content)  # content will be a dict or list depending on JSON structure

# Example 2: Read large JSON file by streaming (returns a generator)
file_path_large_json = 'large_data.json'
json_stream: Generator[dict, None, None] = read_file_content(file_path_large_json, stream_json=True)
print("\nLarge JSON file content streamed:")
for item in json_stream:
    print(item)  # process each streamed JSON object one by one

# Example 3: Read a large text file using mmap
file_path_large_txt = 'large_text.txt'
text_content = read_file_content(file_path_large_txt)
print("\nLarge text file content (using mmap):")
print(text_content[:500])  # print first 500 characters

# Example 4: Read a small text file with encoding detection
file_path_small_txt = 'small_text.txt'
text_content = read_file_content(file_path_small_txt)
print("\nSmall text file content (with encoding detection):")
print(text_content)

================================================================
10. Save to file

from scrapery import save_file_content

# Example 1: Save plain text content to a file
text_content = "Hello, this is a sample text file.\nWelcome to file handling in Python!"
save_file_content("output/text_file.txt", text_content)

# Output: Content successfully written to output/text_file.txt

# Example 2: Save JSON content to a file
json_content = {
    "name": "Alice",
    "age": 30,
    "skills": ["Python", "Data Science", "Machine Learning"]
}
save_file_content("output/data.json", json_content)

# Output: JSON content successfully written to output/data.json

# Example 3: Save number (non-string content) to a file
number_content = 12345
save_file_content("output/number.txt", number_content)

# Output: Content successfully written to output/number.txt

# Example 4: Append text content to an existing file
append_text = "\nThis line is appended."
save_file_content("output/text_file.txt", append_text, mode="a")

# Output: Content successfully written to output/text_file.txt

================================================================
11. Send mail

from scrapery import send_email

smtp_server = "smtp.gmail.com"  # For Gmail, change if using other services
sender_email = "your_email@gmail.com"  # Replace with the sender's email address
sender_passwd = "your_email_password"  # Replace with the sender's email password (consider using OAuth for security)
to_addrs = ["recipient1@example.com", "recipient2@example.com"]  # List of recipient email addresses
subject = "Test Email with Attachments"
smtp_port = 465  # SMTP port for Gmail SSL
text_body = "Hello, this is a test email."
html_body = "<html><body><h1>Hello, this is a <i>test</i> email.</h1></body></html>"
cc_addrs = ["cc_recipient@example.com"]  # Optional: list of CC recipients
bcc_addrs = ["bcc_recipient@example.com"]  # Optional: list of BCC recipients
attachments = [Path("/path/to/file1.pdf"), Path("/path/to/image.png")]  # Optional: list of file paths to attach

# Call the send_email function
success, message = send_email(
    smtp_server=smtp_server,
    sender_email=sender_email,
    sender_passwd=sender_passwd,
    to_addrs=to_addrs,
    subject=subject,
    smtp_port=smtp_port,
    text_body=text_body,
    html_body=html_body,
    cc_addrs=cc_addrs,
    bcc_addrs=bcc_addrs,
    attachments=attachments
)

# Print the result
print(f"Success: {success}")
print(f"Message: {message}")



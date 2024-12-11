# HyperSnitch

HyperSnitch is a simple web monitoring tool designed to scan websites for specific strings, notifying users when changes occur. It can be used to track registration openings (e.g., for apartment complexes), monitor content updates, or detect specific text on target URLs.

## Features
- **Website Monitoring**: Scan websites at regular intervals to detect specific content or changes.
- **Customizable Alerts**: Get notified when particular strings are found or missing on a website.
- **Flexible Scheduling**: Define scanning intervals and time windows for optimal monitoring.
- **Multiple Scanners**: Set up multiple scanners with individual targets for efficient tracking.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites
- Python 3.10 or higher
- [Poetry](https://python-poetry.org/) for dependency management
- Git
- A STMP relay
- A Digital Ocean API key

### Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/blue-hexagon/HyperSnitch.git ~/hypersnitch
   cd ~/hypersnitch
   poetry install

2. **Create a new .env file**

   Copy the .env.dist to .env and enter in a Digital Ocean API key and your SMTP relay settings.


3. **Add scrapers and scanners** 
     
     Modify the `config.toml` file with relevant information as to what you wish to scrape for, when and how.


4. **Run deployment**
   
    Deploy the application by runnign the deploy script:`python deploy_app.py`

### Example `config.toml`
```toml
[[app.scanner]]
scan_interval = "0:00:00:10"              # Interval between scans - must be specified as: days:hours:minutes:seconds
scan_start = "09:00:00"                   # Time when scanning starts - must be specifed as: hours:minutes:seconds
scan_end = "17:00:00"                     # Time when scanning stops
scanner_id = "scan-between-9-5-every-10s" # Unique identifier for the scanner that you attach to a target

[[app.scanner]]
scan_interval = "0:00:00:30"   
scan_start = "07:00:00"        
scan_end = "20:00:00"          
scanner_id = "scan-between-07-20-every-30s"     


[[app.targets]]
target_id = "PRODUCT_RESTOCK"                              # An ID for internal logic
target_url = "https://example.com/product-page"            # The target URL
target_string = "In Stock"                                 # String to scan for
message_subject = "Product is Back in Stock!"              # Email subject
message_body = "The product you wanted is now available again! Visit https://example.com/product-page."
alert_when_found = true                                    # Send alert when the string is found is enabled
alert_when_not_found = false                               # Send alert when the string is missing is disabled - chose either
scanner_id = "scan-between-07-20-every-30s"                # Link this target to a specific scanner

[[app.targets]]
target_id = "APARTMENT_REGISTRATION"
target_url = "https://example.com/apartment-complex"
target_string = "Open for Registration"
message_subject = "Registration is Now Open!"
message_body = "You can now register for the apartment! Visit https://example.com/apartment-complex."
alert_when_found = true
alert_when_not_found = false
scanner_id = "scan-between-07-20-every-30s"
```
# Web Scraping Project

## Overview
This project aims to scrape data from a dynamic private leasing cars website using Selenium and Selenium Wire in Python. Two scripts have been developed for this purpose, each with its approach to scraping the required data.

## Website Description
The website features a collection of private leasing cars, with each card displaying information such as car manufacturer, model, price, and a hyperlink. The webpage dynamically loads additional cards via a "Load More" button, making traditional scraping methods challenging. Some hyperlinks lead to individual car pages, while others navigate to new pages with additional listings, requiring a recursive scraping approach.

## Challenges
- **Dynamic Content:** The website relies on dynamic loading mechanisms, making it difficult to extract data using traditional scraping techniques.
- **Data Extraction:** Information such as car manufacturer, model, and price are available on the cards, while additional details like fuel type and vehicle chassis require navigation to individual car pages.
- **Load More Button:** The "Load More" button adds more cards to the page dynamically, requiring special handling to ensure all data is captured. It can be bypassed by editing the url to force the page to load with full content.
- **Slow and Error Prone upon Loading Pages:** Must be handled by introducing wait and retry mechanism.
- **Automatic XHR Requests Parsing:** Leveraging XHR requests provides a shortcut to fetch data for multiple pages without navigating to each individual page, but it introduces challenges related to parsing and handling the retrieved data. Multiple Pages each has it's own XHR request need to be scraped while the number of pages vary depending on the scraping time. All that while having to detect, intercept, and scrape all of them with 1 script.
- **Data Consistency:** While the data displayed in XHR requests and on the website may have slight differences, these variations are negligible for scraping purposes.

## Features
- **Selenium Alone Script:** 
  - Scrapes data directly from the website, utilizing regex for extracting information from text.
  - Navigates to individual car pages and handles individual pages with error.
- **Selenium Wire Script:**
  - Utilizes XHR requests to fetch data from multiple pages efficiently.
  - Parses data from XHR responses for faster scraping.
  - Automatically detects XHR requests and it's response.

## Technologies Used
- Python
- Selenium
- Selenium Wire
- Pydantic (for data validation in the Selenium Wire script)
- Pandas (for saving data as csv)
- Fake user agent

## Performance Comparison
So far both script always finish succesfully without missing any data. The Selenium Wire script tends to perform faster due to its ability to fetch data for multiple pages via XHR requests, despite occasional retries. The Selenium alone script provides more consistent runtime but often finishes longer due to navigating individual car pages.

## Data Validation
The Selenium Wire script incorporates data validation using Pydantic to ensure the integrity and correctness of scraped data.

## Known Issues
- Certificate trust issues may lead to varying runtimes in the Selenium Wire script.
- Handling dynamic content and XHR requests may introduce occasional retries.

## Future Improvements
- Address certificate trust issues in the Selenium Wire script for more consistent performance.
- Enhance error handling mechanisms to handle page with new kind of error.

## Contact
Fell free to contact me if you have any questions or feedback! I'll gladly appreciate it!

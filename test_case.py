import requests
from bs4 import BeautifulSoup
import csv
import json
import time
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from collections import defaultdict
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TechnologyScanner:
    def __init__(self, keywords_dict, max_pages_per_domain=5, max_workers=10):
        self.keywords_dict = keywords_dict
        self.max_pages_per_domain = max_pages_per_domain
        self.max_workers = max_workers
        self.results = defaultdict(list)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        # Flatten keywords for faster searching
        self.all_keywords = []
        for category, keywords in self.keywords_dict.items():
            for keyword in keywords:
                self.all_keywords.append((category, keyword.lower()))

    def get_page_content(self, url, timeout=10):
        """Get page content with error handling"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            response = self.session.get(url, timeout=timeout, allow_redirects=True)
            response.raise_for_status()
            return response.text.lower()
        except Exception as e:
            logger.warning(f"Failed to fetch {url}: {str(e)}")
            return None

    def extract_internal_links(self, url, html_content, base_domain):
        """Extract internal links from HTML content"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            links = set()

            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)

                # Only include links from the same domain
                parsed_url = urlparse(full_url)
                if parsed_url.netloc.lower().endswith(base_domain.lower()):
                    # Skip certain file types and fragments
                    if not any(
                            full_url.lower().endswith(ext) for ext in ['.pdf', '.jpg', '.png', '.gif', '.css', '.js']):
                        if '#' in full_url:
                            full_url = full_url.split('#')[0]
                        links.add(full_url)

            return list(links)[:self.max_pages_per_domain]  # Limit number of links
        except Exception as e:
            logger.warning(f"Failed to extract links from {url}: {str(e)}")
            return []

    def scan_page_for_keywords(self, url, content):
        """Scan page content for keywords"""
        found_keywords = []

        for category, keyword in self.all_keywords:
            # Use word boundaries for better matching
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, content):
                found_keywords.append({
                    'category': category,
                    'keyword': keyword,
                    'url': url
                })

        return found_keywords

    def scan_company_domain(self, company_info):
        """Scan a single company domain for keywords"""
        company_name = company_info.get('name', 'Unknown')
        domain = company_info.get('domain', '').strip()

        if not domain:
            logger.warning(f"No domain provided for {company_name}")
            return []

        logger.info(f"Scanning {company_name} - {domain}")

        company_results = []
        visited_urls = set()

        # Start with main domain
        main_url = domain if domain.startswith(('http://', 'https://')) else f"https://{domain}"
        urls_to_check = [main_url]

        for url in urls_to_check:
            if len(visited_urls) >= self.max_pages_per_domain:
                break

            if url in visited_urls:
                continue

            visited_urls.add(url)
            content = self.get_page_content(url)

            if content:
                # Scan for keywords
                found_keywords = self.scan_page_for_keywords(url, content)
                company_results.extend(found_keywords)

                # Extract more links to scan (only on first page to avoid going too deep)
                if url == main_url:
                    try:
                        base_domain = urlparse(url).netloc
                        internal_links = self.extract_internal_links(url, content, base_domain)
                        # Add common pages that might contain technology info
                        priority_paths = ['/about', '/services', '/solutions', '/technology', '/products', '/partners']

                        for path in priority_paths:
                            priority_url = urljoin(main_url, path)
                            if priority_url not in urls_to_check:
                                urls_to_check.insert(1, priority_url)  # Insert near beginning

                        # Add other internal links
                        for link in internal_links:
                            if link not in urls_to_check:
                                urls_to_check.append(link)
                    except Exception as e:
                        logger.warning(f"Failed to process links for {url}: {str(e)}")

            # Small delay to be respectful
            time.sleep(0.5)

        logger.info(f"Completed {company_name}: Found {len(company_results)} keyword matches")
        return {
            'company': company_name,
            'domain': domain,
            'keywords_found': company_results
        }

    def scan_companies(self, companies_list):
        """Scan multiple companies using threading"""
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_company = {
                executor.submit(self.scan_company_domain, company): company
                for company in companies_list
            }

            # Process completed tasks
            for future in as_completed(future_to_company):
                try:
                    result = future.result()
                    if result['keywords_found']:  # Only save companies with findings
                        results.append(result)
                except Exception as e:
                    company = future_to_company[future]
                    logger.error(f"Error processing {company.get('name', 'Unknown')}: {str(e)}")

        return results

    def save_results(self, results, output_file='technology_scan_results.csv'):
        """Save results to CSV file"""
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['company_name', 'domain', 'technology_category', 'keyword', 'page_url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for company_result in results:
                company_name = company_result['company']
                domain = company_result['domain']

                for keyword_info in company_result['keywords_found']:
                    writer.writerow({
                        'company_name': company_name,
                        'domain': domain,
                        'technology_category': keyword_info['category'],
                        'keyword': keyword_info['keyword'],
                        'page_url': keyword_info['url']
                    })

        logger.info(f"Results saved to {output_file}")


# Your keywords dictionary
KEYWORDS_DICT = {
    "SAP": [
        "SAP", "S/4HANA", "SAP Business One", "SAP Business ByDesign",
        "SAP ERP Central Component", "SAP Customer Experience", "SAP Sales Cloud",
        "SAP Edge Services", "SAP HANA"
    ],
    "VMware": [
        "VMware", "VMware vSphere", "vSphere", "vCenter", "VMWare ESX",
        "VMware Horizon", "VMware vSAN", "VMware Infrastructure", "VMware vRealize"
    ],
    "Cloud": [
        "AWS", "Azure", "Microsoft Azure", "GCP", "Google Cloud Platform",
        "Microsoft Cloud", "Google Cloud", "Alibaba Cloud", "IBM Cloud",
        "Ali Cloud", "Amazon Web Services", "Amazon EC2", "Amazon RDS", "Amazon S3",
        "Amazon IAM", "Amazon EBS", "Amazon Lambda", "Amazon EFS", "Amazon CloudFront"
    ]
}


def load_companies_from_csv(file_path):
    """Load companies from CSV file"""
    companies = []
    try:
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                companies.append({
                    'name': row.get('company_name', row.get('name', 'Unknown')),
                    'domain': row.get('domain', row.get('website', ''))
                })
        return companies
    except Exception as e:
        logger.error(f"Error loading companies from {file_path}: {str(e)}")
        return []


def main():
    """Main execution function"""
    # Load companies from your CSV file
    companies_file = 'companies.csv'  # Update this path
    companies = load_companies_from_csv(companies_file)

    if not companies:
        logger.error("No companies loaded. Please check your input file.")
        return

    logger.info(f"Loaded {len(companies)} companies")

    # Initialize scanner
    scanner = TechnologyScanner(
        keywords_dict=KEYWORDS_DICT,
        max_pages_per_domain=3,  # Adjust based on your needs
        max_workers=5  # Adjust based on your system and rate limiting needs
    )

    # Scan companies
    logger.info("Starting technology scan...")
    results = scanner.scan_companies(companies)

    # Save results
    scanner.save_results(results, 'technology_findings_01.csv')

    # Print summary
    total_companies_with_tech = len(results)
    total_keywords_found = sum(len(r['keywords_found']) for r in results)

    print(f"\n=== SCAN COMPLETE ===")
    print(f"Companies with technology keywords: {total_companies_with_tech}")
    print(f"Total keyword matches found: {total_keywords_found}")
    print(f"Results saved to: technology_findings_01.csv")


if __name__ == "__main__":
    main()
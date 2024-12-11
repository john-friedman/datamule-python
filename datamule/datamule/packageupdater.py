import asyncio
import aiohttp
import json
import csv
import os
from pkg_resources import resource_filename
from .helper import headers
from .downloader import PreciseRateLimiter, RateMonitor

class PackageUpdater:
    def __init__(self):
        self.limiter = PreciseRateLimiter(5)  # 5 requests per second
        self.rate_monitor = RateMonitor()
        self.headers = headers
    
    async def _fetch_json(self, session, url):
        """Fetch JSON with rate limiting and monitoring."""
        async with self.limiter:
            try:
                async with session.get(url) as response:
                    response.raise_for_status()
                    content = await response.read()
                    await self.rate_monitor.add_request(len(content))
                    return await response.json()
            except Exception as e:
                print(f"Error fetching {url}: {str(e)}")
                return None

    async def _update_company_tickers(self):
        """Update company tickers data files."""
        url = 'https://www.sec.gov/files/company_tickers.json'
        
        # Define file paths
        json_file = resource_filename('datamule', 'data/company_tickers.json')
        csv_file = resource_filename('datamule', 'data/company_tickers.csv')
        
        # Define temporary file paths
        temp_json_file = json_file + '.temp'
        temp_csv_file = csv_file + '.temp'

        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                data = await self._fetch_json(session, url)
                if not data:
                    raise Exception("Failed to fetch company tickers data")

                # Save the raw JSON file
                with open(temp_json_file, 'w') as f:
                    json.dump(data, f, indent=4)
                
                # Convert to CSV
                with open(temp_csv_file, 'w', newline='') as csvfile:
                    fieldnames = ['cik', 'ticker', 'title']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for _, company in data.items():
                        writer.writerow({
                            'cik': str(company['cik_str']).zfill(10),
                            'ticker': company['ticker'],
                            'title': company['title']
                        })

                # Replace original files
                for src, dst in [(temp_json_file, json_file), (temp_csv_file, csv_file)]:
                    if os.path.exists(dst):
                        os.remove(dst)
                    os.rename(src, dst)

                print(f"Company tickers successfully updated")
                return True

            except Exception as e:
                print(f"Error updating company tickers: {str(e)}")
                return False
            
            finally:
                # Clean up temp files
                for temp_file in [temp_json_file, temp_csv_file]:
                    if os.path.exists(temp_file):
                        try:
                            os.remove(temp_file)
                        except Exception as e:
                            print(f"Warning: Could not remove {temp_file}: {str(e)}")

    async def _process_metadata_batch(self, session, companies, metadata_writer, former_names_writer):
        """Process a batch of companies for metadata updates."""
        metadata_fields = [
            'cik', 'name', 'entityType', 'sic', 'sicDescription', 'ownerOrg',
            'insiderTransactionForOwnerExists', 'insiderTransactionForIssuerExists',
            'tickers', 'exchanges', 'ein', 'description', 'website', 'investorWebsite',
            'category', 'fiscalYearEnd', 'stateOfIncorporation', 'stateOfIncorporationDescription',
            'phone', 'flags', 'mailing_street1', 'mailing_street2', 'mailing_city',
            'mailing_stateOrCountry', 'mailing_zipCode', 'mailing_stateOrCountryDescription',
            'business_street1', 'business_street2', 'business_city', 'business_stateOrCountry',
            'business_zipCode', 'business_stateOrCountryDescription'
        ]

        tasks = []
        for company in companies:
            cik = company['cik']
            url = f'https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json'
            tasks.append(self._fetch_json(session, url))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for company, result in zip(companies, results):
            if isinstance(result, Exception) or not result:
                print(f"Error processing CIK {company['cik']}: {str(result) if isinstance(result, Exception) else 'No data'}")
                continue

            try:
                metadata = {field: result.get(field, '') for field in metadata_fields if field not in ['tickers', 'exchanges']}
                metadata['cik'] = company['cik']
                metadata['tickers'] = ','.join(result.get('tickers', []))
                metadata['exchanges'] = ','.join(result.get('exchanges', []))

                # Add address information
                for address_type in ['mailing', 'business']:
                    address = result.get('addresses', {}).get(address_type, {})
                    for key, value in address.items():
                        metadata[f'{address_type}_{key}'] = value if value is not None else ''

                metadata_writer.writerow(metadata)

                for former_name in result.get('formerNames', []):
                    former_names_writer.writerow({
                        'cik': company['cik'],
                        'former_name': former_name['name'],
                        'from_date': former_name['from'],
                        'to_date': former_name['to']
                    })

            except Exception as e:
                print(f"Error processing metadata for CIK {company['cik']}: {str(e)}")

    async def _update_company_metadata(self):
        """Update company metadata and former names files."""
        metadata_file = resource_filename('datamule', 'data/company_metadata.csv')
        former_names_file = resource_filename('datamule', 'data/company_former_names.csv')
        
        temp_metadata_file = metadata_file + '.temp'
        temp_former_names_file = former_names_file + '.temp'

        # Load current company tickers
        with open(resource_filename('datamule', 'data/company_tickers.csv'), 'r') as f:
            company_tickers = list(csv.DictReader(f))

        metadata_fields = ['cik', 'name', 'entityType', 'sic', 'sicDescription', 'ownerOrg',
                        'insiderTransactionForOwnerExists', 'insiderTransactionForIssuerExists',
                        'tickers', 'exchanges', 'ein', 'description', 'website', 'investorWebsite',
                        'category', 'fiscalYearEnd', 'stateOfIncorporation', 'stateOfIncorporationDescription',
                        'phone', 'flags', 'mailing_street1', 'mailing_street2', 'mailing_city',
                        'mailing_stateOrCountry', 'mailing_zipCode', 'mailing_stateOrCountryDescription',
                        'business_street1', 'business_street2', 'business_city', 'business_stateOrCountry',
                        'business_zipCode', 'business_stateOrCountryDescription']

        former_names_fields = ['cik', 'former_name', 'from_date', 'to_date']

        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                with open(temp_metadata_file, 'w', newline='') as mf, \
                     open(temp_former_names_file, 'w', newline='') as fnf:
                    
                    metadata_writer = csv.DictWriter(mf, fieldnames=metadata_fields)
                    metadata_writer.writeheader()
                    
                    former_names_writer = csv.DictWriter(fnf, fieldnames=former_names_fields)
                    former_names_writer.writeheader()

                    # Process in batches of 10 companies
                    batch_size = 10
                    for i in range(0, len(company_tickers), batch_size):
                        batch = company_tickers[i:i + batch_size]
                        await self._process_metadata_batch(
                            session, batch, metadata_writer, former_names_writer
                        )

            # Replace original files
            for src, dst in [(temp_metadata_file, metadata_file), 
                           (temp_former_names_file, former_names_file)]:
                if os.path.exists(dst):
                    os.remove(dst)
                os.rename(src, dst)

            print("Company metadata successfully updated")
            return True

        except Exception as e:
            print(f"Error updating company metadata: {str(e)}")
            return False

        finally:
            # Clean up temp files
            for temp_file in [temp_metadata_file, temp_former_names_file]:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except Exception as e:
                        print(f"Warning: Could not remove {temp_file}: {str(e)}")

    def update_company_tickers(self):
        """Update company tickers data files."""
        return asyncio.run(self._update_company_tickers())

    def update_company_metadata(self):
        """Update company metadata and former names files."""
        return asyncio.run(self._update_company_metadata())
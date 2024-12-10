    async def _download_company_metadata(self):
        # Define file paths
        metadata_file = resource_filename('datamule', 'data/company_metadata.csv')
        former_names_file = resource_filename('datamule', 'data/company_former_names.csv')
        
        # Define temporary file paths
        temp_metadata_file = metadata_file + '.temp'
        temp_former_names_file = former_names_file + '.temp'
        
        metadata_fields = ['cik', 'name', 'entityType', 'sic', 'sicDescription', 'ownerOrg', 
                        'insiderTransactionForOwnerExists', 'insiderTransactionForIssuerExists', 
                        'tickers', 'exchanges', 'ein', 'description', 'website', 'investorWebsite', 
                        'category', 'fiscalYearEnd', 'stateOfIncorporation', 'stateOfIncorporationDescription', 
                        'phone', 'flags', 'mailing_street1', 'mailing_street2', 'mailing_city', 
                        'mailing_stateOrCountry', 'mailing_zipCode', 'mailing_stateOrCountryDescription', 
                        'business_street1', 'business_street2', 'business_city', 'business_stateOrCountry', 
                        'business_zipCode', 'business_stateOrCountryDescription']
        
        former_names_fields = ['cik', 'former_name', 'from_date', 'to_date']
        
        company_tickers = load_package_csv('company_tickers')
        
        async with aiohttp.ClientSession() as session:
            with open(temp_metadata_file, 'w', newline='') as mf, open(temp_former_names_file, 'w', newline='') as fnf:
                metadata_writer = csv.DictWriter(mf, fieldnames=metadata_fields)
                metadata_writer.writeheader()
                
                former_names_writer = csv.DictWriter(fnf, fieldnames=former_names_fields)
                former_names_writer.writeheader()
                
                for company in tqdm(company_tickers, desc="Updating company metadata"):
                    cik = company['cik']
                    url = f'https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json'
                    
                    try:
                        data = await self._fetch_json_from_url(session, url)
                        
                        metadata = {field: data.get(field, '') for field in metadata_fields if field not in ['tickers', 'exchanges']}
                        metadata['cik'] = cik
                        metadata['tickers'] = ','.join(data.get('tickers', []))
                        metadata['exchanges'] = ','.join(data.get('exchanges', []))
                        
                        # Add address information
                        for address_type in ['mailing', 'business']:
                            address = data.get('addresses', {}).get(address_type, {})
                            for key, value in address.items():
                                metadata[f'{address_type}_{key}'] = value if value is not None else ''
                        
                        metadata_writer.writerow(metadata)
                        
                        for former_name in data.get('formerNames', []):
                            former_names_writer.writerow({
                                'cik': cik,
                                'former_name': former_name['name'],
                                'from_date': former_name['from'],
                                'to_date': former_name['to']
                            })
                    
                    except Exception as e:
                        print(f"Error processing CIK {cik}: {str(e)}")
        
        # Now we can safely replace the original files
        
        try:
            # Remove original files if they exist
            if os.path.exists(metadata_file):
                os.remove(metadata_file)
            if os.path.exists(former_names_file):
                os.remove(former_names_file)
            
            # Rename temp files to original names
            os.rename(temp_metadata_file, metadata_file)
            os.rename(temp_former_names_file, former_names_file)
            
            print(f"Metadata successfully updated in {metadata_file}")
            print(f"Former names successfully updated in {former_names_file}")
        except Exception as e:
            print(f"Error occurred while finalizing file update: {str(e)}")
            print("Temporary files have been kept. Please manually review and rename if necessary.")
            return

        # Clean up temp files if they still exist for some reason
        for temp_file in [temp_metadata_file, temp_former_names_file]:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as e:
                    print(f"Warning: Could not remove temporary file {temp_file}: {str(e)}")

return asyncio.run(self._download_company_metadata())


    async def _download_company_tickers(self):
        url = 'https://www.sec.gov/files/company_tickers.json'
        
        # Define file paths
        json_file = resource_filename('datamule', 'data/company_tickers.json')
        csv_file = resource_filename('datamule', 'data/company_tickers.csv')
        
        # Define temporary file paths
        temp_json_file = json_file + '.temp'
        temp_csv_file = csv_file + '.temp'

        async with aiohttp.ClientSession() as session:
            try:
                content = await self._fetch_content_from_url(session, url)
                
                # Save the raw JSON file
                await self.write_content_to_file(content, temp_json_file)
                
                # Parse the JSON content
                data = json.loads(content)
                
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

                # If everything went well, replace the original files
                if os.path.exists(json_file):
                    os.remove(json_file)
                if os.path.exists(csv_file):
                    os.remove(csv_file)
                
                os.rename(temp_csv_file, csv_file)


                print(f"Company tickers successfully updated in {csv_file}")

            except Exception as e:
                print(f"Error occurred while updating company tickers: {str(e)}")
                print("Temporary files have been kept. Please manually review and rename if necessary.")
                return

            finally:
                # Clean up temp files if they still exist
                for temp_file in [temp_json_file, temp_csv_file]:
                    if os.path.exists(temp_file):
                        try:
                            os.remove(temp_file)
                        except Exception as e:
                            print(f"Warning: Could not remove temporary file {temp_file}: {str(e)}")



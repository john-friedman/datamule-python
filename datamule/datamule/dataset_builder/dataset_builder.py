import pandas as pd
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import google.generativeai as genai
import time
from datetime import datetime
import psutil
from threading import Lock

class RateLimiter:
    def __init__(self, max_rpm):
        self.min_delay = 60.0 / max_rpm
        self.last_request = time.time()
        self.lock = Lock()
        self.request_count = 0
        
    def acquire(self):
        with self.lock:
            now = time.time()
            time_since_last = now - self.last_request
            if time_since_last < self.min_delay:
                time.sleep(self.min_delay - time_since_last)
            
            self.last_request = time.time()
            self.request_count += 1
            return self.request_count

class DatasetBuilder:
    def __init__(self):
        self.base_prompt = None
        self.response_schema = None
        self.input_path = None
        self.output_path = None
        self.failed_path = None
        self.max_rpm = 1450
        self.max_workers = 30
        self.save_frequency = 100
        self.output_columns = None
        self.buffer = []
        self.buffer_lock = Lock()
        self.failed_ids = set()
        self.failed_lock = Lock()
        self.model_name = "gemini-1.5-flash-8b"  # Default model
        self.model_config = {}  # Additional model configuration
        self.api_key = None

    def set_api_key(self, api_key):
        """Set the API key for Google's Generative AI."""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        return self

    def set_paths(self, input_path, output_path, failed_path):
        """Set input and output file paths."""
        self.input_path = input_path
        self.output_path = output_path
        self.failed_path = failed_path
        return self

    def set_base_prompt(self, prompt):
        """Set the base prompt for LLM processing."""
        self.base_prompt = prompt
        return self

    def set_response_schema(self, schema):
        """Set the response schema and derive output columns."""
        self.response_schema = schema
        # Derive output columns from schema
        if schema and 'items' in schema and 'properties' in schema['items']:
            properties = schema['items']['properties']
            self.output_columns = ['accession_number'] + list(properties.keys())
        return self

    def set_rpm(self, max_rpm=1450):
        """Set the maximum requests per minute."""
        self.max_rpm = max_rpm
        return self

    def set_max_workers(self, max_workers=30):
        """Set the maximum number of concurrent workers."""
        self.max_workers = max_workers
        return self

    def set_save_frequency(self, frequency=100):
        """Set how often to save progress."""
        self.save_frequency = frequency
        return self

    def set_model(self, model_name="gemini-1.5-flash-8b", **model_config):
        """Set the model name and configuration."""
        self.model_name = model_name
        self.model_config = model_config
        return self

    def validate_config(self):
        """Validate that all required configurations are set."""
        if not all([self.base_prompt, self.response_schema, self.input_path, 
                   self.output_path, self.failed_path, self.api_key]):
            raise ValueError("""Missing required configuration. Please ensure you have set:
                           - API key
                           - Paths (input_path, output_path, failed_path)
                           - Base prompt
                           - Response schema""")

    def load_existing_data(self):
        """Load existing processed data if available."""
        if os.path.exists(self.output_path):
            return pd.read_csv(self.output_path)
        return pd.DataFrame(columns=self.output_columns)

    def save_data(self, df):
        """Safely save data with backup."""
        if os.path.exists(self.output_path):
            backup_path = f"{self.output_path}.backup"
            os.replace(self.output_path, backup_path)
        
        try:
            df.to_csv(self.output_path, index=False)
            if os.path.exists(f"{self.output_path}.backup"):
                os.remove(f"{self.output_path}.backup")
        except Exception as e:
            if os.path.exists(f"{self.output_path}.backup"):
                os.replace(f"{self.output_path}.backup", self.output_path)
            raise e

    def save_failed_ids(self):
        """Save failed accession numbers to file."""
        with open(self.failed_path, 'w') as f:
            for acc in self.failed_ids:
                f.write(f"{acc}\n")

    def process_text(self, args):
        """Process a single text entry through the model."""
        model, text, accession_number, rate_limiter = args
        
        current_requests = rate_limiter.acquire()
        
        full_prompt = self.base_prompt + "\n\nINFORMATION:\n" + text

        try:
            generation_config = genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=self.response_schema,
                **self.model_config
            )
            
            response = model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            results = json.loads(response.text)
            
            for result in results:
                result['accession_number'] = accession_number
            
            with self.buffer_lock:
                self.buffer.extend(results)
            
            return True, current_requests
        except Exception as e:
            with self.failed_lock:
                self.failed_ids.add(accession_number)
            return False, f"Error processing {accession_number}: {str(e)}"

    def build(self):
        """Main processing method to build the dataset."""
        self.validate_config()

        # Initialize model and rate limiter
        model = genai.GenerativeModel(self.model_name)
        rate_limiter = RateLimiter(self.max_rpm)
        
        # Load data
        print("Loading data...")
        df_input = pd.read_csv(self.input_path)
        df_existing = self.load_existing_data()
        
        processed_ids = set(df_existing['accession_number'])
        df_to_process = df_input[~df_input['accession_number'].isin(processed_ids)]
        
        print(f"Found {len(df_input) - len(df_to_process)} already processed entries")
        print(f"Processing {len(df_to_process)} new entries")
        
        if len(df_to_process) == 0:
            print("All entries already processed!")
            return

        work_items = [
            (model, row['text'], row['accession_number'], rate_limiter) 
            for _, row in df_to_process.iterrows()
        ]
        
        start_time = time.time()
        last_save_time = time.time()
        processed_count = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.process_text, item): item for item in work_items}
            
            with tqdm(total=len(work_items), desc="Processing entries") as pbar:
                for future in as_completed(futures):
                    success, result = future.result()
                    
                    if not success:
                        print(f"\n{result}")
                    
                    processed_count += 1
                    pbar.update(1)
                    
                    elapsed = time.time() - start_time
                    rpm = processed_count / (elapsed / 60)
                    memory_usage = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
                    
                    pbar.set_description(
                        f"Processing: {rpm:.0f} RPM, Mem: {memory_usage:.0f}MB"
                    )
                    
                    # Save periodically
                    if (len(self.buffer) >= self.save_frequency or 
                        time.time() - last_save_time > 300):
                        
                        if self.buffer:
                            with self.buffer_lock:
                                df_new = pd.DataFrame(self.buffer)
                                self.buffer = []
                            
                            if not df_new.empty:
                                df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                                df_combined = df_combined[self.output_columns]
                                self.save_data(df_combined)
                                df_existing = df_combined
                                last_save_time = time.time()
                        
                        if self.failed_ids:
                            self.save_failed_ids()
        
        # Save remaining results
        if self.buffer:
            with self.buffer_lock:
                df_new = pd.DataFrame(self.buffer)
                self.buffer = []
            
            if not df_new.empty:
                df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                df_combined = df_combined[self.output_columns]
                self.save_data(df_combined)
        
        if self.failed_ids:
            self.save_failed_ids()
        
        # Print final statistics
        elapsed = time.time() - start_time
        final_rpm = processed_count / (elapsed / 60)
        
        print(f"\nProcessing complete:")
        print(f"Total processed: {processed_count}")
        print(f"Average speed: {final_rpm:.0f} RPM")
        print(f"Failed entries: {len(self.failed_ids)}")
        if self.failed_ids:
            print(f"Failed entries saved to: {self.failed_path}")
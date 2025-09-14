from gmail_reader import authenticate, fetch_filtered_messages_from_threads, get_threads
from message_processor import save_thread_as_markdown

SUBJECT_KEYWORD = 'Feedback received from'

def fetch_and_process_mails(max_threads: None):
    service = authenticate()
    
    page_token = None
    counter = 1
    while True:
        threads, next_page_token = get_threads(service, page_token)
        print(f"Found {len(threads)} threads in total for iteration #{counter}. Next page token: {next_page_token}")
        if not threads:
            print("No more threads found.")
            break
        
        counter += 1
        
        messages_per_threads = fetch_filtered_messages_from_threads(service, threads, max_threads, SUBJECT_KEYWORD)
        print(f"*** Found relevant {len(threads)} threads for iteration #{counter} ***")
        for i, messages_per_thread in enumerate(messages_per_threads):
            thread_id = f"{i + 1}"
            save_thread_as_markdown(thread_id, messages_per_thread)
            
        if not next_page_token:
            print("No more pages to process.")
            break
        
        page_token = next_page_token

def main():
    fetch_and_process_mails(100)

if __name__ == '__main__':
    main()
from datetime import datetime
import os
import base64
import markdownify
import re
from email_message import EmailMessage

def __generate_filename(date_str: datetime, thread_id: str) -> str:
    # Sat, 07 Jun 2025 07:44:51 +0000 (UTC)
    if date_str.endswith(' (UTC)'):
        date_str = date_str[:-7].strip()
    date_str = re.sub(r' [+-]\d{3,4}$', '', date_str)  # Remove " +000" or " +0000" at end
    try:
      date = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S")
      date_str = date.strftime("%Y-%m-%d_%H-%M")
    except ValueError:
        print(f"Error parsing date: {date_str}. Using thread ID as filename.")
        return f"{thread_id}.md"
    return f"{date_str}_{thread_id}.md"

def save_thread_as_markdown(thread_id, messages, out_dir="gmail_threads"):
    os.makedirs(out_dir, exist_ok=True)
    
    email_messages = __convert_raw_messages_to_messages(messages)
    if not email_messages or len(email_messages) == 0:
        print(f"No messages found for thread {thread_id}. Skipping.")
        return
   
    date_str = email_messages[0].date
    pure_filename = __generate_filename(date_str, thread_id)
    filename = os.path.join(out_dir, f"{pure_filename}")
    
    lines = []
    for i, email_message in enumerate(email_messages):
        if i == 0:
            print(f"Saving thread {thread_id} to {filename}")
        line = f"## From: {email_message.from_email}\n**Date**: {email_message.date}\n**Subject**: {email_message.subject}\n\n"
        line += f"```\n{email_message.body}\n```\n"
        lines.append(line)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n---\n'.join(lines))
        
        
def __convert_raw_messages_to_messages(raw_messages) -> list[EmailMessage]:
    messages = []
    for raw_message in raw_messages:
        headers = {h['name']: h['value'] for h in raw_message['payload']['headers']}
        from_header = headers.get('From', 'Unknown Sender')
        date_header = headers.get('Date', 'Unknown Date')
        subject = headers.get('Subject', 'No Subject')
        body = extract_message_text(raw_message)

        messages.append(EmailMessage(
            raw_message['threadId'],
            subject,
            from_header,
            date_header,
            body
        ))
    return messages
  
def extract_message_text(message):
    payload = message['payload']
    parts = payload.get('parts')
    
    result = "[No readable content]"
    
    if parts:
        result = __get_text_from_parts(parts)
    else:
        # fallback for plain text
        body = payload['body'].get('data')
        if body:
            result = base64.urlsafe_b64decode(body).decode('utf-8', errors='ignore')

    result = result.replace('<br/>', '\n')
    result = __clean_email_body(result)
    return result
  
def __get_text_from_parts(parts):
    for part in parts:
        if part.get('mimeType') == 'text/plain':
            data = part['body'].get('data')
            if data:
                return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        elif part.get('mimeType') == 'text/html':
            data = part['body'].get('data')
            if data:
                html = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                return markdownify.markdownify(html)
        # Recursively check nested parts
        if 'parts' in part:
            result = __get_text_from_parts(part['parts'])
            if result:
                return result
    return "[No readable content]"

def __clean_email_body(text):
    # Regex for common German Gmail reply separators
    #Am Mo., 7. Juli 2025 um 13:05 Uhr schrieb <\r\email@mailing.eu>:\r\n\r\n>
    # Am 31.05.25 um 17:50 schrieb Vorname Nachname:
    # Von: Vorname Nachname <email@gmail.com>
    patterns = [
        r'Am .* schrieb .*',                        # Pattern 1: "Am ... schrieb ..."
        r'.*<.*?> schrieb am .*',                        # Pattern 2: "... <...> schrieb am ..."
        r'Von: .* <.*?>',                        # Pattern 3: "Von: ... <...>"
    ]
    
    result = text.strip()
    # Split text into lines array by newlines (\r or \n)
    text_lines = result.splitlines()
    # Remove empty lines
    text_lines = [line for line in text_lines if line.strip()]
    
    text_lines_to_keep = []
    for line in text_lines:
        line = line.strip()
        start_of_conversation_history = False
        for pattern in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                start_of_conversation_history = True
                break
        if start_of_conversation_history:
            break  # Stop processing further lines
        
        text_lines_to_keep.append(line)

    # Join lines back to a single string
    result = '\n'.join(text_lines_to_keep)
    return result    
  
# def __remove_quoted_lines(text):
#   cleaned_lines = []
#   for line in text.splitlines():
#       if not line.strip().startswith('>'):
#           cleaned_lines.append(line)
#   return '\n'.join(cleaned_lines).strip()
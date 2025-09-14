from dataclasses import dataclass

@dataclass
class EmailMessage():
    thread_id: str
    subject: str
    from_email: str
    date: str
    body: str
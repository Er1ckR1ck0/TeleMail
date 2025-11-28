import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
import os
import re
import html

import html2text


def html_to_text(html_content: str) -> str:
    if not html_content:
        return ""
    
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = True
    h.body_width = 0
    
    return h.handle(html_content).strip()


def decode_header_value(header) -> str:
    if header is None:
        return ""
    decoded_parts = decode_header(header)
    result = []
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            result.append(part.decode(encoding or "utf-8", errors="replace"))
        else:
            result.append(part)
    return "".join(result)


def get_email_body(msg) -> str:
    text_body = ""
    html_body = ""
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if "attachment" in str(part.get("Content-Disposition")):
                continue
            try:
                payload = part.get_payload(decode=True)
                if not payload:
                    continue
                charset = part.get_content_charset() or "utf-8"
                decoded = payload.decode(charset, errors="replace")
                if content_type == "text/plain":
                    text_body = decoded
                elif content_type == "text/html":
                    html_body = decoded
            except Exception:
                continue
    else:
        try:
            payload = msg.get_payload(decode=True)
            charset = msg.get_content_charset() or "utf-8"
            decoded = payload.decode(charset, errors="replace")
            if msg.get_content_type() == "text/html":
                html_body = decoded
            else:
                text_body = decoded
        except Exception:
            pass
    
    if text_body:
        return text_body.strip()
    elif html_body:
        return html_to_text(html_body)
    return ""


def get_attachments(msg) -> list:
    attachments = []
    
    if msg.is_multipart():
        for part in msg.walk():
            content_disposition = str(part.get("Content-Disposition", ""))
            
            if "attachment" in content_disposition or "inline" in content_disposition:
                filename = part.get_filename()
                if filename:
                    filename = decode_header_value(filename)
                    
                    try:
                        payload = part.get_payload(decode=True)
                        if payload and len(payload) <= 50 * 1024 * 1024:
                            attachments.append({
                                "filename": filename,
                                "data": payload,
                                "size": len(payload)
                            })
                    except Exception as e:
                        print(f"Ошибка извлечения вложения {filename}: {e}")
    
    return attachments


class MailService:
    
    def __init__(self):
        self.email_addr = os.getenv("YANDEX_EMAIL")
        self.password = os.getenv("YANDEX_APP_PASSWORD")
        self.server = "imap.yandex.ru"
        self.seen_uids = set()
    
    def _connect(self):
        mail = imaplib.IMAP4_SSL(self.server, 993)
        mail.login(self.email_addr, self.password)
        mail.select("INBOX")
        return mail
    
    def _parse_email(self, raw_email: bytes, uid: bytes) -> dict:
        msg = email.message_from_bytes(raw_email)
        
        return {
            "uid": uid.decode(),
            "subject": decode_header_value(msg["Subject"]) or "(без темы)",
            "sender": decode_header_value(msg["From"]),
            "date": msg["Date"],
            "body": get_email_body(msg),
            "attachments": get_attachments(msg)
        }
    
    def check_new_emails(self, limit: int = 5, mark_seen: bool = True) -> list:
        new_emails = []
        
        try:
            mail = self._connect()
            
            status, messages = mail.search(None, "UNSEEN")
            if status == "OK":
                uids = messages[0].split()
                
                for uid in uids[-limit:]:
                    if uid in self.seen_uids:
                        continue
                    self.seen_uids.add(uid)
                    
                    fetch_cmd = "(RFC822)" if mark_seen else "(BODY.PEEK[])"
                    status, msg_data = mail.fetch(uid, fetch_cmd)
                    if status != "OK":
                        continue
                    
                    raw_email = msg_data[0][1]
                    new_emails.append(self._parse_email(raw_email, uid))
            
            mail.logout()
        except Exception as e:
            print(f"Ошибка проверки почты: {e}")
        
        return new_emails
    
    def get_emails_by_date(self, days_back: int = 7, offset: int = 0, limit: int = 1) -> tuple:
        emails = []
        total = 0
        
        try:
            mail = self._connect()
            
            since_date = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")
            status, messages = mail.search(None, f'(SINCE "{since_date}")')
            
            if status == "OK":
                uids = messages[0].split()
                total = len(uids)
                
                uids = list(reversed(uids))
                
                for uid in uids[offset:offset + limit]:
                    status, msg_data = mail.fetch(uid, "(BODY.PEEK[])")
                    if status != "OK":
                        continue
                    
                    raw_email = msg_data[0][1]
                    emails.append(self._parse_email(raw_email, uid))
            
            mail.logout()
        except Exception as e:
            print(f"Ошибка получения писем: {e}")
        
        return emails, total
    
    def get_all_emails(self, limit: int = 5) -> list:
        emails = []
        
        try:
            mail = self._connect()
            
            status, messages = mail.search(None, "ALL")
            if status == "OK":
                uids = messages[0].split()
                
                for uid in uids[-limit:]:
                    status, msg_data = mail.fetch(uid, "(BODY.PEEK[])")
                    if status != "OK":
                        continue
                    
                    raw_email = msg_data[0][1]
                    emails.append(self._parse_email(raw_email, uid))
            
            mail.logout()
        except Exception as e:
            print(f"Ошибка получения писем: {e}")
        
        return emails

    def get_emails_page(self, page: int = 0, per_page: int = 10) -> tuple[list, int, int]:
        emails = []
        total = 0
        
        try:
            mail = self._connect()
            
            status, messages = mail.search(None, "ALL")
            if status == "OK":
                uids = messages[0].split()
                total = len(uids)

                uids = list(reversed(uids))

                start = page * per_page
                end = start + per_page
                page_uids = uids[start:end]
                
                for uid in page_uids:
                    status, msg_data = mail.fetch(uid, "(BODY.PEEK[])")
                    if status != "OK":
                        continue
                    
                    raw_email = msg_data[0][1]
                    emails.append(self._parse_email(raw_email, uid))
            
            mail.logout()
        except Exception as e:
            print(f"Ошибка получения писем: {e}")
        
        total_pages = (total + per_page - 1) // per_page if total > 0 else 0
        return emails, total, total_pages

    def get_email_by_uid(self, uid: str) -> dict | None:
        try:
            mail = self._connect()
            
            status, msg_data = mail.fetch(uid.encode(), "(BODY.PEEK[])")
            if status != "OK":
                mail.logout()
                return None
            
            raw_email = msg_data[0][1]
            email_data = self._parse_email(raw_email, uid.encode())
            
            mail.logout()
            return email_data
        except Exception as e:
            print(f"Ошибка получения письма {uid}: {e}")
            return None

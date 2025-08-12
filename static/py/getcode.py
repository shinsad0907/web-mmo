import imaplib
import email
import re
import time
from email.header import decode_header
from email.utils import parsedate_to_datetime
import asyncio

class GetCode:
    def __init__(self, mail_data):
        self.mail_data = mail_data
        self.mail = None
        
    def decode_mime_words(self, s):
        decoded_fragments = decode_header(s)
        return ''.join(
            fragment.decode(charset or 'utf-8') if isinstance(fragment, bytes) else fragment
            for fragment, charset in decoded_fragments
        )

    def process_mail(self, msg, body_text, body_html):
        mailadd = self.mail_data["mailadd"]
        mail = self.mail_data["mail"]

        to_addr = msg.get("To", "").lower()
        mailadd_lower = mailadd.lower()
        if mailadd_lower not in to_addr:
            return None

        from_raw = msg.get("From", "Unknown")
        from_name_match = re.match(r'"?([^"<]+)"?\s*(<[^>]+>)?', from_raw)
        from_name = from_name_match.group(1).strip() if from_name_match else from_raw

        date_raw = msg.get("Date", "")
        try:
            dt = parsedate_to_datetime(date_raw)
            date_str = dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            date_str = date_raw

        subject_raw = msg.get("Subject", "")
        subject = self.decode_mime_words(subject_raw)

        match = re.search(
            r'https://www\.facebook\.com/login/recover/cancel/\?n=(\d+)&amp;id=(\d+)',
            body_html
        )
        if not match:
            match = re.search(
                r'https://www\.facebook\.com/login/recover/cancel/\?n=(\d+)&id=(\d+)',
                body_text
            )

        if match:
            n_val = match.group(1)
            id_val = match.group(2)
            
            return {
                'mail': mail,
                'mailadd': mailadd,
                'from_name': from_name,
                'date_str': date_str,
                'subject': subject,
                'uid': id_val,
                'code': n_val,
                'status': "✅ Đã tìm thấy code"
            }

        return None

    async def read_mail(self):
        results = []
        try:
            # Sử dụng imaplib thay vì aioimaplib
            self.mail = imaplib.IMAP4_SSL("imap.poczta.onet.pl", 993)
            self.mail.login(self.mail_data['mail'], self.mail_data['pass'])
            
            try:
                self.mail.select('"Spo&AUI-eczno&AVs-ci"')
            except:
                self.mail.select("INBOX")

            status, data = self.mail.search(None, "ALL")
            if status != "OK":
                results.append({
                    'mail': self.mail_data['mail'],
                    'mailadd': self.mail_data['mailadd'],
                    'from_name': 'N/A',
                    'date_str': time.strftime("%Y-%m-%d %H:%M"),
                    'subject': 'Lỗi tìm mail',
                    'uid': 'N/A',
                    'code': 'N/A',
                    'status': "❌ Không thể tìm thấy mail"
                })
                return results

            mail_ids = data[0].split()
            mail_ids = mail_ids[-50:]  # Chỉ lấy 50 mail mới nhất

            for mail_id in reversed(mail_ids):
                try:
                    status, msg_data = self.mail.fetch(mail_id, "(RFC822)")
                    if status != "OK":
                        continue

                    msg = email.message_from_bytes(msg_data[0][1])
                    body_text = ""
                    body_html = ""

                    if msg.is_multipart():
                        for part in msg.walk():
                            ctype = part.get_content_type()
                            if ctype == "text/plain":
                                body_text += part.get_payload(decode=True).decode(
                                    part.get_content_charset() or "utf-8", errors="ignore"
                                )
                            elif ctype == "text/html":
                                body_html += part.get_payload(decode=True).decode(
                                    part.get_content_charset() or "utf-8", errors="ignore"
                                )
                    else:
                        ctype = msg.get_content_type()
                        if ctype == "text/plain":
                            body_text = msg.get_payload(decode=True).decode(
                                msg.get_content_charset() or "utf-8", errors="ignore"
                            )
                        elif ctype == "text/html":
                            body_html = msg.get_payload(decode=True).decode(
                                msg.get_content_charset() or "utf-8", errors="ignore"
                            )

                    result = self.process_mail(msg, body_text, body_html)
                    if result:
                        results.append(result)
                        break  # Tìm thấy code thì dừng

                    await asyncio.sleep(0.05)  # Thêm delay nhỏ giữa các request

                except Exception as e:
                    print(f"[INFO] Bỏ qua mail {mail_id}: {str(e)}")
                    continue

            self.mail.logout()

        except Exception as e:
            results.append({
                'mail': self.mail_data['mail'],
                'mailadd': self.mail_data['mailadd'],
                'from_name': 'N/A',
                'date_str': time.strftime("%Y-%m-%d %H:%M"),
                'subject': 'Lỗi đăng nhập',
                'uid': 'N/A',
                'code': 'N/A',
                'status': f"❌ Lỗi đăng nhập: {e}"
            })

        if not results:
            results.append({
                'mail': self.mail_data['mail'],
                'mailadd': self.mail_data['mailadd'],
                'from_name': 'N/A',
                'date_str': time.strftime("%Y-%m-%d %H:%M"),
                'subject': 'Đã check xong',
                'uid': 'N/A',
                'code': 'N/A',
                'status': "❌ Không tìm thấy code"
            })

        return results

async def process_accounts(accounts):
    tasks = [GetCode(account).read_mail() for account in accounts]
    results = await asyncio.gather(*tasks)
    return [item for sublist in results for item in sublist]
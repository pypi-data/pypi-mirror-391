"""
easynotify.notifier
A simple notification helper using AWS SNS or email (fallback)
"""

import boto3
import os
import smtplib
from email.mime.text import MIMEText

class EasyNotify:
    def __init__(self, mode='sns', region='eu-west-1'):
        self.mode = mode
        self.region = region

    def send(self, subject, message, target):
        if self.mode == 'sns':
            return self._send_sns(subject, message, target)
        else:
            return self._send_email(subject, message, target)

    def _send_sns(self, subject, message, topic_arn):
        sns = boto3.client('sns', region_name=self.region)
        sns.publish(TopicArn=topic_arn, Subject=subject, Message=message)
        return f"SNS message sent to topic: {topic_arn}"

    def _send_email(self, subject, message, email_to):
        sender = os.getenv('EMAIL_USER')
        password = os.getenv('EMAIL_PASS')
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = email_to

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, email_to, msg.as_string())
        return f"Email sent to {email_to}"


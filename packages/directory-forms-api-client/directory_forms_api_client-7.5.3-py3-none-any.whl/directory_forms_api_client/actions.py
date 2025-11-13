import abc

from directory_forms_api_client.client import forms_api_client


class AbstractAction(abc.ABC):

    def __init__(self, form_url, client=forms_api_client, form_session=None, sender=None, spam_control=None):
        self.form_url = form_url
        self.client = client
        self.form_session = form_session
        self.sender = sender or {}
        self.spam_control = spam_control or {}

    @property
    @abc.abstractmethod
    def name(self):
        return ''

    def serialize_data(self, data):
        return {'data': data, 'meta': self.serialize_meta()}

    def serialize_meta(self):
        meta = {
            'action_name': self.name,
            'form_url': self.form_url,
            'sender': self.sender,
            'spam_control': self.spam_control,
            **self.meta,
        }
        if self.form_session:
            meta['funnel_steps'] = self.form_session.funnel_steps
            meta['ingress_url'] = self.form_session.ingress_url
        return meta

    def save(
        self,
        data,
        form_session=None,
    ):
        serialized_data = self.serialize_data(data)
        return self.client.submit_generic(serialized_data)


class SaveOnlyInDatabaseAction(AbstractAction):
    name = 'save-only-in-db'

    def __init__(self, subject, full_name, email_address, *args, **kwargs):
        self.meta = {
            'full_name': full_name,
            'email_address': email_address,
            'subject': subject,
            'recipient_email': email_address,
        }
        super().__init__(*args, **kwargs)


class HCSatAction(AbstractAction):
    name = 'hcsat-feedback-submission'

    def __init__(self, *args, **kwargs):
        self.meta = {}
        super().__init__(*args, **kwargs)

    def save(self, data):
        return self.client.hcsat_feedback_submission(data)


# To be deprecated - DO NOT USE EmailAction Use GovNotifyEmailAction
class EmailAction(AbstractAction):
    name = 'email'

    def __init__(self, recipients, subject, reply_to, *args, **kwargs):
        self.meta = {
            'recipients': recipients,
            'subject': subject,
            'reply_to': reply_to,
        }
        super().__init__(*args, **kwargs)


class ZendeskAction(AbstractAction):
    name = 'zendesk'

    def __init__(
        self,
        subject,
        full_name,
        email_address,
        service_name,
        subdomain=None,
        sort_fields_alphabetically=True,
        *args,
        **kwargs,
    ):
        self.meta = {
            'full_name': full_name,
            'email_address': email_address,
            'subject': subject,
            'service_name': service_name,
            'sort_fields_alphabetically': sort_fields_alphabetically,
        }
        # if empty Forms API will use the default configured zendesk subdomain
        if subdomain:
            self.meta['subdomain'] = subdomain
        super().__init__(*args, **kwargs)


class GovNotifyEmailAction(AbstractAction):
    name = 'gov-notify-email'

    def __init__(self, template_id, email_address, email_reply_to_id=None, *args, **kwargs):
        self.meta = {
            'template_id': template_id,
            'email_address': email_address,
        }
        if email_reply_to_id:
            self.meta['email_reply_to_id'] = email_reply_to_id
        super().__init__(*args, **kwargs)


class GovNotifyBulkEmailAction(AbstractAction):
    name = 'gov-notify-bulk-email'

    def __init__(self, template_id, email_reply_to_id=None, *args, **kwargs):
        self.meta = {'template_id': template_id}
        if email_reply_to_id:
            self.meta['email_reply_to_id'] = email_reply_to_id
        super().__init__(*args, **kwargs)

    def save(self, data):
        return self.client.gov_notify_bulk_email(data)


class GovNotifyLetterAction(AbstractAction):
    name = 'gov-notify-letter'

    def __init__(self, template_id, *args, **kwargs):
        self.meta = {
            'template_id': template_id,
        }
        super().__init__(*args, **kwargs)


class PardotAction(AbstractAction):
    name = 'pardot'

    def __init__(self, pardot_url, *args, **kwargs):
        self.meta = {
            'pardot_url': pardot_url,
        }
        super().__init__(*args, **kwargs)


class UnverifiedReminderAction(AbstractAction):
    name = 'verification-reminders'

    def __init__(self, template_id, email_reply_to_id=None, *args, **kwargs):
        self.meta = {
            'template_id': template_id,
        }
        if email_reply_to_id:
            self.meta['email_reply_to_id'] = email_reply_to_id
        super().__init__(*args, **kwargs)

    def save(self, data):
        serialized_data = self.serialize_data(data)
        return self.client.verification_reminders(serialized_data)

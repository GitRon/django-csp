from django.core.mail import send_mail, mail_admins
from django.core.urlresolvers import reverse
from django.conf import settings
from django.template import loader, Context


def from_settings():
    return {
        'default-src': getattr(settings, 'CSP_DEFAULT_SRC', ["'self'"]),
        'script-src': getattr(settings, 'CSP_SCRIPT_SRC', None),
        'object-src': getattr(settings, 'CSP_OBJECT_SRC', None),
        'style-src': getattr(settings, 'CSP_STYLE_SRC', None),
        'img-src': getattr(settings, 'CSP_IMG_SRC', None),
        'media-src': getattr(settings, 'CSP_MEDIA_SRC', None),
        'frame-src': getattr(settings, 'CSP_FRAME_SRC', None),
        'font-src': getattr(settings, 'CSP_FONT_SRC', None),
        'connect-src': getattr(settings, 'CSP_CONNECT_SRC', None),
        'sandbox': getattr(settings, 'CSP_SANDBOX', None),
        'report-uri': getattr(settings, 'CSP_REPORT_URI', None),
    }


def build_policy():
    """Builds the policy as a string from the settings."""

    config = from_settings()
    report_uri = config.pop('report-uri', None)
    policy = ['%s %s' % (k, ' '.join(v)) for k, v in
              config.items() if v is not None]
    if report_uri:
        policy.append('report-uri %s' % report_uri)
    return '; '.join(policy)


def send_new_mail(sender, report, site=None, **kw):
    subject = 'New CSP Violation: %s' % sender.name
    url = reverse('admin:csp_report_change', args=(report.id,))
    if site is not None:
        url = ''.join(('http://', site.domain, url))
    data = report.__dict__
    data.update({'name': sender.name,
                 'identifier': sender.identifier,
                 'url': url})
    c = Context(data)
    t = loader.get_template('csp/email/new_report.ltxt')
    body = t.render(c)

    if hasattr(settings, 'CSP_NOTIFY'):
        send_mail(subject, body, settings.SERVER_EMAIL, settings.CSP_NOTIFY)
    else:
        mail_admins(subject, body)

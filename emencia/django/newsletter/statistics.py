"""Statistics for emencia.django.newsletter"""
from django.db.models import Q

from emencia.django.newsletter.models import ContactMailingStatus as Status

def get_newsletter_opening_statistics(status, recipients):
    """Return opening statistics of a newsletter based on status"""
    openings = status.filter(Q(status=Status.OPENED) | Q(status=Status.OPENED_ON_SITE))
    total_openings = openings.count()
    if total_openings:
        unique_openings = len(set(openings.values_list('contact', flat=True)))
        unique_openings_percent = float(unique_openings) / float(recipients) * 100
        unknow_openings = recipients - unique_openings
        unknow_openings_percent = float(unknow_openings) / float(recipients) * 100
        opening_average = float(total_openings) / float(unique_openings)
    else:
        unique_openings = unique_openings_percent = unknow_openings = \
                          unknow_openings_percent = opening_average = 0

    return {'total_openings': total_openings,
            'double_openings': total_openings - unique_openings,
            'unique_openings': unique_openings,
            'unique_openings_percent': unique_openings_percent,
            'unknow_openings': unknow_openings,
            'unknow_openings_percent': unknow_openings_percent,
            'opening_average': opening_average}

def get_newsletter_on_site_opening_statistics(status):
    """Return on site opening statistics of a newsletter based on status"""
    on_site_openings = status.filter(status=Status.OPENED_ON_SITE)
    total_on_site_openings = on_site_openings.count()
    unique_on_site_openings = len(set(on_site_openings.values_list('contact', flat=True)))

    return {'total_on_site_openings': total_on_site_openings,
            'unique_on_site_openings': unique_on_site_openings}


def get_newsletter_clicked_link_statistics(status, recipients, openings):
    """Return clicked link statistics of a newsletter based on status"""
    clicked_links = status.filter(status=Status.LINK_OPENED)

    total_clicked_links = clicked_links.count()
    total_clicked_links_percent = float(total_clicked_links) / float(recipients) * 100

    unique_clicked_links = len(set(clicked_links.values_list('contact', flat=True)))
    unique_clicked_links_percent = float(unique_clicked_links) / float(recipients) * 100

    double_clicked_links = total_clicked_links - unique_clicked_links
    double_clicked_links_percent = float(double_clicked_links) / float(recipients) * 100

    clicked_links_by_openings = openings and float(total_clicked_links) / float(openings) * 100 or 0.0

    clicked_links_average = total_clicked_links and float(total_clicked_links) / float(unique_clicked_links) or 0.0

    return {'total_clicked_links': total_clicked_links,
            'total_clicked_links_percent': total_clicked_links_percent,
            'double_clicked_links': double_clicked_links,
            'double_clicked_links_percent': double_clicked_links_percent,
            'unique_clicked_links': unique_clicked_links,
            'unique_clicked_links_percent': unique_clicked_links_percent,
            'clicked_links_by_openings': clicked_links_by_openings,
            'clicked_links_average': clicked_links_average}

def get_newsletter_top_links(status):
    """Return the most clicked links"""
    links = {}
    for s in status.filter(status=Status.LINK_OPENED):
        links.setdefault(s.link, 0)
        links[s.link] += 1

    return {'top_links': sorted(links.iteritems(), key=lambda (k,v): (v,k), reverse=True)}

def get_newsletter_statistics(newsletter):
    """Return the statistics of a newsletter"""
    recipients = newsletter.mailing_list.expedition_set().count()
    all_status = Status.objects.filter(newsletter=newsletter)
    post_sending_status = all_status.filter(creation_date__gte=newsletter.sending_date)
    mails_sent = post_sending_status.filter(status=Status.SENT).count()

    statistics = {'tests_sent': all_status.filter(status=Status.SENT_TEST).count(),
                  'mails_sent': mails_sent,
                  'mails_to_send': recipients,
                  'remaining_mails': recipients - mails_sent}

    statistics.update(get_newsletter_opening_statistics(post_sending_status, recipients))
    statistics.update(get_newsletter_on_site_opening_statistics(post_sending_status))
    statistics.update(get_newsletter_clicked_link_statistics(post_sending_status, recipients,
                                                             statistics['total_openings']))
    statistics.update(get_newsletter_top_links(post_sending_status))

    return statistics


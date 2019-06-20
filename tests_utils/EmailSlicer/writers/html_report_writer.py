import jinja2


def write(report_title, pst_name, email_frequency):
    """
    The HTMLReport function generates the HTML report from a Jinja2 Template
    :param report_title: A string representing the title of the report
    :param pst_name: A string representing the file name of the PST
    :param top_words: A list of the top 10 words
    :param top_senders: A list of the top 10 senders
    :return: None
    """
    open_template = open("stats_template.html", 'r').read()
    html_template = jinja2.Template(open_template)

    #context = {"report_title": report_title, "pst_name": pst_name}
    top_senders = []
    context = {"report_title": report_title, "pst_name": pst_name,
               "email_frequency": email_frequency}
    new_html = html_template.render(context)

    html_report_file = open('output_files/' + report_title + '.html', 'w+')
    html_report_file.write(new_html)
    html_report_file.close()
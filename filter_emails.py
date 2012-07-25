import re
import csv
import sys
from webscraping import common



def order_emails(emails, website):
    """Order emails by how useful they are

    An email is considered more useful if:
    - comes from the same domain
    - contains 'info' or 'contact'
    - is not a no-reply email
    """
    email_score = {}
    domain = common.get_domain(website)
    for i, email in enumerate(emails):
        email = email.strip()
        if email and not re.match('no.?reply', email):
            # ignore no reply emails
            score = 0
            if domain and domain in email:
                # same domain more useful
                score += 10
            if 'info' in email or 'contact' in email:
                # info domain more useful
                score += 10
            if i < 5:
                # give first found emails a bonus
                score += 5 - i
            email_score[email] = score

    # order by score
    return sorted(email_score, key=email_score.get)


def main(input_file, output_file):
    writer = common.UnicodeWriter(output_file)
    header = None
    for row in csv.reader(open(input_file)):
        if header:
            emails = row[email_i].split(',')
            website = row[website_i]
            row[email_i] = order_emails(emails, website)[0]
        else:
            header = row
            email_i = website_i = None
            for i, col in enumerate(header):
                if 'email' in col.lower():
                    email_i = i
                elif 'website' in col.lower():
                    website_i = i
            if email_i is None:
                raise Exception('Could not find email column')
            if website_i is None:
                raise Exception('Could not find website column')
        writer.writerow(row)



if __name__ == '__main__':
    try:
        input_file = sys.argv[1]
    except IndexError:
        print('Usage: %s <csv file>' % sys.argv[0])
    if not input_file.endswith('.csv'):
        print ('Need to pass a CSV file')
    output_file = input_file.replace('.csv', '_emails.csv')
    main(input_file, output_file)

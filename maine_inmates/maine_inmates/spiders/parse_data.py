from datetime import datetime


def get_maine_inmates(response, link):
    full_name = data_fetcher(response, 'Last Name, First Name, Middle Initial:')
    first_name, middle_name, last_name, suffix = name_split(full_name)
    birthdate = data_fetcher(response, 'Date of Birth:')
    data_hash = {
        'full_name': full_name,
        'first_name': first_name,
        'middle_name': middle_name,
        'last_name': last_name,
        'suffix': suffix,
        'birthdate': get_date(birthdate),
        'sex': data_fetcher(response, 'Gender:'),
        'race': data_fetcher(response, 'Race/Ethnicity:'),
        'data_source_url': link
    }
    return data_hash


def get_date(date):
    try:
        date_obj = datetime.strptime(date, "%m/%d/%Y")
        return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        return None


def name_split(full_name):
    suffix_name = None
    if ' - ' in full_name:
        name_splitting = [a.strip().replace(' - ', '-')
                          for a in full_name.split(',')]
        first_name = name_splitting[0]
        last_name = name_splitting[-1]
        if len(last_name.split(' ')) == 2:
            middle_name, last_name = last_name.split(' ')
        else:
            middle_name = None
    else:
        try:
            name_splitting = full_name.strip().split(' ')
            middle_name, last_name = None, None
            first_name = name_splitting[0]
            suffix_name = get_suffix(name_splitting)
            filtered_array = [s for s in name_splitting if s.upper() not in [
                "JR", "JR.", "SR", "SR."]]
            if len(filtered_array) == 1:
                middle_name, last_name = None, None
            elif len(filtered_array) == 2:
                middle_name, last_name = None, filtered_array[-1]
            elif len(filtered_array) == 3:
                middle_name, last_name = filtered_array[1], filtered_array[2]
            elif len(filtered_array) > 3:
                middle_name, last_name = filtered_array[1], ' '.join(
                    filtered_array[2:])
        except:
            first_name, middle_name, last_name = None, None, None

    return remove_comma(first_name), remove_comma(middle_name), remove_comma(last_name), suffix_name


def remove_comma(name):
    return name.replace(",", "") if name else name


def get_suffix(name_splitting):
    suffix_value = None
    suffix_list = ["JR", "JR.", "SR", "SR."]
    suffix_matches = [s for s in name_splitting if s.upper() in suffix_list]
    if suffix_matches:
        suffix_value = suffix_matches[0]
    return suffix_value


def data_fetcher(response, search_text, index=0):
    table = response.css('table.at-data-table')[0]
    values = table.xpath(
        './/td[contains(text(), "{}")]/following-sibling::td[1]//text()'.format(search_text)).getall()
    if values:
        return values[index].strip()
    else:
        return None

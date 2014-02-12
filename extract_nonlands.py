import datetime
import logging
import json
import re
import subprocess
import sys
import traceback

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

def _query_tutor(command_parameters):
    """
    :param command_parameters:
    :return: the json-parsed output of the tutor command
    """

    command = ['tutor', '--format', 'json'] + command_parameters

    try:
        return json.loads(subprocess.check_output(command).strip())
    except (subprocess.CalledProcessError, ValueError) as e:
        raise subprocess.CalledProcessError(u'problem with command',
                                            u' '.join(command))

def query_cards_with_ids(card_ids):
    set_cards = []

    for card_id in card_ids:
        card = _query_tutor(['card', card_id])
        card['id'] = card_id
        set_cards.append(card)

    return set_cards

def query_cards_in_set(set_name):
    """
    :param set_name: the set's name, which will be passed to tutor's command line
    :return: a list of cards represented as dictionaries in the given set.
    """

    print "Getting set \'" + set_name + "\'..."

    start_time = get_time_now()
    set_card_list = _query_tutor(['set', set_name])
    card_ids = get_ids_from_set_list(set_card_list)

    set_cards = query_cards_with_ids(card_ids)

    end_time = get_time_now()

    print('Finished getting set \'{0}\' of {1} cards; set elapsed time: {2}'.format(
        set_name, len(set_cards), str(end_time - start_time)))

    return set_cards

# group 2 should contain the card ID part of a Gatherer URL.
url_breaker = re.compile(r"(.*)=(\d+$)")

def get_ids_from_set_list(set_card_list):
    card_ids = []
    for card in set_card_list:
        url_parts = url_breaker.match(card['gatherer_url'])
        card_ids.append(url_parts.group(2))

    return card_ids

def query_all_sets():
    """
    :return: list of all sets reported by Gatherer.
    """
    log.debug('searching for sets')
    return _query_tutor(['sets'])

def write_cards_from_sets_to_file(target_sets):
    """
    :return: a dictionary mapping card IDs to the card's dictionary representation
    """
    all_cards_dict = {}
    all_errored_cards = []

    for set_name in target_sets:
        set_cards = query_cards_in_set(set_name)
        set_id_dict = {}

        (set_id_dict, errored_cards) = card_postprocessing(set_cards)
        all_errored_cards.extend(errored_cards)

        all_cards_dict.update(set_id_dict)

    json.dump(all_cards_dict, open('cards.json', 'wb'), indent=4, sort_keys=True, separators=(',', ': '))

    return all_errored_cards

def card_postprocessing(set_cards):
    errored_cards = []
    set_id_dict = {}
    set_collector_num_dict = {}

    for card in set_cards:
        cardname = card['name']
        card['special_card'] = 'normal'

        # leaving out basic lands; most basic lands have several art variations with different IDs
        # (and thus different image and gatherer URLs).  I can't figure out how to get Tutor to report these
        # other art variations' IDs.  it *does* report a card for each variation, but the IDs are all identical.
        if card['rarity'] != 'Basic Land':
            try:
                # early sets don't have reported collector numbers...
                if 'number' in card:
                    cleaned_number = clean_ab(str(card['number']))

                    # hack note 1:
                    # split cards and flip cards are reported twice with the same id by Tutor.
                    # the full English 'X // Y' name may be found in the nonenglish card names for nearly every set.
                    # Almost every split card has a German "translation", and it's in *English*.
                    if card['id'] in set_id_dict:
                        card['special_card'] = 'split-or-flip'
                        card['name'] = card['languages']['de']['name']
                    # hack note 2:
                    # each face of double-face cards (like werewolves) are reported with separate IDs, but
                    # they have the same collector number with a or b appended... note the card's double-faced
                    # plus the ID of its companion.  let's record that the two IDs are related.
                    elif cleaned_number in set_collector_num_dict:
                        card['special_card'] = 'double-face'
                        companion_card = set_collector_num_dict[cleaned_number]
                        card['companion_id'] = companion_card['id']
                        companion_card['companion_id'] = card['id']
                        companion_card['special_card'] = 'double-face'

                    set_collector_num_dict[cleaned_number] = card

            except KeyError as ke:
                print 'KeyError in special_card_processing: {0}'.format(str(ke))
                print 'Error was on card: {0} with id {1}'.format(card['name'], card['id'])
                print traceback.format_exc()
                errored_cards.append(card)
            
            set_id_dict[card['id']] = card

    return (set_id_dict, errored_cards)

def ends_with_ab(number_string):
    last_char = number_string[-1:]
    return last_char == 'a' or last_char == 'b'

def clean_ab(number_string):
    if ends_with_ab(number_string):
        return number_string[0:-1]
    return number_string

def check_specified_sets_exist(all_sets, spec_sets):
    for spec_set in spec_sets:
        if not spec_set in all_sets:
            return False

    return True

def main(args):
    all_sets = query_all_sets()

    query_sets = args

    if not check_specified_sets_exist(all_sets, query_sets):
        print("Some of the sets you specified don't exist.  Doublecheck your arguments.")
        exit(1)

    if len(args) == 0:
        query_sets = all_sets

    start_time = get_time_now()
    print('Started scrape at: ' + str(start_time))

    errored_cards = write_cards_from_sets_to_file(query_sets)

    end_time = get_time_now()
    print('***************************************************')
    print('Finished scrape at: ' + str(end_time))
    print('Total elapsed time: ' + str(end_time - start_time))
    print('***************************************************')

    print_errored_cards(errored_cards)

def get_time_now():
    return datetime.datetime.now().replace(microsecond=0)

def print_errored_cards(errored_cards):
    if len(errored_cards) > 0:
        print "The following cards had processing errors: "
        errored_cards.sort(key=lambda card: card['id'])
        for card in errored_cards:
            print("id = {0:8}; name = {1}".format(card['id'], card['name']))

if __name__ == '__main__':
    main(sys.argv[1:])

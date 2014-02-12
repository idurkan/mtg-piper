## MTG Piper

Piper is my set of Python tools for scraping *Magic: The Gathering* card information from the Gatherer site.  Be warned it is not particularly robust.  Piper scrapes only English-language text and images of cards; the card output does point out the IDs of corresponding non-English cards however.

## Dependencies

- Python 2.7.3; earlier versions of Python may work however.  Invoke all the scripts using python.
- The [Tutor](https://github.com/davidchambers/tutor) tool for [Node.js](http://nodejs.org/).
- I've only used Piper on recent versions of Linux Mint (14 and 15).  Presumably it'll work on any Debian Linux distro.

## Installation

There is no specific installation for Piper itself, however Tutor must be installed globally.

1. Install Node.js and npm.  See the [instructions here](http://www.joyent.com/blog/installing-node-and-npm/).
2. Clone the Tutor repo.
3. Install Tutor as a global module: `npm install <path_to_tutor> --global`.  Note that the version of Tutor in the world repository is out-of-date and *will not work*.

## Instructions

### extract_nonlands.py

`extract_nonlands` uses Tutor to scrape Gatherer for non-land cards.  It uses Tutor to find the cards in each set, then uses Tutor to get the full details of each non-land card reported in the sets.  
- Specify the sets you want to scrape on the command-line, space-separated.  Enclose set names with spaces and symbols in double-quotes.  For example `python extract_nonlands.py "Avacyn Restored"` will retrieve the nonland cards in 'Avacyn Restored'.
- To scrape *all* sets specify nothing on the command-line.
- Output goes to an output file `cards.json`.

### extract_lands.py

`extract_lands` uses Tutor to scrape Gatherer for land cards.  Command-line options are the same as `extract_nonlands`.
- Output goes to an output file `lands.json`.

### download_images.py

`download_images` expects two command-line arguments:
1. Path to a card JSON file produced by `extract_nonlands`, `extract_lands`, or Tutor's `set` tool.
2. Path to an output directory - it will be created if it does not already exist.

## JSON Output Format

The JSON output format from `extract_nonlands` and `extract_lands` is nearly the same as the JSON output by Tutor.  However, all cards have an additional field `special_card` that is set to one of 'double-face', 'split-or-flip', or 'normal'.  
- 'split-or-flip' is used to indicate a card is something like 'Homura, Human Ascendant' or 'Fire // Ice' with two pseudo-cards on one card.  
- 'double-face' is used to indicate a card is something like 'Huntmaster of the Fells' which has a double face.  The other face gets a separate card, whose ID may be found in the `companion_id` field.

## "Errored Cards"

The `extract_nonlands` script will list some "errored cards" when it's finished its job.  Certain sets such as 'Archenemy' have split cards where there's no way to figure out the true full name of the card - these are the "errored cards".  'Wax // Wane' in 'Archenemy' is one example although there are more.  

## Image Output

Images are output into the specified directory as JPEGs in the format <ID>_<card name>.jpg.

*Magic: The Gathering* and all information in files rendered by this software are copyrighted by Wizards of the Coast.

This software is not produced by, endorsed by, supported by, or affiliated with Wizards of the Coast.
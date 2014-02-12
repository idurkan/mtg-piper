import re
import sys
import pprint

def main(args):
	text_path = args[0]
	file_content = open(text_path, 'r').read()

	link_id_expr = re.compile(r"multiverseid=(\d+)")
	matches = link_id_expr.findall(file_content)

	print "There were {0} matches in {1}".format(len(matches), text_path)
	pprint.pprint(matches)

if __name__ == '__main__':
    main(sys.argv[1:])

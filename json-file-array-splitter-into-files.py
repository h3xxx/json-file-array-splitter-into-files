import argparse
import json
import os


class FontColors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_msg(message, text=None, color=FontColors.GREEN) -> None:
    """
    Prints message
    :param message:
    :type message: str
    :param text:
    :type text: str
    :param color:
    :type color: any
    :return:
    """
    if text:
        print("{0}{1}{2}: {3}".format(color, message, FontColors.ENDC, text))
    else:
        print("{0}{1}{2}".format(color, message, FontColors.ENDC))


def print_info(message, text=None) -> None:
    """
    Prints info message
    :param message:
    :type message: str
    :param text:
    :type text: str
    :return:
    """
    print_msg(message, text, FontColors.BLUE)


def print_error(message, text=None) -> None:
    """
    Prints error message
    :param message:
    :type message: str
    :param text:
    :type text: str
    :return:
    """
    print_msg(message, text, FontColors.FAIL)


def save_json_file(json_content, output_file_path) -> None:
    """
    Saves JSON output file
    :param json_content:
    :type json_content: str or dict
    :param output_file_path:
    :type output_file_path: str
    :return:
    :rtype: None
    """
    try:
        if output_file_path is None:
            output_file_path = "output.json"
        with open(output_file_path, 'w') as file:
            if type(json_content) is str:
                json.dump(json.loads(json_content), file, ensure_ascii=True, indent=2, sort_keys=True)
            elif type(json_content) is dict:
                json.dump(json_content, file, ensure_ascii=True, indent=2, sort_keys=True)
    except OSError as os_error:
        print_error("Error:", os_error.strerror)
    except json.decoder.JSONDecodeError as save_json_error:
        print_error("JSON decode error", save_json_error.msg)
        print("Trying to parse JSON string:")
        print(json_content)


def save_lines_to_file(lines, output_file_path) -> None:
    """
    Saves lines to output file
    :param lines:
    :type lines: list
    :param output_file_path:
    :type output_file_path: str
    :return:
    :rtype: None
    """
    try:
        with open(output_file_path, 'w') as file:
            for line in lines:
                file.write("%s\n" % line)
    except OSError as os_error:
        print_error("Error:", os_error.strerror)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='JSON file array splitter into files')

    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('-i', '--input', help='Input JSON file path', required=True,
                               dest="input_file_path")
    requiredNamed.add_argument('-a', '--array', help='JSON array key', required=True,
                               dest="json_array_key")
    requiredNamed.add_argument('-o', '--output', help='Output directory path', required=False,
                               dest="output_dir_path")
    requiredNamed.add_argument('-j', '--json_path', help='JSON path to value that should be used for output file name',
                               required=False, dest="json_path")
    requiredNamed.add_argument('-s', '--separator',
                               help='Character used in string value (loaded with JSON path) as separator. '
                                    'After splitting value the first part will be used as directory name and '
                                    'the second part as filename',
                               required=False, dest="separator")
    requiredNamed.add_argument('-f', '--file',
                               help='Output file path to save all processed sections',
                               required=False, dest="file")

    args = parser.parse_args()

    processed_sections = []
    json_path = args.json_path.split("/")

    print_info("Loading file", args.input_file_path)
    try:
        with open(args.input_file_path, 'r') as file:
            data = json.load(file)
    except OSError as os_error:
        print_error("Error", os_error.strerror)
    except json.decoder.JSONDecodeError as save_json_error:
        print_error("JSON decode error", save_json_error.msg)

    if args.json_array_key:
        data_array = data[args.json_array_key]
    else:
        data_array = data

    print_info("Saving files:")

    for data_array_element in data_array:

        element = data_array_element

        for key in json_path:
            element = element[key]

        if args.separator in element:
            splitted = element.split(args.separator)
        else:
            splitted = None

        output_dir_path = args.output_dir_path

        if splitted and len(splitted) > 1:
            if output_dir_path:
                output_dir_path = "%s/%s" % (output_dir_path, splitted[0])
            else:
                output_dir_path = splitted[0]

        if not os.path.exists(output_dir_path):
            os.makedirs(output_dir_path)

        if splitted:
            if output_dir_path:
                output_file_path = "%s/%s.json" % (output_dir_path, args.separator.join(splitted[1:]))
            else:
                output_file_path = "%s/%s.json" % (splitted[0], args.separator.join(splitted[1:]))
        else:
            if output_dir_path:
                output_file_path = "%s/%s.json" % (output_dir_path, element)
            else:
                output_file_path = "%s.json" % element

        print(output_file_path)
        save_json_file(data_array_element, output_file_path)
        processed_sections.append("%%file:%s%%" % output_file_path)

    if args.file:
        processed_sections.sort()
        print(type(processed_sections))
        save_lines_to_file(processed_sections, args.file)

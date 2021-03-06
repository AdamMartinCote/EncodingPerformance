################################################################################
# INTERFACE:
# bytepair_encode(str)
# bytepair_decode(coded_message_object)
# bytepair_encode_file(filepath)
################################################################################
import matplotlib.pyplot as py
import numpy as np
from collections import OrderedDict


def bytepair_get_results(filepath):
    initial_message_obj = bytepair_file_to_message_object(filepath)
    encoded_message_obj = bytepair_encode_internal(initial_message_obj)

    initial_size = len(initial_message_obj["bytes"])
    compressed_size = len(encoded_message_obj["bytes"])

    compression_rate = 1 - (compressed_size / float(initial_size))
    nb_replacements = len(encoded_message_obj["replacements"])
    stop_reason = encoded_message_obj["stop_reason"]

    return OrderedDict({"filename": filepath,
                        "in_size": initial_size,
                        "out_size": compressed_size,
                        "compression_rate": compression_rate,
                        "nb_replacements":nb_replacements,
                        "stop_reason": stop_reason})


def bytepair_file_to_message_object(filepath):
    bytes_list = None
    if filepath.endswith(".jpeg") or filepath.endswith("raw"):
        bytes_list = bytepair_load_image(filepath)
    else:
        with open(filepath) as f:
            message = f.read()
            bytes_list = list(map(ord, message))
    return {"bytes": bytes_list, "replacements":[]}


def bytepair_encode_image(filepath):
    message_object = { "bytes": bytepair_image_to_bytes(filepath), "replacements":list()}


def rgb2gray(rgb):
    return np.dot(rgb[:,:], [0.299, 0.587, 0.114])


def bytepair_load_image(filepath):

    imagelue = py.imread(filepath)
    image=imagelue.astype('float')
    image=rgb2gray(image)
    imageout=image.astype('uint8').tolist()
    single_list = []
    for l in imageout:
        single_list += l

    return single_list


def test_image_to_int_list():
    image = bytepair_load_image("../../res/cats_are_evil.jpeg")
    print(image[0:10])
    print(len(image))


def bytepair_encode_file(filepath):
    with open("../../res/lipsum.txt") as f:
        string = f.read()
    return bytepair_encode(string)


def bytepair_compression_rate_file(filepath):
    if filepath.endswith(".jpeg"):
        return bytepair_compression_rate_img(filepath)
    else:
        return bytepair_compression_rate_txt(filepath)


def bytepair_compression_rate_txt(filepath):
    with open(filepath) as f:
        message = f.read()
        return bytepair_compression_rate_str(message)


def bytepair_compression_rate_img(filepath):
    img_int_list = bytepair_load_image(filepath)
    initial_size = len(img_int_list)
    cmo = {"bytes":img_int_list, "replacements":[]}
    cmo = bytepair_encode_internal(cmo)
    compressed_size = len(cmo["bytes"])
    return compressed_size / float(initial_size)


def bytepair_compression_rate_str(input_string):
    cmo = bytepair_encode_string(input_string)
    coded_length = len( cmo["bytes"] )
    input_length = len(input_string)
    return coded_length / float(input_length)


def bytepair_encode_string(input_string):
    message_object = { "bytes":list(map(ord, input_string)),
                       "replacements":[]}

    return bytepair_encode_internal(message_object)


def bytepair_encode_internal(message_object):
    current_object = message_object
    stop_reason = "None"
    while True:
        pair = get_most_frequent_pair(current_object["bytes"])
        if pair[1] == 1:
            stop_reason = "pairs"
            break
        unused_chars = get_unused_chars(current_object["bytes"])
        if not unused_chars:
            stop_reason = "unused_bytes"
            break
        replacement_char = unused_chars.pop()

        next_message = replace_pair(current_object["bytes"], pair[0], replacement_char)
        new_replacements = current_object["replacements"] + [(pair[0], replacement_char)]
        current_object = { "bytes": next_message, "replacements":new_replacements}

    return { "bytes": next_message, "replacements":new_replacements, "stop_reason":stop_reason}


def bytepair_encoded_msg_as_str(coded_message_object):
    return ''.join(map(chr,coded_message_object["bytes"]))


def bytepair_decode_string(coded_message_object):
    bytes = coded_message_object["bytes"]
    repls = coded_message_object["replacements"]
    for rep in reversed(coded_message_object["replacements"]):
        bytes = un_replace_pair(bytes, rep)

    return ''.join(map(chr, bytes))


def un_replace_pair(bytes, replacement):
    output = []
    length = len(bytes)
    i = 0
    while i < length:
        c = bytes[i]
        p = tuple(bytes[i:i+2])

        if c == replacement[1]:
            output += list(replacement[0])
            i += 1
        else:
            output.append(c)
            i += 1
    return output


def test_bytepair_encode():
    with open("./small_text.txt") as input_file:
        file_content = input_file.read()
        print(file_content)
        print(type(file_content))


def get_pair_frequencies(string):
    pair_frequencies = {}
    for i in range(len(string) - 2):

        pair = tuple(string[i:i+2])

        if pair in pair_frequencies:
            pair_frequencies[pair] += 1
        else:
            pair_frequencies[pair] = 1

    return pair_frequencies


def test_get_pair_frequencies():
    pair_frequencies = get_pair_frequencies(test_string)
    print(pair_frequencies)


def get_most_frequent_pair(string):
    pair_frequencies = get_pair_frequencies(string)

    max_freq = 0
    most_frequent = None

    for p in pair_frequencies:
        freq = pair_frequencies[p]
        if freq > max_freq:
            most_frequent = p
            max_freq = freq
    return (most_frequent, max_freq)


def test_get_most_frequent_pair():
    mfp = get_most_frequent_pair(test_string)
    print(get_pair_frequencies(test_string))
    print("most frequent pair " + str(mfp))


def do_first_pass(string):
    pair = get_most_frequent_pair(string)
    replacement_char = get_unused_chars(string).pop()
    return (replace_pair(string, pair, replacement_char), [(pair, replacement_char)])


def get_unused_chars(string):
    possible_chars = set(range(256))
    used_chars = set(string)
    return possible_chars - used_chars


def test_get_unused_chars():
    print(get_unused_chars([81,83,82]))


def replace_pair(string, pair, replacement):
    output = []
    length = len(string)
    i = 0
    while i < length:
        c = string[i]
        p = tuple(string[i:i+2])

        # print("replacement : ".format(replacement))
        if p == pair:
            output.append(replacement)
            i += 2
        else:
            output.append(c)
            i += 1
    return output


def test_replace_pair():
    print(test_string)
    print(replace_pair(test_string, (65,83), 8))


def test_bytepair_encode_decode():
    with open("../../res/lipsum.txt") as f:
        string = f.read()
        print(string)

    cmo = bytepair_encode_string(string)
    print(''.join(map(chr, cmo["bytes"])))
    decoded = bytepair_decode_string(cmo)
    print(decoded)


if __name__ == "__main__":
    test_string = "ASDASDASKSA:DSKDASDFHFDLJLSGDNCMS<DVB:JK:J"
    # print(test_string)

    # print(test_string)
    # test_get_most_frequent_pair()
    # test_bytepair_encode():
    # test_get_pair_frequencies():
    # test_get_byte_set():
    # test_get_most_frequent_pair():
    #test_get_unused_chars()
    #test_replace_pair()
    # print(do_first_pass(test_string))
    test_bytepair_encode_decode()
    # test_image_to_int_list()

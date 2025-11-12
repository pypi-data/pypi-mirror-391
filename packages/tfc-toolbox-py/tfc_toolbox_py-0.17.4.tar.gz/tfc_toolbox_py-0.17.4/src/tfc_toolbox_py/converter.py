def binary_to_text(binary_str):
    """
    Converte binary to ascii.
    """
    binary_str = binary_str.replace(' ', '').replace('0x', '').replace('\t', '').replace('\n', '')
    return ''.join(chr(int(binary_str[i * 8:i * 8 + 8], 2)) for i in range(len(binary_str) // 8))
 
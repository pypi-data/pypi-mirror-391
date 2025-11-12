import re
import os

def _parse_verilog_ports(port_definition):
    """
    解析Verilog模块的端口定义
    """
    port_pattern = r'(input|output|inout)\s*(reg|wire)?\s*(\[\d+:\d+\])?\s*(\w+)'
    ports = []

    for line in port_definition.split('\n'):
        line = line.strip().rstrip(',')
        if not line:
            continue

        match = re.search(port_pattern, line)
        if match:
            direction = match.group(1)
            data_type = match.group(2) or 'wire'
            width = match.group(3)
            name = match.group(4)
            ports.append({
                'name': name,
                'direction': direction,
                'width': width,
                'type': data_type
            })

    return ports

def _generate_instance(module_name, instance_name, ports, connections=None):
    """
    生成Verilog例化代码
    """
    if connections is None:
        # 如果没有提供连接，默认使用端口名作为连接信号
        connections = {port['name']: port['name'] for port in ports}

    conn_lines = []
    for port in ports:
        port_name = port['name']
        connection = connections.get(port_name, port_name)
        conn_lines.append(f"    .{port_name}({connection})")

    conn_str = " (\n" + ",\n".join(conn_lines) + "\n  )"

    return f"{module_name} {instance_name}{conn_str};"


def generate_instances_from_file(module_file, connections=None):
    """
    从Verilog文件生成例化代码
    使用示例：
    print(generate_instances_from_file("my_module.v"))
    """
    with open(module_file, 'r') as f:
        content = f.read()

    # 简单提取模块端口定义(实际项目中应该使用更可靠的解析方法)
    port_section = re.search(r'module\s+\w+\s*\((.*?)\);', content, re.DOTALL)
    if not port_section:
        raise ValueError("无法找到模块端口定义")

    # 解析Verilog模块的端口定义
    ports = _parse_verilog_ports(port_section.group(1))
    module_name = re.search(r'module\s+(\w+)', content).group(1)

    return _generate_instance(module_name, "u_" + module_name, ports, connections)


def generate_instances_from_string(connections=None):
    """
    从Verilog的模块定义和端口声明生成例化代码
    使用示例：
    print(generate_instances_from_string())
    粘贴如下代码：
    ```Verilog
    module pll(
        input sys_clk,
        input sys_rst_n,
        output clk_out_100,
        output clk_out_50,
        output clk_out_100_phase,
        output clk_out_25,
        output locked
    );
    ```
    """

    lines = []
    # 循环获取用户输入，获取模块定义和端口声明
    print("请在下方粘贴模块定义和端口声明：")
    while True:
        line = input()
        lines.append(line)
        if ";" in line:
            # 生成空行
            print("")
            print("")
            break

    port_string = "\n".join(lines)

    # 简单提取模块端口定义
    port_section = re.search(r'module\s+\w+\s*\((.*?)\);', port_string, re.DOTALL)
    if not port_section:
        raise ValueError("无法找到模块端口定义")

    # 解析Verilog模块的端口定义
    ports = _parse_verilog_ports(port_section.group(1))
    module_name = re.search(r'module\s+(\w+)', port_string).group(1)

    print("例化代码如下：")
    instance_code = _generate_instance(module_name, "u_" + module_name, ports, connections)
    return instance_code

if __name__ == '__main__':
    print(generate_instances_from_string())
    os.system('pause')
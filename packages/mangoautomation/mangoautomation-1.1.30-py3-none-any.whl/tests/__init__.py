import os


def change_file_extensions(directory, new_extension='.pyx'):
    """
    将指定目录及其子目录中所有文件的后缀改为指定的新后缀

    Args:
        directory (str): 要处理的根目录路径
        new_extension (str): 新的文件后缀，默认为'.py'
    """
    # 确保新后缀以点开头
    if not new_extension.startswith('.'):
        new_extension = '.' + new_extension

    # 计数器
    changed_count = 0
    error_count = 0

    # 遍历目录及其所有子目录
    for root, dirs, files in os.walk(directory):
        for filename in files:
            # 获取文件完整路径
            file_path = os.path.join(root, filename)

            try:
                # 分离文件名和扩展名
                name, ext = os.path.splitext(filename)

                # 如果扩展名已经是要改的后缀，则跳过
                if ext == new_extension:
                    continue

                # 构建新的文件名
                new_filename = name + new_extension
                new_file_path = os.path.join(root, new_filename)

                # 重命名文件
                os.rename(file_path, new_file_path)
                print(f"已重命名: {filename} -> {new_filename}")
                changed_count += 1

            except Exception as e:
                print(f"错误: 无法重命名 {filename} - {str(e)}")
                error_count += 1

    print(f"\n操作完成!")
    print(f"成功重命名: {changed_count} 个文件")
    print(f"失败: {error_count} 个文件")


def main():
    # 获取用户输入的目录路径
    directory = input("请输入要处理的目录路径: ").strip()

    # 检查目录是否存在
    if not os.path.exists(directory):
        print("错误: 指定的目录不存在!")
        return

    if not os.path.isdir(directory):
        print("错误: 指定的路径不是一个目录!")
        return

    # 确认操作
    confirm = input(f"这将把目录 '{directory}' 中的所有文件后缀改为 '.py'，包括子目录。确认执行? (y/n): ")

    if confirm.lower() in ['y', 'yes', '是']:
        change_file_extensions(directory)
    else:
        print("操作已取消。")


if __name__ == "__main__":
    main()
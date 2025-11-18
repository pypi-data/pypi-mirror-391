from cpp_module import cpp_extension


def main():
    # 调用C++函数
    result = cpp_extension.add(5, 3)
    print(f"5 + 3 = {result}")  # 输出: 5 + 3 = 8

    # 使用C++类
    processor = cpp_extension.TextProcessor("MyProcessor")
    upper_text = processor.to_upper("Hello, World!")
    print(upper_text)  # 输出: HELLO, WORLD!
    print(processor.name)  # 输出: MyProcessor


if __name__ == "__main__":
    main()

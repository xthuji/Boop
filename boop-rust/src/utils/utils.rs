//! 工具函数模块

pub fn format_text(text: &str) -> String {
    // 格式化文本
    text.to_string()
}

pub fn validate_input(input: &str) -> bool {
    // 验证输入
    !input.is_empty()
}

pub fn trim_whitespace(text: &str) -> String {
    // 去除空白字符
    text.trim().to_string()
}

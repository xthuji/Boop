//! 日志模块

pub fn init() {
    // 初始化日志系统
    println!("日志系统初始化");
}

pub fn info(message: &str) {
    println!("[INFO] {}", message);
}

pub fn error(message: &str) {
    println!("[ERROR] {}", message);
}

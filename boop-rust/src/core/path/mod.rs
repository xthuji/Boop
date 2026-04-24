//! 路径模块

use std::path::PathBuf;

pub fn get_app_data_path() -> PathBuf {
    // 获取应用数据路径
    PathBuf::from("./data")
}

pub fn get_scripts_path() -> PathBuf {
    // 获取脚本路径
    PathBuf::from("./scripts")
}

pub fn get_config_path() -> PathBuf {
    // 获取配置文件路径
    get_app_data_path().join("config.json")
}

//! 脚本管理器

use std::path::PathBuf;

pub struct ScriptManager {
    scripts_path: PathBuf,
}

impl ScriptManager {
    pub fn new(scripts_path: PathBuf) -> Self {
        Self {
            scripts_path,
        }
    }

    pub fn load_scripts(&self) -> Vec<String> {
        // 加载脚本列表
        vec![
            "align_code.py".to_string(),
            "calculate_size.py".to_string(),
            "case_to_camel.py".to_string(),
        ]
    }

    pub fn get_script_path(&self, script_name: &str) -> PathBuf {
        // 获取脚本路径
        self.scripts_path.join(script_name)
    }
}

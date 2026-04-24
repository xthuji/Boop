//! 脚本元数据

pub struct ScriptMetadata {
    pub name: String,
    pub description: String,
    pub author: String,
    pub version: String,
}

impl ScriptMetadata {
    pub fn new(name: String, description: String, author: String, version: String) -> Self {
        Self {
            name,
            description,
            author,
            version,
        }
    }

    pub fn from_script(script_path: &str) -> Self {
        // 从脚本文件中提取元数据
        Self {
            name: script_path.to_string(),
            description: "脚本描述".to_string(),
            author: "未知作者".to_string(),
            version: "1.0.0".to_string(),
        }
    }
}

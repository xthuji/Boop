//! 核心模块

pub mod config;
pub mod log;
pub mod path;
pub mod script;

pub use config::Config;
pub use log::{init, info, error};
pub use path::{get_app_data_path, get_scripts_path, get_config_path};
pub use script::{ScriptExecutor, ScriptManager, ScriptMetadata};

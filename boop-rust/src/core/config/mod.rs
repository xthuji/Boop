//! 配置模块

pub struct Config {
    pub window_width: u32,
    pub window_height: u32,
    pub status_bar_height: u32,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            window_width: 800,
            window_height: 600,
            status_bar_height: 24,
        }
    }
}

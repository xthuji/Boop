//! 首选项窗口模块

use iced::widget::{column, text, button};
use iced::{Element, Length, Task};

pub struct Preferences {
    // 首选项设置
}

#[derive(Debug, Clone)]
pub enum PreferencesMessage {
    // 首选项消息
}

impl Preferences {
    pub fn new() -> Self {
        Self {}
    }

    pub fn update(&mut self, _message: PreferencesMessage) -> Task<PreferencesMessage> {
        Task::none()
    }

    pub fn view(&self) -> Element<'_, PreferencesMessage> {
        column!(
            text("首选项").size(18),
            text("设置选项将在这里显示"),
            button("确定").width(Length::Fixed(100.0))
        )
        .padding(20)
        .spacing(10)
        .into()
    }
}

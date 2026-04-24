//! 脚本选择器模块

use iced::widget::{column, text, button, row};
use iced::{Element, Length, Task};

pub struct ScriptPicker {
    pub scripts: Vec<String>,
    pub selected_script: Option<usize>,
}

#[derive(Debug, Clone)]
pub enum ScriptPickerMessage {
    ScriptSelected(usize),
    RunScript,
    Cancel,
}

impl ScriptPicker {
    pub fn new(scripts: Vec<String>) -> Self {
        Self {
            scripts,
            selected_script: None,
        }
    }

    pub fn update(&mut self, message: ScriptPickerMessage) -> Task<ScriptPickerMessage> {
        match message {
            ScriptPickerMessage::ScriptSelected(index) => {
                self.selected_script = Some(index);
            }
            ScriptPickerMessage::RunScript => {
                // 运行选中的脚本
            }
            ScriptPickerMessage::Cancel => {
                // 取消
            }
        }
        
        Task::none()
    }

    pub fn view(&self) -> Element<'_, ScriptPickerMessage> {
        let mut script_list = column![];
        
        for (index, script) in self.scripts.iter().enumerate() {
            script_list = script_list.push(
                button(text(script)).width(Length::Fill).on_press(ScriptPickerMessage::ScriptSelected(index))
            );
        }
        
        script_list = script_list
            .width(Length::Fill)
            .height(Length::Fill);

        column!(
            text("选择脚本").size(18),
            script_list,
            row!(
                button("运行").width(Length::Fixed(100.0)).on_press(ScriptPickerMessage::RunScript),
                button("取消").width(Length::Fixed(100.0)).on_press(ScriptPickerMessage::Cancel)
            )
            .spacing(10)
            .width(Length::Fill)
        )
        .padding(20)
        .spacing(10)
        .width(Length::Fixed(400.0))
        .height(Length::Fixed(400.0))
        .into()
    }
}

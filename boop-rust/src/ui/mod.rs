//! UI模块

pub mod editor;
pub mod main_window;
pub mod preferences;
pub mod script_picker;

pub use editor::{Editor, EditorMessage, StatusBar, StatusBarMessage};
pub use main_window::{MainWindow, MainWindowMessage};
pub use preferences::{Preferences, PreferencesMessage};
pub use script_picker::{ScriptPicker, ScriptPickerMessage};

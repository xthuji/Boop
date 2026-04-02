import tkinter as tk
import platform

class StateTester:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"Tkinter Event State Tester ({platform.system()})")
        self.root.geometry("500x400")

        self.label = tk.Label(self.root, text="请按下组合键 (如 Alt+A, Cmd+S, Shift+Tab)", font=("Arial", 12), pady=20)
        self.label.pack()

        # 用于显示结果的文本框
        self.result_text = tk.Text(self.root, height=15, width=60)
        self.result_text.pack(padx=20, pady=10)

        # 绑定任意按键事件
        self.root.bind("<Key>", self.report_event)
        
        # 预设的常用位定义 (基于 Tcl/Tk 标准)
        self.masks = {
            "Shift": 0x0001,
            "Lock (Caps)": 0x0002,
            "Control": 0x0004,
            "Mod1 (Cmd/Alt)": 0x0008,
            "Mod2 (Opt/Alt)": 0x0010,
            "Mod3": 0x0020,
            "Mod4": 0x0040,
            "Mod5": 0x0080,
            "Button1": 0x0100,
            "Button2": 0x0200,
            "Button3": 0x0400
        }

    def report_event(self, event):
        state = event.state
        
        # 解析当前 state 包含了哪些已知的位
        active_masks = [name for name, mask in self.masks.items() if state & mask]
        
        output = [
            f"Keysym: {event.keysym}",
            f"Char:   {repr(event.char)}",
            f"State (Dec): {state}",
            f"State (Hex): {hex(state)}",
            f"State (Bin): {bin(state)}",
            f"Active Masks: {', '.join(active_masks) if active_masks else 'None'}",
            "-" * 30
        ]
        
        self.result_text.insert("1.0", "\n".join(output) + "\n")
        print(f"Key: {event.keysym} | State: {hex(state)} | Masks: {active_masks}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    print(f"操作系统: {platform.system()}")
    print("窗口已启动，请在窗口内操作按键...")
    StateTester().run()
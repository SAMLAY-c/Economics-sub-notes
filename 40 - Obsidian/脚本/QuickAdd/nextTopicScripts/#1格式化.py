import tkinter as tk
from tkinter import filedialog, messagebox

def format_markdown_notes(markdown_text):
    """
    Processes Markdown text to remove a blank line between a line starting
    with "## " or "### " and a subsequent line starting with "  #1".

    Args:
        markdown_text (str): The input Markdown text as a single string.

    Returns:
        str: The processed Markdown text.
    """
    lines = markdown_text.splitlines()
    processed_lines = []
    i = 0
    n = len(lines)

    while i < n:
        current_line = lines[i]
        # Check for the pattern:
        # 1. Current line starts with "## " OR "### "
        # 2. There is a next line (i+1)
        # 3. The next line is blank
        # 4. There is a line after the blank line (i+2)
        # 5. The line after the blank line starts with "  #1"
        if (current_line.startswith("## ") or current_line.startswith("### ")) and \
           (i + 2 < n) and \
           lines[i+1].strip() == "" and \
           lines[i+2].startswith("  #1"):
            
            processed_lines.append(current_line)  # Add the "## " or "### " line
            # Skip the blank line (lines[i+1])
            processed_lines.append(lines[i+2])    # Add the "  #1" line (moved up)
            i += 3 # Move index past the three lines processed (header, blank, #1)
        else:
            processed_lines.append(current_line)
            i += 1
            
    return "\n".join(processed_lines)

def main():
    # Create the main Tkinter window but hide it, as we only need dialogs
    root = tk.Tk()
    root.withdraw()

    # Ask the user to select an input Markdown file
    input_filepath = filedialog.askopenfilename(
        title="选择要处理的Markdown文件",
        filetypes=(("Markdown 文件", "*.md *.markdown"), ("所有文件", "*.*"))
    )

    if not input_filepath:
        messagebox.showinfo("提示", "未选择输入文件，程序已退出。")
        return

    # Confirm before overwriting the original file
    # Current date for context in message:
    # (This part is commented out as it uses the context of my execution,
    #  but you could uncomment and adapt if you want a timestamp in the message)
    # from datetime import datetime
    # current_timestamp_for_message = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    confirm_overwrite = messagebox.askyesno(
        "确认覆盖操作",
        f"您确定要直接修改并覆盖原始文件吗？\n\n文件路径:\n{input_filepath}\n\n强烈建议在操作前备份此文件。",
        icon='warning' # Add a warning icon
    )

    if not confirm_overwrite:
        messagebox.showinfo("操作取消", "文件未被修改。")
        return

    try:
        # Read the original content first
        with open(input_filepath, 'r', encoding='utf-8') as f_in:
            original_content = f_in.read()
        
        processed_content = format_markdown_notes(original_content)
        
        # Check if any changes were actually made to avoid unnecessary writes
        # or to notify user if no relevant patterns were found.
        if original_content == processed_content:
            messagebox.showinfo("提示", "文件内容未发生变化，无需覆盖。\n（可能未找到需要修改的格式）")
            return

        # If changes were made, then overwrite the original file
        with open(input_filepath, 'w', encoding='utf-8') as f_out:
            f_out.write(processed_content)
        
        messagebox.showinfo("成功", f"文件已成功处理并覆盖保存:\n{input_filepath}")

    except FileNotFoundError: # Should ideally not happen if askopenfilename worked
        messagebox.showerror("错误", f"错误: 输入文件 '{input_filepath}' 未找到。")
    except Exception as e:
        messagebox.showerror("错误", f"处理文件时发生错误: {e}")

if __name__ == "__main__":
    main()
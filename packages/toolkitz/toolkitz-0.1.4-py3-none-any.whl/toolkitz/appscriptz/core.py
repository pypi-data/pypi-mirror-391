""" 脚本交互 """
from datetime import datetime
import subprocess
from llama_index.core import PromptTemplate
import shlex
from promptlibz.core import PromptManager,PromptRepository
from llmada.core import BianXieAdapter
import textwrap # Add this line

def generate_schedule(text: str, habit: str = "") -> str:
    """
    使用 GPT 模型生成日程安排。

    Args:
        text (str): 用于生成日程的输入文本。
        habit (str, optional): 习惯描述，用于定制日程。默认为空字符串。

    Returns:
        str: 生成的日程安排结果。
    """
    llm = BianXieAdapter()
    llm.set_model("o3-mini")
    repository = PromptRepository()
    manager = PromptManager(repository)
    template = manager.get_prompt("GenerateSchedule")
    current_utc_time = str(datetime.today())[:-7]
    prompt = template.format(text=text,habit=habit,current_utc_time = current_utc_time)
    completion = llm.product(prompt)
    return completion


def run_applescript(script: str) -> str:
    """
    运行 AppleScript 脚本。

    Args:
        script (str): 要执行的 AppleScript 脚本字符串。

    Returns:
        str: 脚本执行的标准输出，已去除末尾换行符。
    """
    result = subprocess.run(['osascript', '-e', script],capture_output=True,check=False)
    return result.stdout.decode().replace('\n','')


class Notes():

    @staticmethod
    def write(content: str) -> str:
        """
        将内容写入 macOS 备忘录应用。

        Args:
            content (str): 要写入备忘录的内容。

        Returns:
            str: AppleScript 执行结果。
        """
        content = content.replace("\n",",").replace('- [ ]','')
        # 构造 AppleScript 脚本  TODO 解决无法换行问题
        script = f'''
        tell application "Notes"
            activate
            -- 获取默认账户
            set defaultAccount to default account
            -- 创建一个新的备忘录
            set newNote to make new note in defaultAccount
            -- 写入文本信息到备忘录
            set body of newNote to "{content}"
            -- 显示新创建的备忘录
            show newNote
        end tell
        '''
        return run_applescript(script)

class Reminder():

    @staticmethod
    def write_reminder(
                       content: str,
                       list_name: str = "Reminders",
                       due_date: str = None,
                       priority: int = None,
                       notes: str = "") -> str:
        """
        在 macOS 提醒事项应用中创建新的提醒。

        Args:
            content (str): 提醒事项的主要内容。
            list_name (str, optional): 提醒事项所属的列表名称。默认为 "Reminders"。
            due_date (str, optional): 提醒事项的到期日期，格式为 "YYYY年MM月DD日HH:MM"。默认为 None。
            priority (int, optional): 提醒事项的优先级 (1-4)。1 为最高优先级，4 为最低优先级。默认为 None。
            notes (str, optional): 提醒事项的备注信息。默认为空字符串。

        Returns:
            str: AppleScript 执行结果。
        """
        # 预处理内容
        processed_content = content.replace('\n', ' ').replace('- [ ]', '').strip()
        processed_content = processed_content.replace('"', '\\"')
        notes = notes.replace('"', '\\"')
        
        # 构建属性字典
        properties = [f'name:"{processed_content}"']
        if due_date:
            properties.append(f'due date:(date "{due_date}")')
        if priority and 1 <= priority <= 4:
            properties.append(f'priority:{priority}')
        if notes:
            properties.append(f'body:"{notes}"')
        
        # 构造AppleScript
        script = f'''
        tell application "Reminders"
            activate
            set targetList to list "{list_name}"
            set newReminder to make new reminder in targetList with properties {{{', '.join(properties)}}}
            show newReminder
        end tell
        '''
        return run_applescript(script)

class Calulate():
    @staticmethod
    def update(
               start_date: str = "2025年4月25日8:00",
               end_date: str = "2025年4月25日9:00",
               event_name: str = "会议") -> str:
        """
        在 macOS 日历应用中创建或更新一个事件。

        Args:
            start_date (str, optional): 事件的开始日期和时间，格式为 "YYYY年MM月DD日HH:MM"。
                                        默认为 "2025年4月25日8:00"。
            end_date (str, optional): 事件的结束日期和时间，格式为 "YYYY年MM月DD日HH:MM"。
                                      默认为 "2025年4月25日9:00"。
            event_name (str, optional): 事件的名称或标题。默认为 "会议"。

        Returns:
            str: AppleScript 执行结果。
        """
        script = PromptTemplate(template='''
        tell application "Calendar"
            activate
            tell calendar "Obsidian" -- 或者 tell first calendar
                -- nih
                -- 假设您已经将开始时间、结束时间和标题存储在变量中
                set theStartDate to date "{start_date}" -- 示例日期时间
                set theEndDate to date "{end_date}" -- 示例日期时间
                set theSummary to "{event_name}" -- 示例标题
                make new event with properties {summary:theSummary, start date:theStartDate, end date:theEndDate}
            end tell
        end tell
        ''')

        # 构造 AppleScript 脚本
        script = script.format(start_date=start_date,end_date=end_date,event_name=event_name)

        return run_applescript(script)

    @staticmethod
    def delete(event_name: str) -> str:
        """
        从 macOS 日历应用中删除指定名称的事件。

        Args:
            event_name (str): 要删除的事件的名称。

        Returns:
            str: AppleScript 执行结果。
        """
        script = PromptTemplate(template='''
        tell application "Calendar"
            -- 设置你要删除的日程名称
            set eventNameToRemove to "{event_name}" -- **这里已经设置为“会议”**
            
            -- 遍历所有的日历
            repeat with i from 1 to (count of calendars)
                set cal to item i of calendars
                
                -- 获取当前日历的所有日程到一个变量中
                set allEvents to every event in cal
                
                -- 从后往前遍历日程列表
                repeat with j from (count of allEvents) to 1 by -1
                    set ev to item j of allEvents
                    -- 检查日程的摘要（名称）是否匹配
                    if summary of ev is equal to eventNameToRemove then
                        -- 如果匹配，删除该日程
                        delete ev
                        display notification "已删除日程: " & eventNameToRemove & " (来自 " & name of cal & ")" with title "Calendar Script"
                    end if
                end repeat
            end repeat
            
        end tell
        ''')

        # 构造 AppleScript 脚本
        script = script.format(event_name=event_name)

        # 执行 AppleScript 脚本
        return run_applescript(script)


class Display():
    @staticmethod
    def multiple_selection_boxes(
                                 prompt_text: str = "请从下面的列表中选择一项：",
                                 list_title: str = "请选择",
                                 options: list[str] = None,
                                 default_option: str = None) -> str | None:
        """
        使用 AppleScript 在 macOS 上显示一个列表选择框，并返回用户的选择。

        Args:
            prompt_text (str, optional): 显示在列表上方的提示信息。默认为 "请从下面的列表中选择一项："。
            list_title (str, optional): 选择框窗口的标题。默认为 "请选择"。
            options (list[str], optional): 供用户选择的字符串列表。如果为 None，则使用默认选项。
            default_option (str, optional): 默认选中的项目。如果提供，该项目必须存在于 options 列表中。

        Returns:
            str | None: 用户选择的项目字符串。如果用户取消选择或发生错误，则返回 None。
        """
        import sys
        if sys.platform != 'darwin':
            print("错误：此功能仅在 macOS 上可用。")
            return None

        if options is None:
            options = ["选项 A", "选项 B", "选项 C", "另一个选项"] # 默认选项

        # 将 Python 列表转换为 AppleScript 列表字符串: {"item1", "item2", ...}
        applescript_list = '{' + ', '.join([f'"{item}"' for item in options]) + '}'

        # 构建 AppleScript
        script_template = """
        try
            set myList to {applescript_list}
            set thePrompt to "{prompt_text}"
            set theTitle to "{list_title}"
            {default_choice_script}
            set theChoice to choose from list myList with title theTitle with prompt thePrompt & default_items_script
            -- 检查用户是否点击了取消按钮
            if theChoice is false then
                error number -128 -- 引发标准取消错误
            else
                -- 返回选择的第一个项目 (choose from list 返回列表)
                return item 1 of theChoice
            end if
        on error number -128
            -- 捕获取消错误，可以返回特定值或让 Python 处理异常
            return "USER_CANCELLED" -- 返回一个特殊标记
            -- 或者你可以不处理，让 osascript 返回非零退出码
            -- error number -128
        end try
        """

        default_choice_script = ""
        default_items_script = ""
        if default_option and default_option in options:
            default_choice_script = f'set defaultChoice to {{"{default_option}"}}'
            default_items_script = f'default items defaultChoice'

        script = textwrap.dedent(script_template).format(
            applescript_list=applescript_list,
            prompt_text=prompt_text,
            list_title=list_title,
            default_choice_script=default_choice_script,
            default_items_script=default_items_script
        )

        try:
            # 不需要 shlex.quote
            result = subprocess.run(
                ['osascript', '-e', script],
                check=True,          # 如果 osascript 返回非零则抛出异常
                capture_output=True, # 捕获 stdout/stderr
                text=True,           # 将输出解码为文本
                encoding='utf-8'     # 指定编码
            )
            output = result.stdout.strip()

            
            if output == "USER_CANCELLED":
                print("用户取消了选择。")
                return None
            else:
                return output # 返回用户的选择
        except subprocess.CalledProcessError as e:
            # osascript 执行失败或返回错误码 (例如，如果我们在 AppleScript 中直接 error -128)
            # 检查 stderr 获取更多信息
            error_message = e.stderr.strip()
            if "-128" in error_message: # 检查是否是用户取消的标准错误代码
                print("用户取消了选择 (通过错误码捕获)。")
            else:
                print(f"执行 AppleScript 时出错: {e}")
                print(f"错误详情: {error_message}")
            return None
        except FileNotFoundError:
            print("错误: 'osascript' 命令未找到。请确保你在 macOS 上运行。")
            return None
        except Exception as e:
            print(f"发生意外错误: {e}")
            return None

    @staticmethod
    def get_multi_level_selection_simple(
                                         warehouse_list: list[str],
                                         action_list: list[str]) -> str:
        """
        通过调用 AppleScript 在 macOS 上显示多层级 UI 对话框来收集用户输入。
        此版本为极简版，移除了所有错误处理。如果用户点击"取消"，脚本会失败。

        Args:
            warehouse_list (list[str]): 字符串列表，用于仓库选择。
            action_list (list[str]): 字符串列表，用于动作类型选择。

        Returns:
            str: 格式为 "动作:仓库:标题:描述" 的字符串。
        """
        # 1. 将Python列表格式化为AppleScript能识别的列表字符串
        # 例如: ['server', 'client'] -> '{"server", "client"}'
        as_warehouse_list = '{' + ', '.join(f'"{w}"' for w in warehouse_list) + '}'
        as_action_list = '{' + ', '.join(f'"{a}"' for a in action_list) + '}'

        # 2. 构建最核心的AppleScript代码
        # 注意：这里没有任何 'try' 或 'if' 来处理取消操作
        applescript_code = f'''
        -- 步骤 1: 选择仓库
        set selectedWarehouse to item 1 of (choose from list {as_warehouse_list} with prompt "步骤 1/4: 请选择仓库")

        -- 步骤 2: 选择动作类型
        set selectedAction to item 1 of (choose from list {as_action_list} with prompt "步骤 2/4: 请选择动作类型")

        -- 步骤 3: 输入标题
        set titleText to text returned of (display dialog "步骤 3/4: 请输入标题" default answer "")

        -- 步骤 4: 输入详细描述
        set descriptionText to text returned of (display dialog "步骤 4/4: 请输入详细描述" default answer "")

        -- 拼接并返回最终结果
        return selectedAction & ":" & selectedWarehouse & ":" & titleText & ":" & descriptionText
        '''

        # 3. 执行AppleScript并捕获其标准输出
        process = subprocess.run(
            ["osascript", "-e", applescript_code],
            capture_output=True,  # 捕获输出
            text=True             # 以文本模式处理
        )

        # 4. 返回AppleScript脚本的输出结果，并去除末尾的换行符
        return process.stdout.strip()


    @staticmethod
    def display_dialog(
                       title: str,
                       text: str,
                       buttons: str = '"OK"',
                       button_cancel: bool = True) -> str | None:
        """
        使用 AppleScript 在 macOS 上显示一个简单的对话框。

        Args:
            title (str): 对话框的标题。
            text (str): 对话框中显示的主要文本内容。
            buttons (str, optional): 对话框按钮的 AppleScript 格式字符串，例如 '"OK","Cancel"'。
                                     默认为 '"OK"'。
            button_cancel (bool, optional): 是否包含取消按钮。如果为 True，则在提供的按钮前添加 "cancel"。
                                            默认为 True。

        Returns:
            str | None: 用户点击的按钮文本。如果发生错误，则返回 None。
        """
        if button_cancel:
            script = f'''
            display dialog "{text}" with title "{title}" buttons {{"cancel",{buttons}}} \
                default button "{buttons.split(',')[0][1:-1]}"
            '''

        else:
            script = f'''
            display dialog "{text}" with title "{title}" buttons {{{buttons}}} \
                default button "{buttons.split(',')[0][1:-1]}"
            '''
        try:
            # 使用 shlex.quote 防止注入
            shlex.quote(script)
            result = subprocess.run(['osascript', '-e', script],
                                    check=True, capture_output=True, text=True)
            # print(result.stdout)
            return result.stdout[16:-1]
        except subprocess.CalledProcessError as e:
            print(f"Error displaying dialog: {e}")
        except FileNotFoundError:
            print("Error: 'osascript' command not found. Ensure you are on macOS.")

class ShortCut():

    @staticmethod
    def run_shortcut(shortcut_name: str, params: str = None) -> str:
        """
        运行 macOS 快捷指令。

        Args:
            shortcut_name (str): 要运行的快捷指令的名称。
            params (str, optional): 传递给快捷指令的输入参数。默认为 None。

        Returns:
            str: 快捷指令执行后的输出结果。
        """
        commend = f'run shortcut "{shortcut_name}"' if params is None else f'run shortcut "{shortcut_name}" with input "{params}"'
        script = f'''tell application "Shortcuts"
            {commend}
        end tell'''
        return run_applescript(script)

    @staticmethod
    def applescript() -> str:
        """
        执行一个包含 AppleScript 示例代码的脚本。

        此方法主要用于演示 AppleScript 的执行，不返回任何值。

        Returns:
            str: AppleScript 执行结果。
        """
        script_content = """

```applescript
**use** AppleScript version "2.4" -- Yosemite (10.10) or later

**use** _scripting additions_

  

-- 告诉 System Events 我们要和它交互

**tell** _application_ "System Events"

 **tell** _process_ "网易有道翻译"
  
  -- set frontmost to true
  
   **tell** _window_ "网易有道翻译"
   
    **tell** _scroll area_ 1 **of** _group_ 1 **of** _group_ 1 -- 滚动区 组 组
     
     **tell** _UI element_ 1 -- 组 HTML 内容
      
      entire contents -- 获取所有 UI 元素
      
      -- static text "hierarchy"
     
     **set** value **of** _group_ 7 **to** "aaa"
    
    **end** **tell**
   
   **end** **tell**
  
  **end** **tell**
 
 **end** **tell**

**end** **tell**



  

-- 告诉 System Events 我们要和它交互

tell application "System Events"

 tell process "网易有道翻译"
 
  entire contents -- 获取所有UI
 
 end tell

end tell

-- static text "hierarchy" of group 7 of UI element 1 of scroll area 1 of group 1 of group 1 of window "网易有道翻译" of application process "网易有道翻译" of application "System Events",
```

"""
        return run_applescript(script_content)

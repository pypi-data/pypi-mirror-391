
import sys
sys.path.insert(0, "./src")

from time import sleep
from tqdm import tqdm

from cobra_color import smart_print, ctext, fmt_dict, fmt_list, set_console_func
from cobra_color.draw import fmt_image, fmt_font, FontName


smart_print("This is a smart print message.")


d = {"a": 2, "b": [1, 2, 3, {"c": 4, "d": [5, 6, 7]}], "e": {"f": 8, "g": 9}}

# tqdm 示例
for i in tqdm(range(5), desc="Processing"):
    sleep(0.5)
    smart_print(f"Current step: {i}")
    
    fmt_dict(d, title="Sample Dict", display=True)
    
    fmt_image(
        "/data/tianzhen/my_projects/vanyarlearn/DRAFT/dec8c8639e61c08614e0e87a90f34221.jpg",
        mode="half-color",
        height=30,
        display=True
    )
    
    fmt_font(
        "Hello, cobra-color!",
        font=FontName.LLDISCO,
        trim_border=True,
        mode="half-gray",
        font_size=10,
        fore_rgb=(255, 120, 0),
        back_rgb=(0, 120, 0),
        display=True
    )
    
    




from rich.progress import Progress, BarColumn, TimeRemainingColumn, TextColumn
from rich.console import Console
from time import sleep

# 创建一个 Rich Console（可传给 smart_print）
console = Console()

set_console_func(console.print, markup=False, highlight=False, end="")


# 定义进度条样式
with Progress(
    TextColumn("[bold blue]{task.description}"),
    BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.0f}%",
    TimeRemainingColumn(),
    console=console,
) as progress:

    # 添加一个任务，总共 10 步
    task = progress.add_task("Processing", total=10)

    for i in range(10):
        sleep(0.3)  # 模拟耗时操作

        # 更新进度
        progress.update(task, advance=1)

        # 输出文本，不打乱进度条
        smart_print(ctext(f"Step {i+1} completed.", bg="lb", styles=["bold", "italic"]), end=" \n")
        
        
        fmt_dict(d, title="Sample Dict", display=True)
        
        # console.print(f"[green]Step {i+1}/10 done![/green]")
        
        smart_print(fmt_font(
            "Hello, cobra-color!",
            font=FontName.LLDISCO,
            trim_border=True,
            mode="half-gray",
            font_size=10,
            fore_rgb=(255, 120, 0),
            back_rgb=(0, 120, 0),
            display=False
        ))
        
        

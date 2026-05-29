import json

import flet as ft

STORAGE_KEY = "kklab.todo.tasks.v1"

COLORS = [
    ft.Colors.RED_100,
    ft.Colors.ORANGE_100,
    ft.Colors.YELLOW_100,
    ft.Colors.GREEN_100,
    ft.Colors.BLUE_100,
    ft.Colors.PURPLE_100,
    ft.Colors.PINK_100,
]


class Task(ft.Column):
    def __init__(self, task_name, task_delete, color, task_change, completed=False):
        super().__init__()
        self.completed = completed
        self.task_name = task_name
        self.task_delete = task_delete
        self.task_change = task_change
        self.color = color

    def build(self):
        self.display_task = ft.Checkbox(
            value=self.completed, on_change=self.status_changed,
        )
        self.task_label = ft.Text(value=self.task_name, size=24, color=ft.Colors.ON_SURFACE)
        self.edit_name = ft.TextField(expand=1, text_size=24)

        self.display_view = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    controls=[self.display_task, self.task_label],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.CREATE_OUTLINED,
                            tooltip="編集",
                            on_click=self.edit_clicked,
                            icon_color=ft.Colors.BLUE_400,
                        ),
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE,
                            tooltip="削除",
                            on_click=self.delete_clicked,
                            icon_color=ft.Colors.RED_400,
                        ),
                    ],
                ),
            ],
        )

        self.edit_view = ft.Row(
            visible=False,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.edit_name,
                ft.IconButton(
                    icon=ft.Icons.DONE_OUTLINE_OUTLINED,
                    icon_color=ft.Colors.GREEN,
                    tooltip="保存",
                    on_click=self.save_clicked,
                ),
            ],
        )

        self.controls = [
            ft.Container(
                content=ft.Column(controls=[self.display_view, self.edit_view]),
                bgcolor=self.color,
                border_radius=12,
                padding=ft.Padding(left=12, top=4, right=12, bottom=4),
            )
        ]

    def edit_clicked(self, e):
        self.edit_name.value = self.task_label.value
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()

    async def save_clicked(self, e):
        self.task_label.value = self.edit_name.value
        self.display_view.visible = True
        self.edit_view.visible = False
        self.update()
        await self.task_change()

    async def status_changed(self, e):
        self.completed = self.display_task.value
        await self.task_change()

    async def delete_clicked(self, e):
        await self.task_delete(self)

    def to_dict(self):
        name = getattr(self, "task_label", None)
        return {
            "name": name.value if name is not None else self.task_name,
            "completed": self.completed,
            "color": self.color,
        }


class TodoApp(ft.Column):
    def __init__(self, prefs):
        super().__init__()
        self.prefs = prefs

    def build(self):
        self.new_task = ft.TextField(
            key="new_task",
            hint_text="やることを入力してください",
            on_submit=self.add_clicked,
            expand=True,
            border_color=ft.Colors.PURPLE_300,
            focused_border_color=ft.Colors.PURPLE_600,
            text_size=24,
        )
        self.tasks = ft.Column(spacing=8)
        self._color_index = 0

        self.filter = ft.TabBar(
            scrollable=False,
            tabs=[
                ft.Tab(label="すべて"),
                ft.Tab(label="未完了"),
                ft.Tab(label="完了"),
            ],
            label_text_style=ft.TextStyle(size=20),
        )

        self.filter_tabs = ft.Tabs(
            length=3,
            selected_index=0,
            on_change=lambda e: self.update(),
            content=self.filter,
        )

        self.items_left = ft.Text("残り0件", size=20, color=ft.Colors.BLUE_GREY_600)

        self.width = 800
        self.controls = [
            ft.Container(
                content=ft.Row(
                    [ft.Text(value="🌈 やること", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM)],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                bgcolor=ft.Colors.PURPLE_100,
                border_radius=16,
                padding=12,
            ),
            ft.Row(
                controls=[
                    self.new_task,
                    ft.FloatingActionButton(
                        key="add_task",
                        icon=ft.Icons.ADD,
                        on_click=self.add_clicked,
                        bgcolor=ft.Colors.ORANGE_300,
                    ),
                ],
            ),
            ft.Column(
                spacing=25,
                controls=[
                    self.filter_tabs,
                    self.tasks,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            self.items_left,
                            ft.OutlinedButton(
                                content="完了済みを削除",
                                on_click=self.clear_clicked,
                                style=ft.ButtonStyle(color=ft.Colors.RED_400),
                            ),
                        ],
                    ),
                ],
            ),
        ]

    def did_mount(self):
        # build() 完了後・ページ接続後に保存済みデータを非同期で読み込む。
        self.page.run_task(self.load_tasks)

    async def add_clicked(self, e):
        if self.new_task.value:
            color = COLORS[self._color_index % len(COLORS)]
            self._color_index += 1
            task = Task(self.new_task.value, self.task_delete, color, self.save_tasks)
            self.tasks.controls.append(task)
            self.new_task.value = ""
            await self.new_task.focus()
            self.update()
            await self.save_tasks()

    async def task_delete(self, task):
        self.tasks.controls.remove(task)
        self.update()
        await self.save_tasks()

    async def clear_clicked(self, e):
        self.tasks.controls[:] = [
            task for task in self.tasks.controls if not task.completed
        ]
        self.update()
        await self.save_tasks()

    async def save_tasks(self):
        if self.prefs is None:
            return
        data = [task.to_dict() for task in self.tasks.controls]
        await self.prefs.set(STORAGE_KEY, json.dumps(data, ensure_ascii=False))

    async def load_tasks(self):
        if self.prefs is None:
            return
        raw = await self.prefs.get(STORAGE_KEY)
        if not raw:
            return
        try:
            data = json.loads(raw)
        except (ValueError, TypeError):
            return
        for item in data:
            task = Task(
                item.get("name", ""),
                self.task_delete,
                item.get("color", COLORS[0]),
                self.save_tasks,
                completed=item.get("completed", False),
            )
            self.tasks.controls.append(task)
        self._color_index = len(self.tasks.controls)
        self.update()

    def before_update(self):
        status = self.filter.tabs[self.filter_tabs.selected_index].label
        count = 0
        for task in self.tasks.controls:
            task.visible = (
                status == "すべて"
                or (status == "未完了" and not task.completed)
                or (status == "完了" and task.completed)
            )
            if not task.completed:
                count += 1
        self.items_left.value = f"残り{count}件"


async def main(page: ft.Page):
    page.title = "やることリスト"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.window.width = 900
    page.window.height = 700
    page.bgcolor = ft.Colors.GREY_50
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(primary=ft.Colors.PURPLE_400),
        text_theme=ft.TextTheme(
            body_medium=ft.TextStyle(size=24),
            label_large=ft.TextStyle(size=24),
        ),
    )
    # SharedPreferences はブラウザの localStorage に永続化される。
    # インスタンス化時に page へ自動登録されるため参照を保持しておく。
    prefs = ft.SharedPreferences()
    page.add(ft.SafeArea(content=TodoApp(prefs)))


if __name__ == "__main__":
    ft.run(main, view=ft.AppView.WEB_BROWSER, port=8080)

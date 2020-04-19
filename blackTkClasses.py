import tkinter as tk

import functions as f


class MyButtonStyle:
    def __init__(self, root, label, cmd, name=None):
        self.text = tk.StringVar()
        self.text.set(label)
        self.btn = tk.Button(root, textvariable=self.text, command=cmd, name=name)
        self.btn.config(font=("arial", 10, ""), fg="white", bg="#101010", activebackground="#404040", bd=3)


class MyCheckButtonStyle:
    def __init__(self, root):
        self.value = tk.BooleanVar()
        self.value.set(tk.FALSE)
        self.btn = tk.Checkbutton(root, variable=self.value, onvalue=tk.TRUE, offvalue=tk.FALSE)
        self.btn.config(bg="#101010", activebackground="#101010")


class MyOptMenuStyle:
    def __init__(self, root, label, options: list):
        self.text = tk.StringVar()
        self.text.set(label)
        self.btn = tk.OptionMenu(root, self.text, "")
        self.btn.config(anchor=tk.W, font=("arial", 10, ""), fg="white", bg="#101010", activebackground="#404040")
        self.menu = self.btn["menu"]
        self.update(options)
        self.menu.config(font=("arial", 10, ""), fg="white", bg="#101010", activebackground="#404040")

    def _cmd_new(self, cmd, value):
        self.text.set(value)
        cmd(int(value[6:]))

    def update(self, options, cmd=None):
        self.menu.delete(0, tk.END)
        if len(options) > 0:
            for opt in options:
                if cmd:
                    self.menu.add_command(label=opt, command=lambda label2=opt: self._cmd_new(cmd, label2))
                else:
                    self.menu.add_command(label=opt, command=lambda label2=opt: self.text.set(label2))
        self.menu.update_idletasks()


class MyListboxStyle:
    def __init__(self, root, items: list):
        self.box = tk.Listbox(root)
        self.items_box = tk.StringVar(value=items)
        if len(items) > 0:
            length = len(items[-1])
            vlength = len(items) if len(items) < 35 else 35
        else:
            length = 5
            vlength = 5
        self.box.config(activestyle=tk.NONE, listvariable=self.items_box, width=length + 2,
                        height=vlength + 1, selectmode=tk.MULTIPLE, font=("arial", 10, ""), fg="white",
                        bg="#101010", borderwidth=5)
        self.menu = MyMenuStyle(self.box)
        self.menu.menu.add_command(label="Copy selected",
                                   command=lambda: f.copy_to_clipboard(self.box, self.box.curselection()))
        self.menu.menu.add_command(label="Select all",
                                   command=lambda: self.box.selection_set(0, tk.END))
        self.menu.menu.add_command(label="Deselect all",
                                   command=lambda: self.box.selection_clear(0, tk.END))

        def rc_event2(event):
            self.menu.menu.post(event.x_root, event.y_root)

        self.box.bind("<Button-3>", rc_event2)


class MyLabelStyle:
    def __init__(self, root, label):
        self.text = tk.StringVar()
        self.text.set(label)
        self.frame = tk.Label(root, textvariable=self.text)
        self.frame.config(font=("arial", 10, ""), fg="white", bg="#101010")


class MyEntryStyle:
    def __init__(self, root, label):
        self.text = tk.StringVar()
        self.text.set(label)
        self.frame = tk.Entry(root, textvariable=self.text, state="readonly")
        self.frame.config(justify=tk.CENTER, font=("arial", 10, ""), borderwidth=2, bg="#f0f0f0",
                          readonlybackground="#f0f0f0")


class MyMenuStyle:
    def __init__(self, root):
        self.menu = tk.Menu(root)
        self.menu.config(tearoff=0, font=("arial", 10, ""), fg="white", bg="#101010")

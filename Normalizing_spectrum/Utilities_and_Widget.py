import tkinter as tk
from Normalizing_spectrum.Work_program import init_region_header
from tkinter.filedialog import askopenfilename, asksaveasfilename
import numpy as np
from astropy.utils.data import get_pkg_data_filename
from astropy.io import fits
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

global list_coef, line, canvas, ax


def update_plotting():
    list_coefficient = list_coef.get()
    t = np.arange(-10.0, 10.0, .01)
    ax.set_ylim(min(list_coefficient[0] + list_coefficient[1] * t + list_coefficient[2] * t ** 2.0 + list_coefficient[
                    3] * t ** 3.0),
                max(list_coefficient[0] + list_coefficient[1] * t + list_coefficient[2] * t ** 2.0 + list_coefficient[
                    3] * t ** 3.0))
    line.set_data(t, list_coefficient[0] + list_coefficient[1] * t + list_coefficient[2] * t ** 2.0 + list_coefficient[
        3] * t ** 3.0)
    canvas.draw()


class Setting_Parameter(tk.Frame):
    """Класс с ползунком и настраиваемым шагом"""

    def __init__(self, parent, init_value, command=None):
        self.list_step = [0.0001, 0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0]
        self.i_step = 4

        tk.Frame.__init__(self, parent)

        self.update_plot = command

        self.lbl_value = tk.Label(self, text=str(init_value))
        self.lbl_step = tk.Label(self, text=str(self.list_step[self.i_step]))

        self.btn_decrease_value = tk.Button(self, text='-', command=self.decrease_value)
        self.btn_increase_value = tk.Button(self, text='+', command=self.increase_value)
        self.btn_increase_step = tk.Button(self, text='>>', command=self.increase_step)
        self.btn_decrease_step = tk.Button(self, text='<<', command=self.decrease_step)

        self.btn_decrease_value.grid(row=0, column=0, sticky="nsew")
        self.btn_increase_value.grid(row=0, column=2, sticky="nsew")
        self.btn_increase_step.grid(row=1, column=2, sticky="nsew")
        self.btn_decrease_step.grid(row=1, column=0, sticky="nsew")

        self.lbl_value.grid(row=0, column=1)
        self.lbl_step.grid(row=1, column=1)

    def increase_value(self):
        value = float(self.lbl_value["text"])
        self.lbl_value["text"] = f"{round(value + self.list_step[self.i_step], 4)}"
        self.update_plot()

    def decrease_value(self):
        value = float(self.lbl_value["text"])
        self.lbl_value["text"] = f"{round(value - self.list_step[self.i_step], 4)}"
        self.update_plot()

    def increase_step(self):
        self.i_step += 1
        if self.i_step > len(self.list_step):
            self.i_step = 0
        self.lbl_step["text"] = f"{round(self.list_step[self.i_step], 4)}"

    def decrease_step(self):
        self.i_step -= 1
        if self.i_step > len(self.list_step):
            self.i_step = 0
        self.lbl_step["text"] = f"{round(self.list_step[self.i_step], 4)}"

    def get(self):
        return float(self.lbl_value["text"])


class Setting_Parameters(tk.Frame):
    """Класс со списком виджетов, в которых настраивается шаг"""

    def __init__(self, parent=None, list_values=None, list_labels=None, command=None):
        if parent is None:
            print("Error, do not have argument parent")
            return
        if list_labels is None:
            list_labels = []
            print("Error, do not have argument list_labels")
            return
        if list_values is None:
            list_values = []
            print("Error, do not have argument list_values")
            return
        else:
            num_values = len(list_values)

        tk.Frame.__init__(self, parent)

        self.btn_values = list(range(num_values))

        for i in range(num_values):
            self.lbl_coefficient = tk.Label(parent, text=list_labels[i])
            self.lbl_coefficient.pack(padx=5)
            self.btn_values[i] = Setting_Parameter(parent, list_values[i], command=command)
            self.btn_values[i].pack(padx=5)

    def get(self):
        return np.array([self.btn_values[i].get() for i in range(len(self.btn_values))])


def main():
    global list_coef, line, canvas, ax

    root = tk.Tk()

    window_param = tk.Frame(root)

    fig = Figure(figsize=(5, 4), dpi=100)
    t = np.arange(-10.0, 10.0, .01)
    ax = fig.add_subplot()
    line, = ax.plot(t, 1.0 + t + t ** 2 + t ** 3)
    ax.set_ylim(min(1.0 + t + t ** 2 + t ** 3), max(1.0 + t + t ** 2 + t ** 3))
    ax.set_xlabel("time [s]")
    ax.set_ylabel("f(t)")

    canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
    canvas.draw()

    list_coef = Setting_Parameters(window_param, [1.0, 1.0, 1.0, 1.0], ['c_1', 'c_2', 'c_3', 'c_4'], update_plotting)

    window_param.grid(row=0, column=0)
    canvas.get_tk_widget().grid(row=0, column=0)
    list_coef.pack()
    root.mainloop()


if __name__ == '__main__':
    main()

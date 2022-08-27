import tkinter as tk
import tkinter.messagebox as mb
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename

import numpy as np

from Normalizing_spectrum.Work_program import init_region_header, approximation_of_the_continuum, clear_frame
# from Normalizing_spectrum.Utilities_and_Widget import slider_setting
from astropy.utils.data import get_pkg_data_filename
from astropy.io import fits
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from astropy.modeling import models

global init_hdu, hdu_current
global init_filepath, set_type_model, combo_list_models, model_parameters, combo_list_power_model
global spectrum_continuum, fixed_continuum

standarts_parameters = (2, 5)


def save_as_file():
    """Сохраняем текущий файл как новый файл."""

    out_filepath = asksaveasfilename(
        defaultextension=".fits",
        filetypes=[("Fits file", "*.fits"), ("All files", "*.*")],
    )
    if not out_filepath:
        return

    hdu_out = hdu_current

    hdu_out.writeto(out_filepath, overwrite=True)


def save_file():
    """Сохраняем текущий файл в старый файл."""

    if not init_filepath:
        return

    hdu_out = hdu_current

    hdu_out.writeto(init_filepath, overwrite=True)


def open_file():
    """Открывает файл для редактирования"""
    global init_hdu, hdu_current
    global init_filepath

    init_filepath = askopenfilename(
        filetypes=[("FITS file", "*.fits"), ("All Files", "*.*")]
    )
    if not init_filepath:
        return

    clear_frame(spectrum_work_place)

    image_file = get_pkg_data_filename(init_filepath)
    init_hdu = fits.open(image_file, ignore_missing_simple=True)[0]
    x = init_region_header(init_hdu.header)

    print(np.shape(init_hdu.data))

    if len(np.shape(init_hdu.data)) == 3:
        y = init_hdu.data[0, 0, :]
    else:
        y = init_hdu.data

    fig = Figure(figsize=(10, 6), dpi=100)
    ax = fig.add_subplot(111)
    ax.plot(x, y)
    ax.set_xlabel(r'$\lambda$, Å')

    try:
        model_parameters
    except NameError:
        pass
    else:
        spectrum_continuum_tr, fixed_continuum = approximation_of_the_continuum(init_hdu, model_parameters)
        ax.plot(x, spectrum_continuum_tr, color='red')

    canvas = FigureCanvasTkAgg(fig, spectrum_work_place)
    canvas.draw()

    toolbar = NavigationToolbar2Tk(canvas, spectrum_work_place, pack_toolbar=False)
    toolbar.update()
    canvas.get_tk_widget().pack(fill=tk.BOTH)
    toolbar.pack(side=tk.BOTTOM, fill=tk.BOTH)

    main_window.title(f"Normalize spectrum - {init_filepath}")
    main_window.after(200, None)

    hdu_current = init_hdu


def onExit():
    """Закрытие визуального интерфейса"""
    main_window.quit()


def set_model():
    global set_type_model, combo_list_models

    clear_frame(setting_work_place)

    set_type_model = tk.Frame(setting_work_place)
    set_type_model['borderwidth'] = 2
    set_type_model['relief'] = 'sunken'

    label_models_norm = tk.Label(set_type_model, text="Модель")
    combo_list_models = ttk.Combobox(set_type_model, values=("Полиномы Чебышева", "Полиномы Лежандра", "Полиномы"))

    label_models_norm.grid(row=0, column=0, sticky='nw', padx=5, pady=5)
    combo_list_models.grid(column=0, row=1, sticky="nw", padx=5, pady=5)

    set_type_model.grid(column=0, row=0)

    combo_list_models.bind("<<ComboboxSelected>>", set_param_model)


def set_param_model(event):
    global model_parameters, combo_list_power_model
    label_parameters_model = tk.Label(set_type_model, text='Степень полинома')

    if combo_list_models.current() > 1:
        combo_list_power_model = ttk.Combobox(set_type_model, values=("3", "4", "5", "6", "7", "8", "9", "10"))
    else:
        combo_list_power_model = ttk.Combobox(set_type_model, values=("3", "4", "5"))

    label_parameters_model.grid(row=2, column=0, sticky='nw', padx=5, pady=5)
    combo_list_power_model.grid(row=3, column=0, sticky="nw", padx=5, pady=5)

    combo_list_power_model.bind("<<ComboboxSelected>>", fit_continuum_spectrum)


def more_setting_fitting_model():
    """Функция строющая продвинутую меню для фитирования континуума"""

    frame_update_setting = tk.Frame(setting_work_place)

    clear_frame(frame_update_setting)

    canvas = tk.Canvas(frame_update_setting)
    scrollbar = ttk.Scrollbar(frame_update_setting, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set)

    fit_param = fixed_continuum.parameters

    for i in range(len(fit_param)):
        lbl_coef = tk.Label(scrollable_frame, text='c_' + str(i))
        lbl_coef.pack(pady=5, padx=5)
        # btn_update_coef.pack(padx=5)

    frame_update_setting.grid(row=2, column=0, sticky='nw')
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")


def cancel_normalization():
    """Возращения спектра к первоначальному"""

    clear_frame(spectrum_work_place)

    hdu_current.data *= spectrum_continuum

    x = init_region_header(hdu_current.header)
    y = hdu_current.data

    fig = Figure(figsize=(8, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.plot(x, y)
    ax.plot(x, spectrum_continuum, color='red')
    ax.set_xlabel(r'$\lambda$, Å')

    canvas = FigureCanvasTkAgg(fig, spectrum_work_place)
    canvas.draw()

    toolbar = NavigationToolbar2Tk(canvas, spectrum_work_place, pack_toolbar=False)
    toolbar.update()

    canvas.get_tk_widget().pack(fill=tk.BOTH)
    toolbar.pack(side=tk.BOTTOM, fill=tk.BOTH)

    main_window.after(200, None)


def normalization_spectrum():
    """Нормализация данного спектра"""

    clear_frame(spectrum_work_place)

    hdu = hdu_current

    x = init_region_header(hdu.header)
    y = hdu.data / spectrum_continuum

    fig = Figure(figsize=(8, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.plot(x, y)
    ax.set_xlabel(r'$\lambda$, Å')

    canvas = FigureCanvasTkAgg(fig, spectrum_work_place)
    canvas.draw()

    toolbar = NavigationToolbar2Tk(canvas, spectrum_work_place, pack_toolbar=False)
    toolbar.update()

    canvas.get_tk_widget().pack(fill=tk.BOTH)
    toolbar.pack(side=tk.BOTTOM, fill=tk.BOTH)

    main_window.after(200, None)

    hdu_current.data = y

    btn_cancel_normalization = tk.Button(setting_work_place, text='Отменить нормализацию', command=cancel_normalization)
    btn_cancel_normalization.grid(row=4, column=0, sticky="ew", padx=5)


def buttons_setting_coef_model():
    """Строит дополнительные кнопки для нормализации и уточнения фитирования континуума"""

    btn_more_characteristic = tk.Button(setting_work_place, text='Дополнительные параметры',
                                        command=more_setting_fitting_model)
    btn_normalization = tk.Button(setting_work_place, text='Нормализовать спектр', command=normalization_spectrum)

    btn_more_characteristic.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
    btn_normalization.grid(row=3, column=0, sticky="ew", padx=5)


def fit_continuum_spectrum(event):
    """Аппроксимация континуума"""

    global spectrum_continuum, fixed_continuum

    clear_frame(spectrum_work_place)

    model_parameters = (int(combo_list_models.current()), int(combo_list_power_model.get()))

    try:
        hdu_current
    except NameError:
        mb.showwarning("Предупреждение", "Отсутствует спектр для обработки")
        open_file()
        clear_frame(spectrum_work_place)

    model_fitting = None

    if model_parameters[0] == 0:
        model_fitting = models.Chebyshev1D(model_parameters[1])
    if model_parameters[0] == 1:
        model_fitting = models.Legendre1D(model_parameters[1])
    if model_parameters[0] == 2:
        model_fitting = models.Polynomial1D(model_parameters[1])

    spectrum_continuum, fixed_continuum = approximation_of_the_continuum(hdu_current, model_fitting)

    x = init_region_header(hdu_current.header)
    y = hdu_current.data

    fig = Figure(figsize=(8, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.plot(x, y)
    ax.plot(x, spectrum_continuum, color='red')
    ax.set_xlabel(r'$\lambda$, Å')

    canvas = FigureCanvasTkAgg(fig, spectrum_work_place)
    canvas.draw()

    toolbar = NavigationToolbar2Tk(canvas, spectrum_work_place, pack_toolbar=False)
    toolbar.update()

    canvas.get_tk_widget().pack(fill=tk.BOTH)
    toolbar.pack(side=tk.BOTTOM, fill=tk.BOTH)

    main_window.after(200, None)

    buttons_setting_coef_model()


main_window = tk.Tk()
main_window.title("Spectrum_analyzing_v0.001")

main_window.rowconfigure(0, minsize=600, weight=1)
main_window.columnconfigure(0, minsize=1000, weight=1)

menubar = tk.Menu(main_window)
main_window.config(menu=menubar)

fileMenu = tk.Menu(menubar)
submenu = tk.Menu(fileMenu)

submenu.add_command(label='Сохранить файл')
submenu.add_command(label='Сохранить файл как ...')

fileMenu.add_command(label='Открыть ...', underline=0, command=open_file)

fileMenu.add_cascade(label='Сохранить', underline=0, menu=submenu)

fileMenu.add_command(label="Выход", underline=0, command=onExit)

fileMenu.add_separator()

menubar.add_cascade(label="Файл", underline=0, menu=fileMenu)

normMenu = tk.Menu(menubar)

normMenu.add_command(label='Фитировать континуум', command=set_model, underline=0)

normMenu.add_separator()

menubar.add_cascade(label="Обработка спектра", underline=0, menu=normMenu)

main_frame = tk.Frame(main_window)
main_frame['borderwidth'] = 2
main_frame['relief'] = 'sunken'
main_frame.rowconfigure(0, minsize=400, weight=1)
main_frame.columnconfigure(0, minsize=250, weight=0)
main_frame.columnconfigure(1, minsize=800, weight=1)

spectrum_work_place = tk.Frame(main_frame)
spectrum_work_place['borderwidth'] = 2
spectrum_work_place['relief'] = 'sunken'

setting_work_place = tk.Frame(main_frame)
setting_work_place['borderwidth'] = 2
setting_work_place['relief'] = 'sunken'

main_frame.grid(row=0, column=0, sticky="nsew")

setting_work_place.grid(row=0, column=0, sticky="nsew")
spectrum_work_place.grid(row=0, column=1, sticky="nsew")

main_window.mainloop()

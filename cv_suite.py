import cv2
import os
import errno
import numpy as np
from matplotlib import pyplot as plt
from PIL import ImageTk, Image
from tkinter import filedialog, simpledialog, Tk, Label, Button, messagebox, N, S, W, E


class CvSuite:

    def __init__(self):
        self.max_image_size = None
        self.desktop_location = None
        self.master = None
        self.label = None
        self.select_image_button = None
        self.detect_edges_button = None
        self.original_image_panel = None
        self.processed_image_panel = None
        self.original_image = None
        self.original_image_file = None
        self.processed_image = None
        self.image_path = None
        self.image_format = None
        self.setup_global_variables()
        self.setup_gui()
        self.master.mainloop()

    def setup_global_variables(self):
        self.max_image_size=500
        self.desktop_location=os.path.join(os.environ["HOME"], "Desktop")

    def setup_gui(self):
        self.master = Tk()
        self.master.title("Nick's Image Suite")
        self.setup_labels()
        self.setup_buttons()
        self.setup_panels()

    def setup_labels(self):
        self.label = Label(self.master, text="Nick's Image Suite")
        self.label.grid(row=0, column=2, sticky=W)

    def setup_buttons(self):
        self.select_image_button = Button(self.master, text="Select an Image", command=self.select_image)
        self.select_image_button.grid(row=2, column=0, sticky=W, columnspan=1, padx=10, pady=10)
        self.detect_edges_button = Button(self.master, text="Detect Edges", command=self.detect_edges)
        self.detect_edges_button.grid(row=2, column=4, sticky=W, columnspan=1, padx=10, pady=10)

    def setup_panels(self):
        self.original_image_panel = Label(text="Original Image")
        self.original_image_panel.image = self.original_image
        self.original_image_panel.grid(row=1, column=1, sticky=N + W, padx="10", pady="10")

        self.processed_image_panel = Label(text="Processed Image")
        self.processed_image_panel.image = self.processed_image
        self.processed_image_panel.grid(row=1, column=3, sticky=N + E, padx="10", pady="10")

    def update_panels(self):
        self.original_image_panel.configure(image=self.original_image)
        self.processed_image_panel.configure(image=self.processed_image)
        self.original_image_panel.image = self.original_image
        self.processed_image_panel.image = self.processed_image

    def detect_edges(self):
        if self.original_image is not None:
            original_image_in_grayscale = cv2.cvtColor(self.original_image_file, cv2.COLOR_BGR2GRAY)
            edge_detected_image = cv2.Canny(original_image_in_grayscale, 50, 100)
            edge_detected_image = Image.fromarray(edge_detected_image)
            self.processed_image = ImageTk.PhotoImage(edge_detected_image)
            self.resize_images()
            self.update_panels()
        else:
            self.select_image()

    def select_image(self):
        self.prompt_user_for_image_file_name()
        if len(self.master.filename):
            self.original_image_file = cv2.imread(self.master.filename)
            self.original_image = self.original_image_file
            self.processed_image = self.original_image_file
            self.resize_images()
            self.transform_original_image_to_image_tk_photo_image()
            self.processed_image = self.original_image
            self.draw_image_panels()

    def draw_image_panels(self):
        if self.processed_image_panel is None:
            self.setup_panels()
            self.draw_image_panels()
        else:
            self.update_panels()

    def prompt_user_for_image_file_name(self):
        self.master.filename = filedialog.askopenfilename(initialdir="C:/", title="Select Image", filetypes=
        ((".jpeg Files", "*.jpeg"), (".jpg Files", "*.jpg"), ("png Files", "*.png")))
        self.split_filename_between_path_and_format()

    def split_filename_between_path_and_format(self):
        self.image_path, self.image_format = os.path.splitext(self.master.filename)

    def resize_images(self):
        old_dimensions = self.original_image_file.shape[:2]
        scale_factor = float(self.max_image_size) / float(max(old_dimensions))

        new_image_dimensions = tuple([int(dimension * scale_factor) for dimension in old_dimensions])
        self.original_image = cv2.resize(self.original_image_file, (new_image_dimensions[1], new_image_dimensions[0]))

    def transform_original_image_to_image_tk_photo_image(self):
        self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        self.original_image = Image.fromarray(self.original_image)
        self.original_image = ImageTk.PhotoImage(self.original_image)


if __name__ == '__main__':
    CvSuite().master.mainloop()

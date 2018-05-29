# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 11:29:37 2018

@author: NickA
"""
import os
import errno
import numpy as np
import opencv as cv2
import tkinter
from matplotlib import pyplot as plt
from PIL import ImageTk, Image
from tkinter import filedialog, simpledialog, Tk, Label, Button, messagebox, N, S, W, E


class NIHCVGUI:
    img = None
    max_size = 500
    img_path = None
    img_format = None
    desktop = os.path.join(os.environ["HOMEPATH"], "Desktop")

    def __init__(self, master):
        self.master = master
        master.title("NIHCV Project")

        self.label = Label(master, text="NIHCV")
        self.label.grid(row=0, column=2, sticky=W)

        # This button will allow a user to select an image
        self.selectImage_button = Button(master, text="Select an Image", command=self.selectImage)
        self.selectImage_button.grid(row=2, column=0, sticky=W, columnspan=1, padx=10, pady=10)

        # This button will allow a user to gray an image
        self.detectEdges_button = Button(master, text="Detect Edges", command=self.detectEdges)
        self.detectEdges_button.grid(row=2, column=4, sticky=W, columnspan=1, padx=10, pady=10)

        # This button will allow user to split loaded image into NXN square tiles
        self.splitIntoN_button = Button(master, text="Split Image!", command=self.splitIntoN)
        self.splitIntoN_button.grid(row=2, column=2, sticky=W, columnspan=1, padx=10, pady=10)

    def resetImages(self):
        if self.img is not None:
            tempImg = self.processImage(self.img)
            self.updatePanelA(tempImg)
        else:
            self.selectImage()

    def selectImage(self):
        # Grab the global variables image1 and img

        # Prompt user to select an image of type .jpg, jpeg, or png
        root.filename = filedialog.askopenfilename(initialdir="C:/", title="Select Image", filetypes=(
        ("jpeg Files", "*.jpeg"), ("jpg Files", "*.jpg"), ("png Files", "*.png")))

        self.img_path, self.img_format = os.path.splitext(root.filename)
        print(self.img_format)

        # Make sure you select a file
        if len(root.filename) > 0:
            # Load image from the disk and put it in img
            self.img = cv2.imread(root.filename)
            # automatically resize an image to fit onto the canvas
            self.resizeImage(self.max_size)

            tempImg = self.processImage(self.img)  # returns a tkImage copy of self.img

            self.updatePanelA(tempImg)

    def resizeImage(self, desiredSize):
        # unprocessed image size is stored (height,width,# channels)

        old_size = self.img.shape[:2]
        print("Old dims of image are: " + str(old_size[0]) + "x" + str(old_size[1]))
        print()
        ratio = float(desiredSize) / float(max(old_size))

        # calculate the new dimensions

        new_size = tuple([int(x * ratio) for x in old_size])
        # news_size = (height)
        self.img = cv2.resize(self.img, (new_size[1], new_size[0]))  # back in (width, height) order

        tempImg = self.processImage(self.img)
        self.updatePanelA(tempImg)

    def splitIntoN(self):
        self.resetImages()

        if self.img is not None:  # Make sure theres an image to use
            # Let user define integer to split the image into square panels
            n = None
            # Width of image
            width = self.img.shape[1]
            print("Initial Width: " + str(width))
            # Height of image
            height = self.img.shape[0]
            print("Initial Height: " + str(height))

            dim = max(width, height)

            while True:
                try:
                    n = int(tkinter.simpledialog.askstring('Image Split',
                                                           'What do you want the dimensions of the square to be?\nYou can pick any number less than ' + str(
                                                               dim)))
                    if n is not None:
                        if n >= dim:
                            messagebox.showinfo("Error", "Must be less than " + str(dim))
                            n = 1
                        elif n <= 1:
                            messagebox.showinfo("Error", "Must be greater than 1")
                            n = 1
                    else:
                        n = 1
                except ValueError:
                    messagebox.showinfo("Error", "Must be an valid integer")
                    n = 1
                except TypeError:
                    n = 1
                    break
                else:
                    break

            if n != 1:  # 1 is code for failed attempt
                print("Attempting to break into " + str(n) + "x" + str(n) + " squares!")
                # We will now pad the image in order to make it a square so that it
                # satisfies the following, width = 0(mod n), height = 0(mod n)

                if n < dim:
                    remW = width % n
                    remH = height % n

                    addW = 0
                    addH = 0

                    if remW != 0:
                        addW = n - remW

                    if remH != 0:
                        addH = n - remH

                    # split the pixels you're going to add into even pairs
                    top, bottom = addH // 2, addH - (addH // 2)
                    left, right = addW // 2, addW - (addW // 2)

                    # This variable determines the border color
                    color = [0, 0, 0]

                    tempImg = cv2.copyMakeBorder(self.img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)

                    print("New dimensions are: " + str(tempImg.shape[0]) + "x" + str(tempImg.shape[1]))
                    print()
                    # Display the image with a new border!
                    self.updatePanelA(self.processImage(tempImg))

                    print()

                    foldname = self.img_path + " " + str(n) + "x" + str(n) + "-split" + " Folder" + "/"
                    print(foldname)
                    if not os.path.exists(os.path.dirname(foldname)):
                        try:
                            os.makedirs(os.path.dirname(foldname))
                            self.cropAndSave(tempImg, n, foldname)
                        except OSError as exc:  # Guard against race condition
                            print("failed to make folder")
                            if exc.errno != errno.EEXIST:
                                raise
                    else:
                        messagebox.showerror("Error",
                                             "You have already saved photos at the location \n" + foldname + "\n Please delete this directory and try again")
        else:
            self.selectImage()

    def cropAndSave(self, image, split, folder):
        width = image.shape[1]
        height = image.shape[0]

        # Save as .jpeg by default
        form = '.jpeg'

        # Change the format if!
        if self.img_format == '.jpeg':
            form = '.png'
        elif self.img_format == '.png':
            form = '.jpg'

        k = 0
        successful = True
        # Actually split the image and save each tile as a file type that
        # it was not before
        for r in range(0, height, split):  # row
            for c in range(0, width, split):  # column
                tempImg = image[r:r + split, c:c + split]
                try:
                    cv2.imwrite(folder + "IMG-%s%s" % (k, form), tempImg)
                except:
                    messagebox.showerror("Error", "Failed to save images.\n Please try again.")
                    sucessful = False
                    break
                k += 1

        if successful:
            messagebox.showinfo("Split Successful!",
                                "Your split images, each of their histograms,\n and their average RGB values are stored at: \n" + folder)
            # open text file to store avg RGB values
            textfile_name = folder + str(split) + "x" + str(split)

            rgb_file = None
            try:
                rgb_file = open(textfile_name + " Average RGB Values.txt", "w+")
            except:
                messagebox.showerror("Error", "File cannot be opened")
                pass

        # Calculate average RBG for that square and write it to .txt file
        # Draw a grid of where you cut the image and display it on panel A
        temp = image
        k = 0
        for r in range(0, height, split):
            for c in range(0, width, split):
                cropped = image[r:r + split, c:c + split]
                # average the RGB Values for cropped
                avg_red = cropped[:, :, 2].mean()
                avg_green = cropped[:, :, 1].mean()
                avg_blue = cropped[:, :, 0].mean()
                rgb_file.write(
                    "IMG-%s%s avg RGB: " % (k, form) + "[" + str(avg_red) + ", " + str(avg_green) + ", " + str(
                        avg_blue) + "]" + "\n")
                temp = cv2.rectangle(temp, (c, r), (c + split, r + split), (255, 255, 255), 1)

                # Compute the grayscale histogram for the tile!
                gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
                histr = cv2.calcHist([gray], [0], None, [256], [0, 256])
                try:
                    hist_file = open(textfile_name + "IMG-%s Histogram.txt" % k, "w+")
                    hist_file.write("IMG-%s%s Histogram:" % (k, form) + str(histr))
                    hist_file.close()
                except:
                    pass

                k += 1
        rgb_file.close()
        self.updatePanelA(self.processImage(image))

    def findHist(self, image):
        disp = plt.hist(image.ravel(), 256, [0, 256])

        # This method will return a processed copy of the original image
        # processed means that the copy is a tk photoImage

    def processImage(self, image):
        # Swap the image channels from BGR to RGB to display with PIL
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Convert the image to PIL format
        image = Image.fromarray(image)

        # Convert PIL format image to ImageTK format
        image = ImageTk.PhotoImage(image)

        return image

    def detectEdges(self):
        self.resetImages()

        if self.img is not None:
            gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
            edged = cv2.Canny(gray, 50, 100)
            edged = Image.fromarray(edged)
            edged = ImageTk.PhotoImage(edged)

            self.updatePanels(self.processImage(self.img), edged)
        else:
            self.selectImage()

    # This method updates left panel and clears right panel
    def updatePanelA(self, panelAimg):
        global panelA, panelB

        # Initialize the panel
        if panelA is None:
            # panelA is the main image
            panelA = Label(image=panelAimg)
            panelA.image = panelAimg
            panelA.grid(row=1, column=1, sticky=N + W, padx="10", pady="10")
        # update the panel
        else:
            # panelA.forget()
            panelA.configure(image=panelAimg, text="Processed Image")
            panelA.image = panelAimg
            if panelB is not None:
                panelB.forget()

    def updatePanels(self, panelAimg, panelBimg):
        global panelA, panelB

        # initialize the panels if they aren't already
        if panelA is None or panelB is None:
            # panelA is the main image
            panelA = Label(image=panelAimg, text="Main Image")
            panelA.image = panelAimg
            panelA.grid(row=1, column=1, sticky=N + W, padx="10", pady="10")

            # panelB is our processed image
            panelB = Label(image=panelBimg, text="Processed Image")
            panelB.image = panelBimg
            panelB.grid(row=1, column=3, sticky=N + E, padx="10", pady="10")

        # or update the panels
        else:
            panelA.configure(image=panelAimg)
            panelB.configure(image=panelBimg)
            panelA.image = panelAimg
            panelB.image = panelBimg


# init the Window and panels
root = Tk()
panelA = None
panelB = None

# start the GUI
my_gui = NIHCVGUI(root)
root.mainloop()